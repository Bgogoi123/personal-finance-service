from pwdlib import PasswordHash

password_encryption = PasswordHash.recommended()

def get_hashed_password(password: str):
  return password_encryption.hash(password)

def verify_password(plain_password: str, hashed_password: str):
  return password_encryption.verify(plain_password, hashed_password)