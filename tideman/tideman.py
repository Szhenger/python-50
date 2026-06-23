import sys
from dataclasses import dataclass

# Max number of candidates
MAX = 9

# In Python 3, a dataclass is the perfect equivalent to a C++ struct.
# It automatically generates the initialization code behind the scenes.
@dataclass
class Pair:
    winner: int
    loser: int

# Global variables
# We initialize these as empty lists and will dynamically size them in main()
preferences: list[list[int]] = []
locked: list[list[bool]] = []
candidates: list[str] = []
pairs: list[Pair] = []

def main() -> int:
    global preferences, locked, candidates
    
    # Check for invalid usage
    if len(sys.argv) < 2:
        print("Usage: tideman [candidate ...]")
        return 1

    # Populate list of candidates
    candidates = sys.argv[1:]
    candidate_count = len(candidates)

    if candidate_count > MAX:
        print(f"Maximum number of candidates is {MAX}")
        return 2

    # Dynamically build the 2D matrices based on the actual number of candidates.
    # This replaces the need to pre-allocate a massive 9x9 grid of zeroes!
    preferences = [[0] * candidate_count for _ in range(candidate_count)]
    locked = [[False] * candidate_count for _ in range(candidate_count)]

    voter_count = get_voter_count()

    # Query for votes
    for _ in range(voter_count):
        # Initialize a list of zeroes for the voter's ranks
        ranks = [0] * candidate_count

        # Query for each rank
        for j in range(candidate_count):
            name = input(f"Rank {j + 1}: ").strip()

            if not vote(j, name, ranks):
                print("Invalid vote.")
                return 3

        record_preferences(ranks)
        print()  # Prints a blank line
        
    add_pairs()
    sort_pairs()
    lock_pairs()
    print_winner()
    
    return 0

def get_voter_count() -> int:
    """Safely grabs a positive integer for the voter count."""
    while True:
        try:
            count = int(input("Number of voters: "))
            if count > 0:
                return count
        except ValueError:
            pass

def vote(rank: int, name: str, ranks: list[int]) -> bool:
    """Update ranks given a new vote."""
    # enumerate() gives us both the index (i) and the value (candidate) 
    for i, candidate in enumerate(candidates):
        if name == candidate:
            ranks[rank] = i
            return True
    return False

def record_preferences(ranks: list[int]) -> None:
    """Update preferences given one voter's ranks."""
    candidate_count = len(candidates)
    for i in range(candidate_count):
        for j in range(i + 1, candidate_count):
            preferences[ranks[i]][ranks[j]] += 1

def add_pairs() -> None:
    """Record pairs of candidates where one is preferred over the other."""
    candidate_count = len(candidates)
    for i in range(candidate_count):
        for j in range(i, candidate_count):
            if preferences[i][j] > preferences[j][i]:
                pairs.append(Pair(winner=i, loser=j))
            elif preferences[i][j] < preferences[j][i]:
                pairs.append(Pair(winner=j, loser=i))

def sort_pairs() -> None:
    """Sort pairs in decreasing order by strength of victory."""
    # We use a lambda function to tell Python exactly which value to sort by.
    # reverse=True ensures it sorts in descending order (strongest victory first).
    pairs.sort(
        key=lambda p: preferences[p.winner][p.loser], 
        reverse=True
    )

def lock_pairs() -> None:
    """Lock pairs into the candidate graph in order, without creating cycles."""
    for pair in pairs:
        if not makes_cycle(pair.winner, pair.loser):
            locked[pair.winner][pair.loser] = True

def makes_cycle(start: int, end: int) -> bool:
    """Recursively checks whether locking a pair makes a cycle."""
    if start == end:
        return True
        
    for i in range(len(candidates)):
        if locked[end][i]:
            if makes_cycle(start, i):
                return True
                
    return False

def print_winner() -> None:
    """Print the winner of the election."""
    candidate_count = len(candidates)
    
    # Initialize edge counts to 0
    candidate_edges = [0] * candidate_count

    # Tally up the incoming edges for everyone
    for i in range(candidate_count):
        for j in range(candidate_count):
            if locked[j][i]:
                candidate_edges[i] += 1

    # Find the minimum number of incoming edges
    min_edges = min(candidate_edges)

    # Print the candidate with the minimum incoming edges (the source of the graph)
    for i in range(candidate_count):
        if candidate_edges[i] == min_edges:
            print(candidates[i])
            break

if __name__ == "__main__":
    sys.exit(main())
