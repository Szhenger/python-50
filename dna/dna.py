import csv
import sys

def longest_match(sequence: str, subsequence: str) -> int:
    """Returns the length of the longest consecutive run of subsequence in sequence."""
    longest_run = 0
    subseq_len = len(subsequence)
    seq_len = len(sequence)

    for i in range(seq_len):
        count = 0
        while True:
            start = i + count * subseq_len
            end = start + subseq_len
            if end <= seq_len and sequence[start:end] == subsequence:
                count += 1
            else:
                break
        longest_run = max(longest_run, count)
    return longest_run

def main():
    if len(sys.argv) != 3:
        print("Usage: python dna.py data.csv sequence.txt", file=sys.stderr)
        sys.exit(1)

    # Read database file
    database = []
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert STR counts to integers, keep name as string
            for key, value in row.items():
                if key != "name":
                    row[key] = int(value)
            database.append(row)

    # Read DNA sequence
    with open(sys.argv[2], "r", encoding="utf-8") as f:
        sequence = f.read().strip()

    # Find longest match of each STR in DNA sequence
    # Headers are all keys except "name"
    str_subsequences = [key for key in database[0].keys() if key != "name"]
    sequence_data = {sub: longest_match(sequence, sub) for sub in str_subsequences}

    # Check database for matching profiles
    for person in database:
        if all(person[sub] == sequence_data[sub] for sub in str_subsequences):
            print(person["name"])
            return

    print("No match")

if __name__ == "__main__":
    main()
