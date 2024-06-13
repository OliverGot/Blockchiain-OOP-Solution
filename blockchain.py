import datetime
import hashlib

class Block():
    def __init__(self, index, time, data, previousHash):
        self.index = index
        self.time = time
        self.data = data
        self.previousHash = previousHash
        self.hash = self.calculateHash()
    
    def calculateHash(self):
        blockString = str(self.index) + str(self.time) + str(self.data) + str(self.previousHash)
        return hashlib.sha256(blockString.encode()).hexdigest()
    
    def __str__(self):
        return f"Index:{self.index}\nTime:{self.time}\nData:{self.data}\nPrevious Hash:{self.previousHash}\nHash:{self.hash}"

class Blockchain():
    def __init__(self):
        self.__chain = [Block(0, datetime.datetime.now(), "The first block!", "0")]

    def addBlock(self, data):
        self.__chain.append(Block(len(self.__chain), datetime.datetime.now(), data, self.__chain[-1].calculateHash()))

    def getBlock(self, index):
        return self.__chain[index]

    def isValid(self):
        for block in self.__chain:
            if block.index != 0 and block.previousHash != self.__chain[block.index - 1].calculateHash():
                return False
        return True

blockchain = Blockchain()
blockchain.addBlock("hello")
blockchain.addBlock("data")
blockchain.addBlock("Cool")
for i in range(0, blockchain.getBlock(-1).index + 1):
    print(blockchain.getBlock(i))
    print()
print(blockchain.isValid())

