import datetime

class Block():
    def __init__(self, index, time, data, previousHash):
        self.index = index
        self.time = time
        self.data = data
        self.previousHash = previousHash
        self.next = None

genesisBlock = Block(0, datetime.datetime.now(), "The first block!", "0")

