from user import User
from blockchain import Blockchain
from config import (calculateBallance, calculateTransactionHash)
from transaction import Transaction

DIFFICULTY = 4
# Payment per block mined. Designed so that if difficulty increases by 1, currency / second mined /= 2
PAYMENT_PER_MINED = 8 ** (DIFFICULTY)

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