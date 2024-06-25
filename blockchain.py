import datetime
from block import Block
import config

class Blockchain():
    """
    Class representing a blockchain.

    Attributes:
        __chain (list): Private list of blocks in the blockchain.
    """
    def __init__(self):
        self.__chain = [Block(0, datetime.datetime.now(), "The first block!", '0' * 64)]

    def addBlock(self, data, userMining):
        """
        Add a new block to the blockchain after mining it.

        Args:
            data (str): Data to be included in the new block.
            userMining (str): User who is mining the block.
        """
        newBlock = Block(len(self.__chain), datetime.datetime.now(), data, self.__chain[-1].hash)
        newBlock.mine(config.DIFFICULTY, userMining, config.PAYMENT_PER_MINED)
        self.__chain.append(newBlock)

    def getBlock(self, index):
        """
        Get a block by its index.

        Args:
            index (int): Index of the block to retrieve.

        Returns:
            Block: The block at the specified index.
        """
        return self.__chain[index]

    def isValid(self):
        """
        Validate the blockchain by checking the hashes of each block.

        Returns:
            bool: True if the blockchain is valid, False otherwise.
        """
        for block in self.__chain:
            if block.index != 0 and block.previousHash != self.__chain[block.index - 1].calculateHash() and block.hash[:config.DIFFICULTY] == '0' * config.PAYMENT_PER_MINED:
                return False
        return True