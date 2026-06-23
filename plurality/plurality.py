import sys

# Max number of candidates
MAX = 9

def main() -> int:
    # Check for invalid usage
    if len(sys.argv) < 2:
        print("Usage: plurality [candidate ...]")
        return 1

    candidate_count = len(sys.argv) - 1
    if candidate_count > MAX:
        print(f"Maximum number of candidates is {MAX}")
        return 2

    # A dictionary maps candidate names directly to their vote counts.
    # This completely eliminates the need for the C++ Candidate struct!
    candidates = {name: 0 for name in sys.argv[1:]}

    voter_count = get_voter_count()

    # Loop over all voters
    # We use '_' as the loop variable since we don't actually need the index number
    for _ in range(voter_count):
        # .strip() cleanly removes any accidental whitespace around the user's input
        name = input("Vote: ").strip()

        # Check for invalid vote
        if not vote(candidates, name):
            print("Invalid vote.")

    # Display winner(s) of the election
    print_winner(candidates)
    return 0

def get_voter_count() -> int:
    """Safely grabs a positive integer for voter count."""
    while True:
        try:
            count = int(input("Number of voters: "))
            if count > 0:
                return count
        except ValueError:
            # Ignore non-integer inputs and repeat the loop
            pass

def vote(candidates: dict[str, int], name: str) -> bool:
    """Update vote totals given a new vote."""
    # The 'in' keyword checks if the name exists as a key in our dictionary
    if name in candidates:
        candidates[name] += 1
        return True
    return False

def print_winner(candidates: dict[str, int]) -> None:
    """Print the winner (or winners) of the election."""
    # Step 1: Find the maximum number of votes using Python's built-in max() function
    max_votes = max(candidates.values())

    # Step 2: Print the name of any candidate who matches that maximum amount
    for name, votes in candidates.items():
        if votes == max_votes:
            print(name)

if __name__ == "__main__":
    sys.exit(main())
