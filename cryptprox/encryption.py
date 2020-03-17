from os import path
from Cryptodome import Random
from Cryptodome.Cipher import AES

KEY_SIZE = 16  # encryption key size, in bytes
KEY_FILE = "/home/elmjag/area51/webcrypt/key"

class CryptoErr(Exception):
    def error_message(self):
        return self.args[0]


def _generate_key(key_file):
    # generate a new random encryption key
    # and write it to the specified key file
    key = Random.get_random_bytes(KEY_SIZE)
    with open(key_file, "wb") as f:
        f.write(key)

    print(f"wrote new encryption key to {key_file}")
    return key


def get_key():
    if path.isfile(KEY_FILE):
        # load the key from specified key file
        with open(KEY_FILE, "rb") as f:
            return f.read()

    # no key file found, create new key
    return _generate_key(KEY_FILE)

# src_file - django uploaded file
def encrypt(key, src_file, dest_file):
    # use 16-byte nonce, as recommended for the EAX mode
    nonce = Random.get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_EAX, nonce)

    with open(dest_file, "wb") as dest:
        # write down used nonce
        dest.write(nonce)

        # encrypt uploaded file by chunks
        for chunk in src_file.chunks():
            dest.write(cipher.encrypt(chunk))

        # write down the MAC/tag
        dest.write(cipher.digest())


def decrypt(key, src_file):
    src_size = path.getsize(src_file)

    with open(src_file, "rb") as src:
        nonce = src.read(16)
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        ciphertext = src.read(src_size - 32)

        # decrypt
        plaintext = cipher.decrypt(ciphertext)

        # load MAC tag and verify integrity of the file
        mac_tag = src.read()
        try:
            cipher.verify(mac_tag)
        except ValueError as e:
            # MAC check failed, source file corrupted
            raise CryptoErr(e.args[0])

        return plaintext
