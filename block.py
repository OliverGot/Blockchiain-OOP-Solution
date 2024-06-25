import hashlib

class Block():
    """
    Class representing a block in the blockchain.

    Attributes:
        index (int): Index of the block in the blockchain.
        time (datetime): Timestamp of the block creation.
        data (str): Data stored in the block.
        nonce (int): Value incremented for proof of work.
        previousHash (str): Hash of the previous block.
        hash (str): Hash of the current block.
    """
    def __init__(self, index, time, data, previousHash):
        self.index = index
        self.time = time
        self.data = data
        self.nonce = 0
        self.previousHash = previousHash
        self.hash = self.calculateHash()
    
    def calculateHash(self):
        """
        Calculate the hash of the block using its attributes.

        Returns:
            str: The calculated hash of the block.
        """
        blockHash = hashlib.sha256()
        blockHash.update(str(self.index).encode("utf-8") + str(self.time).encode("utf-8") + str(self.data).encode("utf-8") + str(self.previousHash).encode("utf-8") + str(self.nonce).encode("utf-8"))
        return blockHash.hexdigest()

    def mine(self, difficulty, userMining, paymentPerMined):
        """
        Mine the block by finding a hash with a specified number of leading zeros.

        Args:
            difficulty (int): Number of leading zeros required in the hash.
            userMining (str): User who is mining the block.
            paymentPerMinded (int): How much the user is payed for mining the block.
        """
        self.data += f"Transaction,{'0' * 64},{paymentPerMined},{userMining},{'0' * 64}"
        while self.hash[0:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculateHash()
        print(f"Mined:{self.hash}. Added {paymentPerMined} to {userMining}'s ballance.")

    def __str__(self):
        return (
            f"Index: {self.index}\n"
            f"Time: {self.time}\n"
            f"Data: {self.data}\n"
            f"Nonce: {self.nonce}\n"
            f"Previous Hash: {self.previousHash}\n"
            f"Hash: {self.hash}"
        )