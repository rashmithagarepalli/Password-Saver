import os
import json
import base64
import hashlib
from cryptography.fernet import Fernet

VAULT_FILE = "vault.bin"
SALT_FILE = "salt.bin"


# ---------------- KEY GENERATION ----------------
def generate_key(password, salt):
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000
    )
    return base64.urlsafe_b64encode(key)


# ---------------- FILE HANDLING ----------------
def get_salt():
    if not os.path.exists(SALT_FILE):
        salt = os.urandom(16)
        with open(SALT_FILE, "wb") as f:
            f.write(salt)
        return salt
    with open(SALT_FILE, "rb") as f:
        return f.read()


def load_vault():
    if not os.path.exists(VAULT_FILE):
        return None
    with open(VAULT_FILE, "rb") as f:
        return f.read()


def save_vault(data):
    with open(VAULT_FILE, "wb") as f:
        f.write(data)


# ---------------- ENCRYPT / DECRYPT ----------------
def encrypt(data, key):
    f = Fernet(key)
    return f.encrypt(json.dumps(data).encode())


def decrypt(data, key):
    f = Fernet(key)
    return json.loads(f.decrypt(data).decode())


# ---------------- MAIN APP ----------------
def main():
    print("\n🔐 Secure Password Saver")

    salt = get_salt()

    master_password = input("Enter master password: ")
    key = generate_key(master_password, salt)

    encrypted_vault = load_vault()

    try:
        if encrypted_vault:
            vault = decrypt(encrypted_vault, key)
        else:
            vault = []
    except:
        print("❌ Wrong password or vault corrupted!")
        return

    while True:
        print("\n------ MENU ------")
        print("1. Add password")
        print("2. View passwords")
        print("3. Delete password")
        print("4. Exit")

        choice = input("Choose option: ")

        # ADD PASSWORD
        if choice == "1":
            site = input("Website: ")
            username = input("Username: ")
            password = input("Password: ")

            vault.append({
                "site": site,
                "username": username,
                "password": password
            })

            save_vault(encrypt(vault, key))
            print("✅ Saved successfully!")

        # VIEW PASSWORDS
        elif choice == "2":
            if not vault:
                print("No passwords saved.")
            else:
                for i, item in enumerate(vault):
                    print(f"\n[{i}] {item['site']}")
                    print("Username:", item["username"])
                    print("Password:", item["password"])

        # DELETE PASSWORD
        elif choice == "3":
            for i, item in enumerate(vault):
                print(f"{i}. {item['site']}")

            idx = int(input("Enter index to delete: "))

            if 0 <= idx < len(vault):
                removed = vault.pop(idx)
                save_vault(encrypt(vault, key))
                print("🗑 Deleted:", removed["site"])
            else:
                print("Invalid index")

        # EXIT
        elif choice == "4":
            save_vault(encrypt(vault, key))
            print("Goodbye 🔐")
            break

        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()