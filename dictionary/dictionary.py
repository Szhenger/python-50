# Represents a node in the hash table.
# We use __slots__ for memory efficiency, mirroring a simple C++ struct.
class Node:
    __slots__ = ['word', 'next']
    
    def __init__(self, word: str, next_node: 'Node | None' = None):
        self.word = word
        self.next = next_node

# Number of buckets in the hash table
N = 28

# Hash table: each bucket owns its singly-linked chain
table: list[Node | None] = [None] * N

# Number of words currently loaded
word_count = 0

def hash_word(word: str) -> int:
    """Hashes word to a bucket index."""
    total = sum(ord(c.lower()) for c in word)
    return total % N

def check(word: str) -> bool:
    """Returns True if word is in the dictionary, else False (case-insensitive)."""
    target = word.lower()
    node = table[hash_word(word)]
    
    while node is not None:
        if node.word.lower() == target:
            return True
        node = node.next
        
    return False

def load(dictionary_file: str) -> bool:
    """Loads dictionary into memory; returns True on success, False on failure."""
    global word_count
    try:
        with open(dictionary_file, 'r', encoding='utf-8') as f:
            for line in f:
                # file >> word skips all whitespace in C++
                for word in line.split():
                    bucket = hash_word(word)
                    # Prepend to chain
                    table[bucket] = Node(word, table[bucket])
                    word_count += 1
        return True
    except IOError:
        return False

def size() -> int:
    """Returns number of words loaded, or 0 if not yet loaded."""
    return word_count

def unload() -> bool:
    """
    Unloads the dictionary from memory; returns True.
    Dropping references allows Python's garbage collector to free the nodes.
    """
    global word_count, table
    table = [None] * N
    word_count = 0
    return True
