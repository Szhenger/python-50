"""
Implements a dictionary's functionality
Python translation of dictionary.cpp
"""

import os

# ── internal linkage ────────────────────────────────────────────────────────

class Node:
    """
    Represents a node in the hash table.
    Using __slots__ prevents Python from creating a dynamic __dict__ for every 
    instance, saving memory and mimicking the strict memory layout of a C++ struct.
    """
    __slots__ = ['word', 'next']
    
    def __init__(self, word: str, next_node: 'Node | None' = None):
        self.word = word
        self.next = next_node

# Number of buckets in the hash table
N: int = 28

# Hash table: each bucket owns its singly-linked chain.
# Python lists hold references to objects, acting exactly like an array of pointers.
table: list[Node | None] = [None] * N

# Number of words currently loaded
word_count: int = 0

# ── public API ──────────────────────────────────────────────────────────────

def hash_word(word: str) -> int:
    """
    Hashes word to a bucket index.
    (Named 'hash_word' instead of 'hash' to avoid shadowing Python's built-in hash())
    """
    total = sum(ord(c.lower()) for c in word)
    return total % N

def check(word: str) -> bool:
    """
    Returns True if word is in the dictionary, else False.
    Comparison is case-insensitive.
    """
    bucket = hash_word(word)
    current = table[bucket]
    word_lower = word.lower()
    
    # Traverse the linked list at this bucket
    while current is not None:
        if current.word.lower() == word_lower:
            return True
        current = current.next
        
    return False

def load(dictionary: str) -> bool:
    """
    Loads dictionary into memory; returns True on success, False on failure.
    """
    global word_count, table
    
    if not os.path.isfile(dictionary):
        return False
        
    try:
        with open(dictionary, 'r', encoding='utf-8') as file:
            for line in file:
                # .split() handles arbitrary whitespace, mirroring C++ `file >> word`
                for word in line.split():
                    bucket = hash_word(word)
                    
                    # Prepend to chain: create a new node pointing to the current head,
                    # then update the head of the bucket to this new node.
                    new_node = Node(word, table[bucket])
                    table[bucket] = new_node
                    
                    word_count += 1
        return True
    except OSError:
        return False

def size() -> int:
    """
    Returns number of words loaded, or 0 if not yet loaded.
    """
    return word_count

def unload() -> bool:
    """
    Unloads the dictionary from memory; returns True.
    Resetting the array clears the root references. Python's Garbage Collector 
    automatically reclaims all the now-orphaned linked-list chains.
    """
    global table, word_count
    
    table = [None] * N
    word_count = 0
    return True
