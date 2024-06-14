import datetime
import hashlib

DIFFICULTY = 3
PAYMENT_PER_MINED = (16 ** DIFFICULTY) // 4 ** (DIFFICULTY + 1)

class Block():
    def __init__(self, index, time, data, previousHash):
        self.index = index
        self.time = time
        self.data = data
        self.nonce = 0
        self.previousHash = previousHash
        self.hash = self.calculateHash()
    
    def calculateHash(self):
        blockHash = hashlib.sha256()
        blockHash.update(str(self.index).encode("utf-8") + str(self.time).encode("utf-8") + str(self.data).encode("utf-8") + str(self.previousHash).encode("utf-8") + str(self.nonce).encode("utf-8"))
        return blockHash.hexdigest()

    def mine(self, difficulty, userMining):
        self.data += f"{'0' * 64},{PAYMENT_PER_MINED},{userMining}"
        while self.hash[0:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculateHash()
        print(f"Mined:{self.hash}")

    def __str__(self):
        return f"Index:{self.index}\nTime:{self.time}\nData:{self.data}\nNonce:{self.nonce}\nPrevious Hash:{self.previousHash}\nHash:{self.hash}"

class Blockchain():
    def __init__(self):
        self.__chain = [Block(0, datetime.datetime.now(), "The first block!", "0" * 64)]

    def addBlock(self, data, userMining):
        newBlock = Block(len(self.__chain), datetime.datetime.now(), data, self.__chain[-1].hash)
        newBlock.mine(DIFFICULTY, userMining)
        self.__chain.append(newBlock)

    def getBlock(self, index):
        return self.__chain[index]

    def isValid(self):
        for block in self.__chain:
            if block.index != 0 and block.previousHash != self.__chain[block.index - 1].calculateHash():
                return False
        return True

class User():
    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        self.hash = self.calculateHash()
    
    def calculateHash(self):
        blockHash = hashlib.sha256()
        blockHash.update(str(self.__username).encode("utf-8") + str(self.__password).encode("utf-8"))
        return blockHash.hexdigest()
    
def calculateBallance(hash, blockchain):
    ballance = 0
    for i in range(blockchain.getBlock(-1).index + 1):
        blockData = blockchain.getBlock(i).data.split("\n")
        for transaction in blockData:
            if len(transaction.split(",")) == 3:
                transactionData = transaction.split(",")
                if transactionData[2] == hash:
                    ballance += int(transactionData[1])
    if blockchain.isValid():
        return ballance
    return 0
    
class Transaction():
    def __init__(self):
        self.__data = ""
    
    def addData(self, transferer, amount, transferee, blockchain):
        if calculateBallance(transferer, blockchain) < amount:
            amount = 0
        self.__data += f"{transferer},{amount},{transferee}\n"

    def getData(self):
        return self.__data
    
def main():
    blockchain = Blockchain()
    currentUsername = ""
    currentPassword = ""
    currentUser = None
    loggedIn = False
    currentTransaction = Transaction()
    while True:
        if not loggedIn:
            print("[L]ogin")
            print("Get user [b]allance")
            print("[Q]uit")
            userInput = input().lower()[0]
            if userInput == 'l':
                currentUsername = input("Enter username: ")
                currentPassword = input("Enter password: ")
                currentUser = User(currentUsername, currentPassword)
                loggedIn = True
            elif userInput == 'b':
                hash = input("Enter hash: ")
                calculateBallance(hash, blockchain)
            elif userInput == 'q':
                break
            else:
                print("That is not a recognised command.")
        else:
            print()
            print(f"Logged in as: {currentUser.hash}")
            print("Get my [b]allance")
            print("[M]ine")
            print("Make a [t]ransaction")
            print("[L]ogout")
            userInput = input().lower()[0]
            if userInput == 'b':
                print(calculateBallance(currentUser.hash, blockchain))
            elif userInput == 'm':
                blockchain.addBlock(currentTransaction.getData(), currentUser.hash)
            elif userInput == 't':
                amount = int(input("Enter Amount: "))
                otherUser = input("Enter other user hash: ")
                currentTransaction.addData(currentUser.hash, amount, otherUser, blockchain)
            elif userInput == 'l':
                loggedIn = False
            elif userInput == 'd':
                for i in range(blockchain.getBlock(-1).index + 1):
                    print(blockchain.getBlock(i))
                    print()
            else:
                print("That command isn't recognised")


if __name__ == "__main__":
    main()