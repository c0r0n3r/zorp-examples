import Cypher
import unittest

class TestBaseCypher():
    def test_transparency(self):
        cyphertext = self.cypher.encrypt('cyphertext')
        plaintext = self.cypher.decrypt(cyphertext)
        self.assertEqual(plaintext, 'cyphertext')

        cyphertext = self.cypher_with_magic.encrypt('cyphertext')
        plaintext = self.cypher_with_magic.decrypt(cyphertext)
        self.assertEqual(plaintext, 'cyphertext')


class TestNoCypher(unittest.TestCase, TestBaseCypher):
    def setUp(self):
        self.cypher = Cypher.NoCypher()
        self.cypher_with_magic = Cypher.NoCypher(magic='magic')

    def test_encrypt(self):
        self.assertEqual(self.cypher.encrypt('plaintext'), 'plaintext')

    def test_decrypt(self):
        self.assertEqual(self.cypher.decrypt('cyphertext'), 'cyphertext')


class TestBase64Cypher(unittest.TestCase, TestBaseCypher):
    def setUp(self):
        self.cypher = Cypher.Base64Cypher()
        self.cypher_with_magic = Cypher.Base64Cypher(magic='magic')


if __name__ == '__main__':
    unittest.main()
