import base64

# QUEUE
class Queue:
    def __init__(self, max_size=10):
        self.data = []
        self.max_size = max_size

    def enqueue(self, item):
        if len(self.data) >= self.max_size:
            self.data.pop(0)
        self.data.append(item)

    def get_all(self):
        return list(self.data)


# ENCRYPTION
class Encryption:
    __SHIFT = 3

    @staticmethod
    def encode(text):
        shifted = ''.join(chr(ord(c) + Encryption.__SHIFT) for c in text)
        return base64.b64encode(shifted.encode()).decode()

    @staticmethod
    def decode(encoded):
        decoded = base64.b64decode(encoded).decode()
        return ''.join(chr(ord(c) - Encryption.__SHIFT) for c in decoded)


# ACCOUNT
class Account:
    def __init__(self, platform, username, password):
        self.__platform = platform
        self.__username = username
        self.__password_encrypted = Encryption.encode(password)

    def get_platform(self):
        return self.__platform

    def get_username(self):
        return self.__username

    def get_password(self):
        return Encryption.decode(self.__password_encrypted)

    def set_password(self, new_password):
        self.__password_encrypted = Encryption.encode(new_password)


# VAULT MANAGER
class VaultManager:
    def __init__(self):
        self.__accounts = []

    def add(self, acc):
        self.__accounts.append(acc)

    def delete(self, index):
        self.__accounts.pop(index)

    def get_all_accounts(self):
        return list(self.__accounts)

    def get_account(self, index):
        return self.__accounts[index]


# MASTER PASSWORD
class MasterPassword:
    __MASTER = "admin123"

    @staticmethod
    def check(pwd):
        return pwd == MasterPassword.__MASTER