import sys
import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QFileDialog,
    QProgressBar,
    QComboBox,
    QTextEdit,
    QMessageBox,
    QCheckBox,
    QSpinBox,
)

from securearchive.engine import (
    encrypt_path,
    decrypt_container,
    list_container,
    verify_container,
    change_password,
    SecureArchiveError,
    InvalidContainerError,
    WrongPasswordError,
)
from securearchive.i18n import tr


class SecureArchiveWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "de"

        self.setWindowTitle(tr(self.lang, "gui.title"))
        self.resize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        top_bar = QHBoxLayout()

        lang_label = QLabel("Language / Sprache:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItem(tr("de", "gui.lang.de"), userData="de")
        self.lang_combo.addItem(tr("en", "gui.lang.en"), userData="en")
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)

        self.github_btn = QPushButton()
        self.github_btn.clicked.connect(self.on_github_clicked)

        self.info_btn = QPushButton("?")
        self.info_btn.setFixedWidth(40)
        self.info_btn.clicked.connect(self.on_info_clicked)

        top_bar.addWidget(lang_label)
        top_bar.addWidget(self.lang_combo)
        top_bar.addStretch()
        top_bar.addWidget(self.github_btn)
        top_bar.addWidget(self.info_btn)

        main_layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 1)

        bottom_layout = QVBoxLayout()
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        bottom_layout.addWidget(self.progress)
        bottom_layout.addWidget(self.log, 1)
        main_layout.addLayout(bottom_layout)

        self._build_encrypt_tab()
        self._build_decrypt_tab()
        self._build_list_tab()
        self._build_verify_tab()
        self._build_passwd_tab()

        self._apply_texts()

        self.append_log(tr(self.lang, "gui.status.ready"))

    def append_log(self, text: str):
        self.log.append(text)

    def set_status_running(self):
        self.progress.setValue(10)
        self.append_log(tr(self.lang, "gui.status.running"))

    def set_status_done(self, msg_key: str | None = None):
        self.progress.setValue(100)
        if msg_key:
            self.append_log(tr(self.lang, msg_key))
        self.append_log(tr(self.lang, "gui.status.done"))

    def set_status_error(self, text: str):
        self.progress.setValue(0)
        self.append_log(tr(self.lang, "gui.status.error"))
        self.append_log(text)

    def show_error_box(self, message: str, title: str | None = None):
        if title is None:
            title = tr(self.lang, "common.error")
        QMessageBox.critical(self, title, message)

    def on_language_changed(self, index: int):
        lang = self.lang_combo.itemData(index)
        if lang not in ("de", "en"):
            lang = "en"
        self.lang = lang
        self._apply_texts()
        self.append_log(tr(self.lang, "common.language_set"))

    def _apply_texts(self):
        self.setWindowTitle(tr(self.lang, "gui.title"))

        self.tabs.setTabText(0, tr(self.lang, "gui.tab.encrypt"))
        self.tabs.setTabText(1, tr(self.lang, "gui.tab.decrypt"))
        self.tabs.setTabText(2, tr(self.lang, "gui.tab.list"))
        self.tabs.setTabText(3, tr(self.lang, "gui.tab.verify"))
        self.tabs.setTabText(4, tr(self.lang, "gui.tab.passwd"))

        self.github_btn.setText(tr(self.lang, "gui.button.github"))
        self.info_btn.setText(tr(self.lang, "gui.button.info"))

        self.enc_input_label.setText(tr(self.lang, "gui.encrypt.input_label"))
        self.enc_output_label.setText(tr(self.lang, "gui.encrypt.output_label"))
        self.enc_password_label.setText(tr(self.lang, "gui.encrypt.password_label"))
        self.enc_password_confirm_label.setText(tr(self.lang, "gui.encrypt.password_confirm_label"))
        self.enc_iterations_label.setText(tr(self.lang, "gui.encrypt.iterations_label"))
        self.enc_force_checkbox.setText(tr(self.lang, "gui.encrypt.force_label"))
        self.enc_browse_input_btn.setText(tr(self.lang, "gui.button.browse_file"))
        self.enc_browse_input_folder_btn.setText(tr(self.lang, "gui.button.browse_folder"))
        self.enc_browse_output_btn.setText(tr(self.lang, "gui.button.browse_container"))
        self.enc_button.setText(tr(self.lang, "gui.encrypt.button"))

        self.dec_container_label.setText(tr(self.lang, "gui.decrypt.container_label"))
        self.dec_output_dir_label.setText(tr(self.lang, "gui.decrypt.output_dir_label"))
        self.dec_password_label.setText(tr(self.lang, "gui.decrypt.password_label"))
        self.dec_browse_container_btn.setText(tr(self.lang, "gui.button.browse_container"))
        self.dec_browse_output_dir_btn.setText(tr(self.lang, "gui.button.browse_output_dir"))
        self.dec_button.setText(tr(self.lang, "gui.decrypt.button"))

        self.list_container_label.setText(tr(self.lang, "gui.list.container_label"))
        self.list_password_label.setText(tr(self.lang, "gui.list.password_label"))
        self.list_browse_container_btn.setText(tr(self.lang, "gui.button.browse_container"))
        self.list_button.setText(tr(self.lang, "gui.list.button"))

        self.ver_container_label.setText(tr(self.lang, "gui.verify.container_label"))
        self.ver_password_label.setText(tr(self.lang, "gui.verify.password_label"))
        self.ver_browse_container_btn.setText(tr(self.lang, "gui.button.browse_container"))
        self.ver_button.setText(tr(self.lang, "gui.verify.button"))

        self.pw_container_label.setText(tr(self.lang, "gui.passwd.container_label"))
        self.pw_current_label.setText(tr(self.lang, "gui.passwd.current_label"))
        self.pw_new_label.setText(tr(self.lang, "gui.passwd.new_label"))
        self.pw_new_confirm_label.setText(tr(self.lang, "gui.passwd.new_confirm_label"))
        self.pw_iterations_label.setText(tr(self.lang, "gui.passwd.iterations_label"))
        self.pw_browse_container_btn.setText(tr(self.lang, "gui.button.browse_container"))
        self.pw_button.setText(tr(self.lang, "gui.passwd.button"))

    def _build_encrypt_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        row_input = QHBoxLayout()
        self.enc_input_label = QLabel()
        self.enc_input_edit = QLineEdit()
        self.enc_browse_input_btn = QPushButton()
        self.enc_browse_input_btn.clicked.connect(self.on_enc_browse_file)
        self.enc_browse_input_folder_btn = QPushButton()
        self.enc_browse_input_folder_btn.clicked.connect(self.on_enc_browse_folder)

        row_input.addWidget(self.enc_input_label)
        row_input.addWidget(self.enc_input_edit, 1)
        row_input.addWidget(self.enc_browse_input_btn)
        row_input.addWidget(self.enc_browse_input_folder_btn)
        layout.addLayout(row_input)

        row_output = QHBoxLayout()
        self.enc_output_label = QLabel()
        self.enc_output_edit = QLineEdit()
        self.enc_browse_output_btn = QPushButton()
        self.enc_browse_output_btn.clicked.connect(self.on_enc_browse_output)

        row_output.addWidget(self.enc_output_label)
        row_output.addWidget(self.enc_output_edit, 1)
        row_output.addWidget(self.enc_browse_output_btn)
        layout.addLayout(row_output)

        row_pw = QHBoxLayout()
        self.enc_password_label = QLabel()
        self.enc_password_edit = QLineEdit()
        self.enc_password_edit.setEchoMode(QLineEdit.Password)
        row_pw.addWidget(self.enc_password_label)
        row_pw.addWidget(self.enc_password_edit, 1)
        layout.addLayout(row_pw)

        row_pw2 = QHBoxLayout()
        self.enc_password_confirm_label = QLabel()
        self.enc_password_confirm_edit = QLineEdit()
        self.enc_password_confirm_edit.setEchoMode(QLineEdit.Password)
        row_pw2.addWidget(self.enc_password_confirm_label)
        row_pw2.addWidget(self.enc_password_confirm_edit, 1)
        layout.addLayout(row_pw2)

        row_iter = QHBoxLayout()
        self.enc_iterations_label = QLabel()
        self.enc_iterations_spin = QSpinBox()
        self.enc_iterations_spin.setRange(10_000, 2_000_000)
        self.enc_iterations_spin.setSingleStep(10_000)
        self.enc_iterations_spin.setValue(300_000)
        self.enc_force_checkbox = QCheckBox()
        row_iter.addWidget(self.enc_iterations_label)
        row_iter.addWidget(self.enc_iterations_spin)
        row_iter.addSpacing(20)
        row_iter.addWidget(self.enc_force_checkbox)
        row_iter.addStretch()
        layout.addLayout(row_iter)

        row_btn = QHBoxLayout()
        row_btn.addStretch()
        self.enc_button = QPushButton()
        self.enc_button.clicked.connect(self.on_encrypt_clicked)
        row_btn.addWidget(self.enc_button)
        layout.addLayout(row_btn)

        layout.addStretch()
        self.tabs.addTab(tab, "Encrypt")

    def _build_decrypt_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        row_cont = QHBoxLayout()
        self.dec_container_label = QLabel()
        self.dec_container_edit = QLineEdit()
        self.dec_browse_container_btn = QPushButton()
        self.dec_browse_container_btn.clicked.connect(self.on_dec_browse_container)
        row_cont.addWidget(self.dec_container_label)
        row_cont.addWidget(self.dec_container_edit, 1)
        row_cont.addWidget(self.dec_browse_container_btn)
        layout.addLayout(row_cont)

        row_out = QHBoxLayout()
        self.dec_output_dir_label = QLabel()
        self.dec_output_dir_edit = QLineEdit()
        self.dec_browse_output_dir_btn = QPushButton()
        self.dec_browse_output_dir_btn.clicked.connect(self.on_dec_browse_output_dir)
        row_out.addWidget(self.dec_output_dir_label)
        row_out.addWidget(self.dec_output_dir_edit, 1)
        row_out.addWidget(self.dec_browse_output_dir_btn)
        layout.addLayout(row_out)

        row_pw = QHBoxLayout()
        self.dec_password_label = QLabel()
        self.dec_password_edit = QLineEdit()
        self.dec_password_edit.setEchoMode(QLineEdit.Password)
        row_pw.addWidget(self.dec_password_label)
        row_pw.addWidget(self.dec_password_edit, 1)
        layout.addLayout(row_pw)

        row_btn = QHBoxLayout()
        row_btn.addStretch()
        self.dec_button = QPushButton()
        self.dec_button.clicked.connect(self.on_decrypt_clicked)
        row_btn.addWidget(self.dec_button)
        layout.addLayout(row_btn)

        layout.addStretch()
        self.tabs.addTab(tab, "Decrypt")

    def _build_list_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        row_cont = QHBoxLayout()
        self.list_container_label = QLabel()
        self.list_container_edit = QLineEdit()
        self.list_browse_container_btn = QPushButton()
        self.list_browse_container_btn.clicked.connect(self.on_list_browse_container)
        row_cont.addWidget(self.list_container_label)
        row_cont.addWidget(self.list_container_edit, 1)
        row_cont.addWidget(self.list_browse_container_btn)
        layout.addLayout(row_cont)

        row_pw = QHBoxLayout()
        self.list_password_label = QLabel()
        self.list_password_edit = QLineEdit()
        self.list_password_edit.setEchoMode(QLineEdit.Password)
        row_pw.addWidget(self.list_password_label)
        row_pw.addWidget(self.list_password_edit, 1)
        layout.addLayout(row_pw)

        row_btn = QHBoxLayout()
        row_btn.addStretch()
        self.list_button = QPushButton()
        self.list_button.clicked.connect(self.on_list_clicked)
        row_btn.addWidget(self.list_button)
        layout.addLayout(row_btn)

        layout.addStretch()
        self.tabs.addTab(tab, "List")

    def _build_verify_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        row_cont = QHBoxLayout()
        self.ver_container_label = QLabel()
        self.ver_container_edit = QLineEdit()
        self.ver_browse_container_btn = QPushButton()
        self.ver_browse_container_btn.clicked.connect(self.on_ver_browse_container)
        row_cont.addWidget(self.ver_container_label)
        row_cont.addWidget(self.ver_container_edit, 1)
        row_cont.addWidget(self.ver_browse_container_btn)
        layout.addLayout(row_cont)

        row_pw = QHBoxLayout()
        self.ver_password_label = QLabel()
        self.ver_password_edit = QLineEdit()
        self.ver_password_edit.setEchoMode(QLineEdit.Password)
        row_pw.addWidget(self.ver_password_label)
        row_pw.addWidget(self.ver_password_edit, 1)
        layout.addLayout(row_pw)

        row_btn = QHBoxLayout()
        row_btn.addStretch()
        self.ver_button = QPushButton()
        self.ver_button.clicked.connect(self.on_verify_clicked)
        row_btn.addWidget(self.ver_button)
        layout.addLayout(row_btn)

        layout.addStretch()
        self.tabs.addTab(tab, "Verify")

    def _build_passwd_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        row_cont = QHBoxLayout()
        self.pw_container_label = QLabel()
        self.pw_container_edit = QLineEdit()
        self.pw_browse_container_btn = QPushButton()
        self.pw_browse_container_btn.clicked.connect(self.on_pw_browse_container)
        row_cont.addWidget(self.pw_container_label)
        row_cont.addWidget(self.pw_container_edit, 1)
        row_cont.addWidget(self.pw_browse_container_btn)
        layout.addLayout(row_cont)

        row_cpw = QHBoxLayout()
        self.pw_current_label = QLabel()
        self.pw_current_edit = QLineEdit()
        self.pw_current_edit.setEchoMode(QLineEdit.Password)
        row_cpw.addWidget(self.pw_current_label)
        row_cpw.addWidget(self.pw_current_edit, 1)
        layout.addLayout(row_cpw)

        row_npw = QHBoxLayout()
        self.pw_new_label = QLabel()
        self.pw_new_edit = QLineEdit()
        self.pw_new_edit.setEchoMode(QLineEdit.Password)
        row_npw.addWidget(self.pw_new_label)
        row_npw.addWidget(self.pw_new_edit, 1)
        layout.addLayout(row_npw)

        row_npw2 = QHBoxLayout()
        self.pw_new_confirm_label = QLabel()
        self.pw_new_confirm_edit = QLineEdit()
        self.pw_new_confirm_edit.setEchoMode(QLineEdit.Password)
        row_npw2.addWidget(self.pw_new_confirm_label)
        row_npw2.addWidget(self.pw_new_confirm_edit, 1)
        layout.addLayout(row_npw2)

        row_it = QHBoxLayout()
        self.pw_iterations_label = QLabel()
        self.pw_iterations_spin = QSpinBox()
        self.pw_iterations_spin.setRange(0, 2_000_000)
        self.pw_iterations_spin.setSingleStep(10_000)
        self.pw_iterations_spin.setValue(0) 
        row_it.addWidget(self.pw_iterations_label)
        row_it.addWidget(self.pw_iterations_spin)
        row_it.addStretch()
        layout.addLayout(row_it)

        row_btn = QHBoxLayout()
        row_btn.addStretch()
        self.pw_button = QPushButton()
        self.pw_button.clicked.connect(self.on_passwd_clicked)
        row_btn.addWidget(self.pw_button)
        layout.addLayout(row_btn)

        layout.addStretch()
        self.tabs.addTab(tab, "Password")

    def on_enc_browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr(self.lang, "gui.button.browse_file"),
        )
        if path:
            self.enc_input_edit.setText(path)

    def on_enc_browse_folder(self):
        path = QFileDialog.getExistingDirectory(
            self,
            tr(self.lang, "gui.button.browse_folder"),
        )
        if path:
            self.enc_input_edit.setText(path)

    def on_enc_browse_output(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr(self.lang, "gui.button.browse_container"),
            filter="*.secarc",
        )
        if path:
            self.enc_output_edit.setText(path)

    def on_dec_browse_container(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr(self.lang, "gui.button.browse_container"),
            filter="*.secarc",
        )
        if path:
            self.dec_container_edit.setText(path)

    def on_dec_browse_output_dir(self):
        path = QFileDialog.getExistingDirectory(
            self,
            tr(self.lang, "gui.button.browse_output_dir"),
        )
        if path:
            self.dec_output_dir_edit.setText(path)

    def on_list_browse_container(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr(self.lang, "gui.button.browse_container"),
            filter="*.secarc",
        )
        if path:
            self.list_container_edit.setText(path)

    def on_ver_browse_container(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr(self.lang, "gui.button.browse_container"),
            filter="*.secarc",
        )
        if path:
            self.ver_container_edit.setText(path)

    def on_pw_browse_container(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr(self.lang, "gui.button.browse_container"),
            filter="*.secarc",
        )
        if path:
            self.pw_container_edit.setText(path)

    def on_encrypt_clicked(self):
        input_path = self.enc_input_edit.text().strip()
        output_path = self.enc_output_edit.text().strip()
        password = self.enc_password_edit.text()
        password2 = self.enc_password_confirm_edit.text()
        iterations = self.enc_iterations_spin.value()
        overwrite = self.enc_force_checkbox.isChecked()

        if not input_path or not output_path or not password or not password2:
            msg = tr(self.lang, "gui.msg.error.missing_input")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return

        if password != password2:
            msg = tr(self.lang, "gui.msg.error.password_mismatch")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return

        src = Path(input_path)
        if not src.exists():
            if src.is_file():
                msg = tr(self.lang, "gui.msg.error.no_file")
            else:
                msg = tr(self.lang, "gui.msg.error.no_dir")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return

        self.set_status_running()

        try:
            encrypt_path(str(src), output_path, password, iterations=iterations, overwrite=overwrite)
        except FileExistsError:
            msg = tr(self.lang, "encrypt.overwrite_blocked")
            self.set_status_error(msg)
            self.show_error_box(msg)
        except FileNotFoundError:
            msg = tr(self.lang, "encrypt.source_missing")
            self.set_status_error(msg)
            self.show_error_box(msg)
        except SecureArchiveError as ex:
            msg = f"{tr(self.lang, 'common.error')}: {ex}"
            self.set_status_error(msg)
            self.show_error_box(msg)
        except OSError:
            msg = tr(self.lang, "error.io")
            self.set_status_error(msg)
            self.show_error_box(msg)
        except Exception as ex:
            msg = f"{tr(self.lang, 'error.generic')}: {ex}"
            self.set_status_error(msg)
            self.show_error_box(msg)
        else:
            self.set_status_done("gui.msg.encrypt.success")

    def on_decrypt_clicked(self):
        container_path = self.dec_container_edit.text().strip()
        output_dir = self.dec_output_dir_edit.text().strip()
        password = self.dec_password_edit.text()

        if not container_path or not output_dir or not password:
            msg = tr(self.lang, "gui.msg.error.missing_input")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return

        cont = Path(container_path)
        if not cont.exists():
            msg = tr(self.lang, "gui.msg.error.no_file")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return

        out_dir = Path(output_dir)
        self.set_status_running()

        try:
            decrypt_container(str(cont), str(out_dir), password)
        except InvalidContainerError:
            msg = tr(self.lang, "error.invalid_container")
            self.set_status_error(msg)
            self.show_error_box(msg)
        except WrongPasswordError:
            msg = tr(self.lang, "error.wrong_password")
            self.set_status_error(msg)
            self.show_error_box(msg)
        except SecureArchiveError as ex:
            msg = f"{tr(self.lang, 'common.error')}: {ex}"
            self.set_status_error(msg)
            self.show_error_box(msg)
        except OSError:
            msg = tr(self.lang, "error.io")
            self.set_status_error(msg)
            self.show_error_box(msg)
        except Exception as ex:
            msg = f"{tr(self.lang, 'error.generic')}: {ex}"
            self.set_status_error(msg)
            self.show_error_box(msg)
        else:
            self.set_status_done("gui.msg.decrypt.success")

    def on_list_clicked(self):
        container_path = self.list_container_edit.text().strip()
        password = self.list_password_edit.text()

        if not container_path or not password:
            msg = tr(self.lang, "gui.msg.error.missing_input")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return

        cont = Path(container_path)
        if not cont.exists():
            msg = tr(self.lang, "gui.msg.error.no_file")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return

        self.set_status_running()

        try:
            entries = list_container(str(cont), password)
        except InvalidContainerError:
            msg = tr(self.lang, "error.invalid_container")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return
        except WrongPasswordError:
            msg = tr(self.lang, "error.wrong_password")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return
        except SecureArchiveError as ex:
            msg = f"{tr(self.lang, 'common.error')}: {ex}"
            self.set_status_error(msg)
            self.show_error_box(msg)
            return
        except Exception as ex:
            msg = f"{tr(self.lang, 'error.generic')}: {ex}"
            self.set_status_error(msg)
            self.show_error_box(msg)
            return

        self.append_log(tr(self.lang, "list.header"))
        for e in entries:
            line = tr(self.lang, "list.entry", path=e["path"], size=e["size"])
            self.append_log(f" - {line}")

        self.set_status_done("gui.msg.list.success")

    def on_verify_clicked(self):
        container_path = self.ver_container_edit.text().strip()
        password = self.ver_password_edit.text()

        if not container_path or not password:
            msg = tr(self.lang, "gui.msg.error.missing_input")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return

        cont = Path(container_path)
        if not cont.exists():
            msg = tr(self.lang, "gui.msg.error.no_file")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return

        self.set_status_running()

        try:
            ok = verify_container(str(cont), password)
        except Exception:
            ok = False

        if ok:
            self.set_status_done("gui.msg.verify.success")
        else:
            msg = tr(self.lang, "gui.msg.verify.failure")
            self.set_status_error(msg)
            self.show_error_box(msg)

    def on_passwd_clicked(self):
        container_path = self.pw_container_edit.text().strip()
        current_pw = self.pw_current_edit.text()
        new_pw = self.pw_new_edit.text()
        new_pw2 = self.pw_new_confirm_edit.text()
        iterations = self.pw_iterations_spin.value()
        if iterations == 0:
            iterations = None

        if not container_path or not current_pw or not new_pw or not new_pw2:
            msg = tr(self.lang, "gui.msg.error.missing_input")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return

        if new_pw != new_pw2:
            msg = tr(self.lang, "gui.msg.error.password_mismatch")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return

        cont = Path(container_path)
        if not cont.exists():
            msg = tr(self.lang, "gui.msg.error.no_file")
            self.set_status_error(msg)
            self.show_error_box(msg)
            return

        self.set_status_running()

        try:
            change_password(str(cont), current_pw, new_pw, iterations=iterations)
        except InvalidContainerError:
            msg = tr(self.lang, "error.invalid_container")
            self.set_status_error(msg)
            self.show_error_box(msg)
        except WrongPasswordError:
            msg = tr(self.lang, "error.wrong_password")
            self.set_status_error(msg)
            self.show_error_box(msg)
        except SecureArchiveError as ex:
            msg = f"{tr(self.lang, 'common.error')}: {ex}"
            self.set_status_error(msg)
            self.show_error_box(msg)
        except Exception as ex:
            msg = f"{tr(self.lang, 'error.generic')}: {ex}"
            self.set_status_error(msg)
            self.show_error_box(msg)
        else:
            self.set_status_done("gui.msg.passwd.success")

    def on_github_clicked(self):
        webbrowser.open("https://github.com/bylickilabs")

    def on_info_clicked(self):
        QMessageBox.information(
            self,
            tr(self.lang, "gui.info.title"),
            tr(self.lang, "gui.info.text"),
        )

def main():
    app = QApplication(sys.argv)
    window = SecureArchiveWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()