class BaseCypher(object):
    def __init__(self, magic=""):
        self.magic = magic
        self.magic_len = len(magic)

    def encrypt(self, plaintext):
        cyphertext = self.magic + self._encrypt(plaintext)
        return cyphertext

    def _encrypt(self, plaintext):
        raise NotImplementedError

    def decrypt(self, cyphertext):
        if self.magic_len > 0 and len(cyphertext) < self.magic_len:
            raise IndexError
        plaintext = self._decrypt(cyphertext[self.magic_len:])
        return plaintext

    def _decrypt(self, cyphertext):
        raise NotImplementedError

class NoCypher(BaseCypher):
    def __init__(self, magic=""):
        super(NoCypher, self).__init__(magic)

    def _encrypt(self, plaintext):
        return plaintext

    def _decrypt(self, cyphertext):
        return cyphertext


class Base64Cypher(BaseCypher):
    base64 = __import__('base64')

    def __init__(self, magic=""):
        super(Base64Cypher, self).__init__(magic)

    def _encrypt(self, plaintext):
        return Base64Cypher.base64.b64encode(plaintext)

    def _decrypt(self, cyphertext):
        return Base64Cypher.base64.b64decode(cyphertext)


class RSAKeyCypher(BaseCypher):
    m2c = __import__('M2Crypto')

    def __init__(self, key_file, magic=""):
        super(RSAKeyCypher, self).__init__(magic)
        self.key = RSAKeyCypher.m2c.RSA.load_key(key_file)

    def _encrypt(self, plaintext):
        return key.public_encrypt(plaintext, RSAKeyCypher.m2c.RSA.pkcs1_oaep_padding)

    def _decrypt(self, cyphertext):
        return key.private_decrypt(cyphertext, RSAKeyCypher.m2c.RSA.pkcs1_oaep_padding)
