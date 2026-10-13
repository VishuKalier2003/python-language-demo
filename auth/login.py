import hashlib


def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()


def verify_password(password, salt, expected):
    return hash_password(password, salt) == expected
