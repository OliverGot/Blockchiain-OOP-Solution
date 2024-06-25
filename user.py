import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class User():
    """
    Class representing a user (node) in the blockchain.

    Attributes:
        __username (str): Private, immutable username of the user.
        __password (str): Private, immutable password of the user.
        __hash (str): Hash of the username and password.
        __privateKey (rsa.RSAPrivateKey): Private key for signing transactions.
        publicKey (rsa.RSAPublicKey): Public key for verifying signatures.
    """
    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        self.__hash = self.calculateHash(self.__username, self.__password)
        self.__privateKey = None
        self.publicKey = None
    
    def calculateHash(self, username, password):
        """
        Calculate the hash of the username and password.

        Args:
            username (str): Username of the user.
            password (str): Password of the user.

        Returns:
            str: The calculated hash.
        """
        blockHash = hashlib.sha256()
        blockHash.update(str(username).encode("utf-8") + str(password).encode("utf-8"))
        return blockHash.hexdigest()

    def generateKeys(self):
        """
        Generate RSA key pair for the user if not already generated.
        """
        if not self.__privateKey:
            self.__privateKey = rsa.generate_private_key(public_exponent=65537,key_size=2048)
        self.publicKey = self.__privateKey.public_key()
    
    def signMessage(self, username, password, message):
        """
        Sign a message if the provided username and password match the user's credentials.

        Args:
            username (str): Username of the user.
            password (str): Password of the user.
            message (str): Message to be signed.

        Returns:
            str: The hexadecimal representation of the signature.
        """
        if self.__hash == self.calculateHash(username, password):
            signature = self.__privateKey.sign(
                message.encode("utf-8"),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signature.hex() 

    def getHash(self):
        """
        Get the hash of the user's credentials.

        Returns:
            str: The hash of the user's credentials.
        """
        return self.__hash