# OS MODULE → digunakan untuk pengecekan file & operasi file (cek exist, hapus, buat)
import os
# BASE64 MODULE → digunakan untuk melakukan encoding dan decoding password
import base64

# QUEUE → Menyimpan log/key history dengan ukuran terbatas (FIFO)
class Queue:
    __max_size = 0

    def __init__(self,max_size=10):
        # data → menampung item log
        self.data = []
        self.__max_size = max_size

    def enqueue(self, item):
        if len(self.data) >= self.__max_size:
            self.data.pop(0)
        # tambahkan item baru
        self.data.append(item)

    def get_all(self):
        # kembalikan list data (copy)
        return list(self.data)


# ENCRYPTION → Encode/Decode password menggunakan Base64 + Caesar Shift
class Encryption:
    __SHIFT = 3 # nilai shift untuk Caesar cipher

    @staticmethod
    def encode(text):
        # geser setiap karakter (Caesar cipher)
        shifted = ''.join(chr(ord(c) + Encryption.__SHIFT) for c in text)
        # encode ke base64
        return base64.b64encode(shifted.encode()).decode()

    @staticmethod
    def decode(encoded):
        # decode base64
        decoded = base64.b64decode(encoded).decode()
        # geser balik ke karakter asli
        return ''.join(chr(ord(c) - Encryption.__SHIFT) for c in decoded)


# ACCOUNT → Model data akun (platform, username, password encrypted)
class Account:
    __platform = ""
    __username = ""
    __password_encrypted = ""

    def __init__(self, platform, username, password):
        # simpan platform & username
        self.__platform = platform
        self.__username = username
        # password disimpan dalam bentuk terenkripsi
        self.__password_encrypted = Encryption.encode(password)

    def get_platform(self):
        return self.__platform

    def get_username(self):
        return self.__username

    # mengembalikan password asli setelah decode
    def get_password(self):
        return Encryption.decode(self.__password_encrypted)

    # update password dengan encode ulang
    def set_password(self, new_password):
        self.__password_encrypted = Encryption.encode(new_password)


# VAULT MANAGER → Menyimpan semua akun dan mengatur CRUD (Create, Read, Delete)
class VaultManager:
    __accounts = ""

    def __init__(self):
        # list menyimpan objek-objek Account
        self.__accounts = []

    def add(self, acc):
        # tambah akun baru
        self.__accounts.append(acc)

    def delete(self, index):
        # hapus akun berdasarkan index
        self.__accounts.pop(index)

    def get_all_accounts(self):
        # kembalikan semua akun sebagai list (copy)
        return list(self.__accounts)

    def get_account(self, index):
        # ambil akun berdasarkan index
        return self.__accounts[index]


# MASTER PASSWORD → Pengelolaan file master password (read, create, update)

MASTER_FILE = "Master.txt"  # lokasi penyimpanan master password

# GET MASTER PASSWORD → membaca atau membuat file jika belum ada
def get_master_password():
    # jika file tidak ada → buat file default berisi "admin123"
    if not os.path.exists(MASTER_FILE):
        with open(MASTER_FILE, "w") as f:
            f.write("admin123")
        return "admin123"
    
    with open(MASTER_FILE, "r") as f:
        # jika ada → baca isi file
        return f.read().strip()

# UPDATE MASTER PASSWORD → mengganti password lama ke baru
def update_master_password(old_pass, new_pass):
    current = get_master_password()
    
    # cek apakah password lama sesuai
    if old_pass != current:
        return False, "Password lama salah!"
    
    # jika benar → update file
    with open(MASTER_FILE, "w") as f:
        f.write(new_pass)

    return True, "Master password berhasil diperbarui!"