# CONTAINER_FORMAT.md — SecureArchive / TitanCrypt Engine

## 1. Overview

The `.secarc` container format is a compact, authenticated, fully encrypted binary format designed for long‑term secure storage.  
It prevents metadata leakage, ensures integrity, and provides deterministic, versioned behavior.

SecureArchive uses:
- AES‑256‑GCM for encryption & authentication  
- PBKDF2‑SHA512 for key derivation  
- A strict header → payload layout  
- A fully encrypted manifest structure  
- A fixed magic identifier for format validation  

<br>

## 2. High-Level Structure

```
+-----------------------------+
|  MAGIC (8 bytes)            |
+-----------------------------+
|  VERSION (1 byte)           |
+-----------------------------+
|  SALT_LEN (1 byte)          |
+-----------------------------+
|  SALT (variable)            |
+-----------------------------+
|  ITERATIONS (4 bytes)       |
+-----------------------------+
|  NONCE_LEN (1 byte)         |
+-----------------------------+
|  NONCE (variable)           |
+-----------------------------+
|  CIPHERTEXT (encrypted)     |
|  - manifest.json            |
|  - PAYLOAD_SEPARATOR        |
|  - raw file data blocks     |
+-----------------------------+
```

Everything after the header is encrypted with AES‑GCM.

<br>

## 3. Header Specification

### 3.1. Magic Identifier
```
"SECARC01"  (8 bytes, ASCII)
```
Used to detect container type and validate integrity before decryption.

### 3.2. Version
```
1 byte
```
Current version = `1`  
Version mismatches cause immediate rejection.

### 3.3. Salt Length + Salt
```
SALT_LEN = 1 byte
SALT     = SALT_LEN bytes
```
Generated via `os.urandom()`.  
Used for PBKDF2‑SHA512 key derivation.

### 3.4. Iterations
```
4 bytes, big-endian unsigned integer
```
PBKDF2 iteration count; default 300,000.

### 3.5. Nonce Length + Nonce
```
NONCE_LEN = 1 byte
NONCE     = NONCE_LEN bytes
```
Nonce for AES‑GCM encryption (typically 12 bytes).

<br>

## 4. Ciphertext Structure

The ciphertext is produced by:
```
AES-256-GCM(key, payload, aad=MAGIC)
```

### 4.1. AAD (Authenticated Additional Data)
The `MAGIC` header is authenticated but not encrypted.

### 4.2. Payload Structure (before encryption)

```
[manifest JSON] + PAYLOAD_SEPARATOR + [raw file data]
```

### 4.3. Separator
```
b"\n---PAYLOAD---\n"
```
Used to differentiate the encrypted manifest from encrypted file data.

### 4.4. Authentication Tag
Stored at the end of the ciphertext automatically via AES‑GCM.

<br>

## 5. Manifest Specification

Stored as UTF‑8 JSON inside the encrypted payload.

### 5.1. Manifest Layout

```
{
  "version": 1,
  "cipher": "AES-256-GCM",
  "kdf": {
    "type": "PBKDF2-SHA512",
    "iterations": 300000,
    "salt_hex": "..."
  },
  "root": "/absolute/path/to/original/location",
  "entries": [
    {
      "path": "relative/path/to/file",
      "size": 12345,
      "mtime": 1700000000,
      "offset": 0,
      "length": 12345
    }
  ]
}
```

### 5.2. Fields Explained

- **version** — Container format version  
- **cipher** — Encryption scheme  
- **kdf** — Key derivation parameters (salt + iterations)  
- **root** — Original source directory (absolute path)  
- **entries** — List of files inside the archive  

<br>

## 6. File Entries

Each file inside the container has:

| Field      | Description |
|------------|-------------|
| `path`     | Relative path inside the archive |
| `size`     | File size in bytes |
| `mtime`    | Unix timestamp |
| `offset`   | Start byte in data section |
| `length`   | Number of bytes to extract |

Offsets refer to the decrypted payload’s data region, not the ciphertext.

<br>

## 7. Integrity Properties

- GCM authentication ensures no block can be modified without detection  
- Manifest + data are covered by a single AEAD operation  
- Offsets cannot be modified without invalidating the container  
- Any corruption → `InvalidContainerError`  

<br>

## 8. Rationale Behind Design

### 8.1. No plaintext metadata
Avoids forensic leaks of:
- Filenames  
- File sizes  
- Folder structure  

### 8.2. Versioned header
Allows migration to:
- Future container formats  
- Compression layers  
- Parallel block encryption  
- Hardware key support  

### 8.3. Unified encryption model
One encryption pass = simpler, safer, more robust.

<br>

## 9. Future Format (Version 2 Roadmap)

Planned improvements:
- Block-based encryption  
- Parallel GCM streams  
- Embedded compression support  
- Extended metadata fields  
- Optional integrity-only mode  
