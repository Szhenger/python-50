def main() -> None:
    # Get height of the desired pyramid between 1 and 8
    height = get_height()

    # Prints the desired pyramid
    make_pyramid(height)

def get_height() -> int:
    """Returns an integer between 1 and 8."""
    while True:
        try:
            # Read input and attempt to parse it as an integer
            user_input = int(input("Height: "))
            
            # Check if it falls within our desired bounds
            if 1 <= user_input <= 8:
                return user_input
                
        except ValueError:
            # If parsing fails (e.g., user typed "apple"), catch the error
            # 'pass' just tells Python to do nothing and let the loop repeat
            pass

def make_pyramid(n: int) -> None:
    """Prints the desired double pyramid of height n."""
    for i in range(n):
        # Calculate the number of spaces and hashes for the current row
        spaces = " " * (n - 1 - i)
        hashes = "#" * (i + 1)
        
        # Print left spaces, left hashes, the 2-space gap, and right hashes
        print(f"{spaces}{hashes}  {hashes}")

if __name__ == "__main__":
    main()
