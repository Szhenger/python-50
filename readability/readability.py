import math

def count_letters(s: str) -> int:
    """Counts alphabetic characters in a string."""
    return sum(1 for c in s if c.isalpha())

def count_words(s: str) -> int:
    """Counts words based on whitespace separation."""
    words = s.split()
    return len(words)

def count_sentences(s: str) -> int:
    """Counts terminal punctuation marks."""
    return sum(1 for c in s if c in {'.', '!', '?'})

def compute_index(letter_c: int, word_c: int, sentence_c: int) -> int:
    """Computes the Coleman-Liau index."""
    if word_c == 0:
        return 0
    
    L = (letter_c / word_c) * 100.0
    S = (sentence_c / word_c) * 100.0
    
    index = 0.0588 * L - 0.296 * S - 15.8
    return round(index)

def main():
    text = input("Text: ")

    letter_count = count_letters(text)
    word_count = count_words(text)
    sentence_count = count_sentences(text)

    grade = compute_index(letter_count, word_count, sentence_count)

    if grade < 1:
        print("Before Grade 1")
    elif grade >= 16:
        print("Grade 16+")
    else:
        print(f"Grade {grade}")

if __name__ == "__main__":
    main()
