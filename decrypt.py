import os
import zipfile
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import getpass

def derive_key_from_password(password: bytes, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def decrypt_file(enc_file, decrypted_zip, password):
    with open(enc_file, 'rb') as f:
        data = f.read()
    salt = data[:16]
    encrypted_data = data[16:]
    key = derive_key_from_password(password, salt)
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)
    with open(decrypted_zip, 'wb') as f:
        f.write(decrypted_data)
    print(f"Decrypted zip file saved: {decrypted_zip}")

def extract_zip_to_folders(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for file_info in zipf.infolist():
            target_path = file_info.filename
            target_folder = os.path.dirname(target_path)
            if target_folder and not os.path.exists(target_folder):
                print(f"Warning: Destination folder does not exist: {target_folder}")
            with zipf.open(file_info) as source, open(target_path, 'wb') as target:
                target.write(source.read())
            print(f"Extracted: {target_path}")

if __name__ == "__main__":
    ENC_FILE = "secret.enc"
    DECRYPTED_ZIP = "decrypted.zip"

    password = getpass.getpass("Enter password for decryption: ").encode()

    decrypt_file(ENC_FILE, DECRYPTED_ZIP, password)

    extract_zip_to_folders(DECRYPTED_ZIP)

    os.remove(DECRYPTED_ZIP)
