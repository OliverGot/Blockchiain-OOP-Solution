from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat,
)
from config import calculateBallance

class Transaction():
    """
    Class representing a transaction.

    Attributes:
        __data (str): Data of the transaction.
    """
    def __init__(self):
        self.__data = ""
    
    def addTransaction(self, transferer, amount, transferee, signature, blockchain):
        """
        Add a transaction between users to the transaction data.

        Args:
            transferer (str): Hash of the user transferring the amount.
            amount (int): Amount to be transferred.
            transferee (str): Hash of the user receiving the amount.
            signature (str): Signature of the transferer.
            blockchain (Blockchain): The blockchain instance.
        """
        if calculateBallance(transferer, blockchain) < amount:
            amount = 0
        self.__data += f"Transaction,{transferer},{amount},{transferee},{signature};"
    
    def addNewUserKey(self, user):
        """
        Add the public key of a new user to the transaction data.

        Args:
            user (User): The user whose public key is to be added.
        """
        publicPem = user.publicKey.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo
    )
        self.__data += f"Signature,{user.getHash()},{publicPem.hex()};"

    def getData(self):
        """
        Get the transaction data.

        Returns:
            str: The transaction data.
        """
        return self.__data