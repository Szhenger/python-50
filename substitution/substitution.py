import sys

def main() -> int:
    # Checks whether key is valid
    if check_key():
        # Get plaintext from user
        plaintext = input("plaintext:  ")

        # Print ciphertext
        print_cipher_text(plaintext, sys.argv[1])

        return 0
    else:
        # Return error otherwise
        return 1

def check_key() -> bool:
    """Validates the command line argument cipher key."""
    # sys.argv is the Python equivalent of argc/argv
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} key")
        return False

    key = sys.argv[1]

    if len(key) != 26:
        print("Key must contain 26 characters.")
        return False

    if not key.isalpha():
        print("Key must contain only letters.")
        return False

    # A set automatically removes duplicates. If we convert the key to lowercase
    # and turn it into a set, it should still have 26 elements if all are unique.
    if len(set(key.lower())) != 26:
        print("Key must contain each letter exactly once.")
        return False

    return True

def print_cipher_text(text: str, cipher: str) -> None:
    """Encrypts and prints the ciphertext."""
    # Python strings are immutable, so we build a list of characters 
    # and join them at the end, which is more memory efficient.
    result = []
    
    for c in text:
        if c.isalpha():
            if c.islower():
                # ord() gets the ASCII integer value of a character
                index = ord(c) - ord('a')
                result.append(cipher[index].lower())
            else:
                index = ord(c) - ord('A')
                result.append(cipher[index].upper())
        else:
            result.append(c)
            
    # Print the fully built string at once by joining the list
    print(f"ciphertext: {''.join(result)}")


if __name__ == "__main__":
    # sys.exit passes the return value of main() to the operating system
    sys.exit(main())
