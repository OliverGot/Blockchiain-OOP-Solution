from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key, Encoding, PrivateFormat, PublicFormat, NoEncryption
)

def generate_key_pair():
    # Generate a private key for use in the signing
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key

def sign_message(private_key, message):
    # Sign the message with the private key
    signature = private_key.sign(
        message.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify_signature(public_key, message, signature):
    # Verify the signature with the public key
    try:
        public_key.verify(
            signature,
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        return False

def main():
    # Generate keys
    private_key, public_key = generate_key_pair()
    
    # Serialize keys for storage or transmission
    private_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo
    )

    print("Private Key:")
    print(private_pem.decode('utf-8'))

    print("Public Key (PEM):")
    print(public_pem.decode('utf-8'))

    # Convert public key PEM to hex
    hex_public_key = public_pem.hex()
    print("Public Key (Hex):")
    print(hex_public_key)

    # Sign a message
    message = "This is a secret message."
    signature = sign_message(private_key, message)
    
    print("Message:")
    print(message)
    
    hex_signature = signature.hex()
    print("Signature (Hex):")
    print(hex_signature)

    # Convert hex public key back to bytes and then to public key object
    public_key_bytes = bytes.fromhex(hex_public_key)
    public_key = load_pem_public_key(public_key_bytes)

    # Convert hex signature back to bytes
    signature_from_hex = bytes.fromhex(hex_signature)

    # Verify the message
    is_valid = verify_signature(public_key, message, signature_from_hex)
    print(f"Signature valid: {is_valid}")

if __name__ == "__main__":
    main()
