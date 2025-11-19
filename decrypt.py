import os
import zipfile
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidToken
import base64
import getpass


# ----------------------------------------
# Key Derivation (must match encrypt script)
# ----------------------------------------

def derive_key_from_password(password: bytes, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=150_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password))


# ----------------------------------------
# File Decryption
# ----------------------------------------

def decrypt_file(enc_file, output_zip, password):
    with open(enc_file, 'rb') as f:
        data = f.read()

    if len(data) < 17:
        raise ValueError("Encrypted file is too small or corrupted.")

    # First 16 bytes = salt
    salt = data[:16]
    encrypted_data = data[16:]

    key = derive_key_from_password(password, salt)
    fernet = Fernet(key)

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except InvalidToken:
        print("❌ Incorrect password or corrupted file.")
        raise SystemExit(1)

    with open(output_zip, 'wb') as f:
        f.write(decrypted_data)

    print(f"Decrypted ZIP written to: {output_zip}")


# ----------------------------------------
# ZIP Extraction (preserves folder structure)
# ----------------------------------------

def extract_zip_to_folders(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for file_info in zipf.infolist():

            # Full path inside ZIP
            target_path = file_info.filename

            # Create folders if needed
            folder = os.path.dirname(target_path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder)

            # Extract file
            with zipf.open(file_info) as src, open(target_path, 'wb') as dst:
                dst.write(src.read())

            print(f"Extracted: {target_path}")


# ----------------------------------------
# MAIN
# ----------------------------------------

if __name__ == "__main__":
    ENC_FILE = "secret.enc"
    DECRYPTED_ZIP = "decrypted.zip"

    password = getpass.getpass("Enter password for decryption: ").encode()

    decrypt_file(ENC_FILE, DECRYPTED_ZIP, password)

    extract_zip_to_folders(DECRYPTED_ZIP)

    # Remove temporary zip
    os.remove(DECRYPTED_ZIP)
    print(f"Removed temporary file: {DECRYPTED_ZIP}")
