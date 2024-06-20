import datetime
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key, Encoding, PrivateFormat, PublicFormat, NoEncryption
)

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
        self.data += f"Transaction,{'0' * 64},{PAYMENT_PER_MINED},{userMining},{'0' * 64}"
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
        self.__hash = self.calculateHash(self.__username, self.__password)
        self.__privateKey = None
    
    def calculateHash(self, username, password):
        blockHash = hashlib.sha256()
        blockHash.update(str(username).encode("utf-8") + str(password).encode("utf-8"))
        return blockHash.hexdigest()

    def generateKeys(self):
        if not self.__privateKey:
            self.__privateKey = rsa.generate_private_key(public_exponent=65537,key_size=2048)
        self.publicKey = self.__privateKey.public_key()
    
    def signMessage(self, username, password, message):
        if self.__hash == self.calculateHash(username, password):
            signature = self.__privateKey.sign(
                message.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signature.hex() 

    def getHash(self):
        return self.__hash
    
class Transaction():
    def __init__(self):
        self.__data = ""
    
    def addTransaction(self, transferer, amount, transferee, signature, blockchain):
        if calculateBallance(transferer, blockchain) < amount:
            amount = 0
        self.__data += f"Transaction,{transferer},{amount},{transferee},{signature};"
    
    def addNewUserKey(self, user):
        publicPem = user.publicKey.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo
    )
        self.__data += f"Signature,{user.getHash()},{publicPem.hex()};"

    def getData(self):
        return self.__data
    
def calculateBallance(hash, blockchain):
    ballance = 0
    userMap = {"0" * 64: "0" * 64}
    for i in range(blockchain.getBlock(-1).index + 1):
        blockData = blockchain.getBlock(i).data.split(";")
        for transaction in blockData:
            for line in transaction.split(";"):
                transactionData = line.split(",")
                if transactionData[0] == "Transaction":
                    if transactionData[3] == hash:
                        transactionHash = calculateTransactionHash(transactionData[1], transactionData[2], transactionData[3])
                        currentKey = userMap[transactionData[1]]
                        if validateSignature(transactionHash, currentKey, transactionData[4]):
                            ballance += int(transactionData[2])

                elif transactionData[0] == "Signature" and len(transactionData) == 3:
                    userMap[transactionData[1]] = transactionData[2]

    if blockchain.isValid():
        return ballance
    return 0

def validateSignature(message, publicKeyHex, signature):
    if signature == "0" * 64:
        return True
    publicKeyBytes = bytes.fromhex(publicKeyHex)
    publicKey = load_pem_public_key(publicKeyBytes)
    try:
        publicKey.verify(
            bytes.fromhex(signature),
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
       print(e)
       return False
   

def calculateTransactionHash(transferer, amount, transferee):
    transactionHash = hashlib.sha256()
    transactionHash.update(str(transferer).encode("utf-8") + str(amount).encode("utf-8") + str(transferee).encode("utf-8"))
    return transactionHash.hexdigest()

def main():
    blockchain = Blockchain()
    currentUsername = ""
    currentPassword = ""
    currentUser = None
    registeredUsers = []
    loggedIn = False
    currentTransaction = Transaction()

    while True:
        if not loggedIn:
            print("[L]ogin / register")
            print("Get user [b]allance")
            print("[Q]uit")
            userInput = input().lower()

            if userInput == 'l':
                currentUsername = input("Enter username: ")
                currentPassword = input("Enter password: ")

                found = False
                for user in registeredUsers:
                    if User(currentUsername, currentPassword).getHash() == user.getHash():
                        currentUser = user
                        found = True
                        
                if not found:
                    registeredUsers.append(User(currentUsername, currentPassword))
                    currentUser = registeredUsers[-1]
                    currentUser.generateKeys()
                    currentTransaction.addNewUserKey(currentUser)
                loggedIn = True

            elif userInput == 'b':
                hash = input("Enter hash: ")
                print(calculateBallance(hash, blockchain))

            elif userInput == 'q':
                break

            else:
                print("That is not a recognised command.")
                
        else:
            print()
            print(f"Logged in as: {currentUser.getHash()}")
            print("Get my [b]allance")
            print("[M]ine")
            print("Make a [t]ransaction")
            print("[L]ogout")
            userInput = input().lower()

            if userInput == 'b':
                print(calculateBallance(currentUser.getHash(), blockchain))

            elif userInput == 'm':
                blockchain.addBlock(currentTransaction.getData(), currentUser.getHash())
                currentTransaction = Transaction()

            elif userInput == 't':
                amount = int(input("Enter Amount: "))
                otherUser = input("Enter other user hash: ")
                transactionHash = calculateTransactionHash(currentUser.getHash(), amount, otherUser)
                currentTransaction.addTransaction(currentUser.getHash(), amount, otherUser, currentUser.signMessage(currentUsername, currentPassword, transactionHash), blockchain)

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