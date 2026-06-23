def main() -> None:
    # Get number
    number = get_long("Number: ")

    # Initialize checksum, length, and startingdigits
    checksum = 0
    length = 0
    startingdigits = 0

    # Compute checksum, length, and startingdigits of number
    while number > 0:
        if startingdigits == 0 and number < 100:
            startingdigits = number
            
        digit = number % 10
        number = number // 10  # Python requires // for integer division
        length += 1
        
        if length % 2 == 0:
            doubled = 2 * digit
            if doubled > 9:
                checksum += (doubled // 10) + (doubled % 10)
            else:
                checksum += doubled
        else:
            checksum += digit

    # Check number and bank
    if checksum % 10 != 0:
        print("INVALID")
    elif length in (13, 16):
        if length == 16 and 50 < startingdigits < 56:
            print("MASTERCARD")
        elif startingdigits // 10 == 4:
            print("VISA")
        else:
            print("INVALID")
    elif length == 15:
        if startingdigits in (34, 37):
            print("AMEX")
        else:
            print("INVALID")
    else:
        print("INVALID")


def get_long(prompt: str) -> int:
    """Safely gets an integer from the user, rejecting bad input."""
    while True:
        try:
            # Attempt to read and parse the input as an integer
            return int(input(prompt))
        except ValueError:
            # If the user typed non-numeric characters, catch the error and repeat
            pass


if __name__ == "__main__":
    main()
