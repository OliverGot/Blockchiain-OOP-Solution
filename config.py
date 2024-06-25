import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key, Encoding, PublicFormat,
)

DIFFICULTY = 4
PAYMENT_PER_MINED = 8 ** (DIFFICULTY)

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