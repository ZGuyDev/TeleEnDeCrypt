from hashlib import sha256
import aes_cipher as aes

__secret_salt = "O&*TGBOO^: J:U&:"


def hash_key(key) -> str:
    m = sha256()
    m.update(bytearray(__secret_salt, encoding="utf-8"))
    m.update(bytearray(key, encoding="utf-8"))
    return m.hexdigest()


def encrypt(raw: bytes or str, key) -> bytes:
    data_encrypter = aes.DataEncrypter(
        aes.Pbkdf2Sha512(1024 * 1024)
    )
    data_encrypter.Encrypt(raw, [key], [__secret_salt])
    return data_encrypter.GetEncryptedData()


def decrypt(enc, key) -> bytes:
    data_decrypter = aes.DataDecrypter(
        aes.Pbkdf2Sha512(1024 * 1024)
    )
    data_decrypter.Decrypt(enc, [key])
    return data_decrypter.GetDecryptedData()
