import datetime
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key, Encoding, PublicFormat,
)

DIFFICULTY = 4
# Payment per block mined. Designed so that if difficulty increases by 1, currency / second mined /= 2
PAYMENT_PER_MINED = 8 ** (DIFFICULTY)

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

    def mine(self, difficulty, userMining):
        """
        Mine the block by finding a hash with a specified number of leading zeros.

        Args:
            difficulty (int): Number of leading zeros required in the hash.
            userMining (str): User who is mining the block.
        """
        self.data += f"Transaction,{'0' * 64},{PAYMENT_PER_MINED},{userMining},{'0' * 64}"
        while self.hash[0:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculateHash()
        print(f"Mined:{self.hash}. Added {PAYMENT_PER_MINED} to {userMining}'s ballance.")

    def __str__(self):
        return (
            f"Index: {self.index}\n"
            f"Time: {self.time}\n"
            f"Data: {self.data}\n"
            f"Nonce: {self.nonce}\n"
            f"Previous Hash: {self.previousHash}\n"
            f"Hash: {self.hash}"
        )

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
        newBlock.mine(DIFFICULTY, userMining)
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
            if block.index != 0 and block.previousHash != self.__chain[block.index - 1].calculateHash() and block.hash[:DIFFICULTY] == '0' * DIFFICULTY:
                return False
        return True

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
    
def calculateBallance(hash, blockchain):
    """
    Calculate the balance of a user by summing up all transactions involving the user.

    Args:
        hash (str): Hash of the user whose balance is to be calculated.
        blockchain (Blockchain): The blockchain instance.

    Returns:
        int: The calculated balance of the user.
    """
    ballance = 0
    userMap = {'0' * 64: '0' * 64}
    for i in range(blockchain.getBlock(-1).index + 1):
        blockData = blockchain.getBlock(i).data.split(';')
        for transaction in blockData:
            for line in transaction.split(';'):
                transactionData = line.split(',')
                
                if transactionData[0] == "Transaction":
                    transactionHash = calculateTransactionHash(transactionData[1], transactionData[2], transactionData[3])
                    currentKey = userMap[transactionData[1]]
                    if transactionData[3] == hash:
                        if validateSignature(transactionHash, currentKey, transactionData[4]):
                            ballance += int(transactionData[2])
                    if transactionData[1] == hash:
                        if validateSignature(transactionHash, currentKey, transactionData[4]):
                            ballance -= int(transactionData[2])

                elif transactionData[0] == "Signature" and len(transactionData) == 3:
                    userMap[transactionData[1]] = transactionData[2]

    if blockchain.isValid():
        return ballance
    return 0

def validateSignature(message, publicKeyHex, signature):
    """
    Validate the signature of a transaction.

    Args:
        message (str): The original message.
        publicKeyHex (str): Hexadecimal representation of the public key.
        signature (str): Hexadecimal representation of the signature.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    if signature == '0' * 64:
        return True
    publicKeyBytes = bytes.fromhex(publicKeyHex)
    publicKey = load_pem_public_key(publicKeyBytes)
    try:
        publicKey.verify(
            bytes.fromhex(signature),
            message.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
       return False
   

def calculateTransactionHash(transferer, amount, transferee):
    """
    Calculate the hash of a transaction.

    Args:
        transferer (str): Hash of the user transferring the amount.
        amount (int): Amount to be transferred.
        transferee (str): Hash of the user receiving the amount.

    Returns:
        str: The calculated hash of the transaction.
    """
    transactionHash = hashlib.sha256()
    transactionHash.update(str(transferer).encode("utf-8") + str(amount).encode("utf-8") + str(transferee).encode("utf-8"))
    return transactionHash.hexdigest()

def main():
    """
    Main function to run the blockchain application.
    """
    blockchain = Blockchain()
    currentUsername = ""
    currentPassword = ""
    currentUser = None
    registeredUsers = []
    loggedIn = False
    currentTransaction = Transaction()

    while True:
        if not loggedIn:
            # use ansii codes (\x1b) to change the colour of the user interface.
            print()
            print("\x1b[32m[\x1b[31mL\x1b[32m]ogin / register")
            print("Get user [\x1b[31mb\x1b[32m]allance")
            print("[\x1b[31mQ\x1b[32m]uit\x1b[31m")
            userInput = input().lower()
            print("\x1b[0m")

            if userInput == 'l':
                currentUsername = input("Enter username: ")
                currentPassword = input("Enter password: ")

                # if user is already registered, set current user to user, otherwise, add a block that has their public key.
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
                print(f"{hash}'s ballance: {calculateBallance(hash, blockchain)}")

            elif userInput == 'q':
                break

            else:
                print("That is not a recognised command.")
                
        else:
            print()
            print(f"Logged in as: {currentUser.getHash()}")
            print("\x1b[32mGet my [\x1b[31mb\x1b[32m]allance")
            print("[\x1b[31mM\x1b[32m]ine")
            print("Make a [\x1b[31mt\x1b[32m]ransaction")
            print("[\x1b[31mD\x1b[32m]isplay blockchain")
            print("[\x1b[31mL\x1b[32m]ogout\x1b[31m")
            userInput = input().lower()
            print("\x1b[0m")

            if userInput == 'b':
                print(f"Your ballance: {calculateBallance(currentUser.getHash(), blockchain)}")

            elif userInput == 'm':
                blockchain.addBlock(currentTransaction.getData(), currentUser.getHash())
                currentTransaction = Transaction()

            elif userInput == 't':
                amount = int(input("Enter Amount: "))
                otherUser = input("Enter other user hash: ")
                transactionHash = calculateTransactionHash(currentUser.getHash(), amount, otherUser)
                currentTransaction.addTransaction(currentUser.getHash(), amount, otherUser, currentUser.signMessage(currentUsername, currentPassword, transactionHash), blockchain)
                print(f"Transfered {amount} to {otherUser}.")

            elif userInput == 'd':
                for i in range(blockchain.getBlock(-1).index + 1):
                    print(blockchain.getBlock(i))
                    print()

            elif userInput == 'l':
                loggedIn = False

            else:
                print("That command isn't recognised")

if __name__ == "__main__":
    main()