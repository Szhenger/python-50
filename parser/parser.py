import sys
import string
from dataclasses import dataclass, field

# --- Grammars ---

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
NP -> N | Det N | Det Adj N | Det Adj Adj N | NP PP
VP -> V | VP Adv | Adv VP | VP Conj VP | VP NP | VP PP
PP -> P NP
"""

# --- Data Structures ---

@dataclass
class Tree:
    label: str
    children: list['Tree'] = field(default_factory=list)
    word: str = ""

    def is_leaf(self) -> bool:
        return len(self.children) == 0 and bool(self.word)

    # Note: @dataclass automatically generates an __eq__ method 
    # that recursively compares fields, perfectly mirroring the C++ operator==.

@dataclass
class Rule:
    lhs: str
    rhs: list[str]
    is_terminal: bool


# --- NLTK Helper Mimics ---

def pretty_print(tree: Tree, depth: int = 0) -> None:
    indent = " " * (depth * 4)
    if tree.is_leaf():
        print(f"{indent}{tree.word}")
    else:
        print(f"{indent}{tree.label}(")
        for child in tree.children:
            pretty_print(child, depth + 1)
        print(f"{indent})")

def flatten(t: Tree) -> list[str]:
    if t.is_leaf():
        return [t.word]
    res = []
    for c in t.children:
        res.extend(flatten(c))
    return res

def get_subtrees(t: Tree, result: list[Tree]) -> None:
    result.append(t)
    for c in t.children:
        get_subtrees(c, result)


# --- Core Logic ---

def parse_cfg(terminals_str: str, nonterminals_str: str) -> list[Rule]:
    rules = []
    
    def process_block(block: str, is_term: bool):
        for line in block.splitlines():
            line = line.strip()
            if not line or "->" not in line:
                continue
            
            lhs, rhs_part = line.split("->", 1)
            lhs = lhs.strip()
            
            for option in rhs_part.split('|'):
                tokens = option.split()
                if is_term:
                    # Strip out quote characters for terminal words
                    tokens = [t.replace('"', '') for t in tokens]
                if tokens:
                    rules.append(Rule(lhs=lhs, rhs=tokens, is_terminal=is_term))
                    
    process_block(nonterminals_str, False)
    process_block(terminals_str, True)
    return rules

def preprocess(sentence: str) -> list[str]:
    words = []
    padded = ""
    
    # NLTK tokenizes punctuation as separate words.
    for c in sentence:
        if c in string.punctuation:
            padded += f" {c} "
        else:
            padded += c
            
    for token in padded.split():
        # Lowercase extraction and alphabetic validation
        lower_word = "".join(c.lower() for c in token)
        if any(c.isalpha() for c in token):
            words.append(lower_word)
            
    return words

def np_chunk(tree: Tree) -> list[Tree]:
    chunks = []
    all_subtrees = []
    get_subtrees(tree, all_subtrees)

    for parent in all_subtrees:
        if parent.label == "NP":
            is_chunk = True
            child_subtrees = []
            for child in parent.children:
                get_subtrees(child, child_subtrees)
                
            for desc in child_subtrees:
                if desc.label == "NP":
                    is_chunk = False
                    break
                    
            if is_chunk:
                chunks.append(parent)
                
    return chunks


# Emulates NLTK ChartParser algorithm (Dynamic Programming)
class ChartParser:
    def __init__(self, rules: list[Rule]):
        self.rules = rules

    def _find_matches(self, chart: list[list[list[Tree]]], i: int, j: int, 
                      rhs: list[str], rhs_idx: int, current_children: list[Tree], 
                      results: list[list[Tree]]) -> None:
        if rhs_idx == len(rhs):
            if i == j:
                # Append a copy of the list so subsequent pops don't mutate it
                results.append(list(current_children))
            return
        if i == j:
            return

        for k in range(i + 1, j + 1):
            for t in chart[i][k]:
                if t.label == rhs[rhs_idx]:
                    current_children.append(t)
                    self._find_matches(chart, k, j, rhs, rhs_idx + 1, current_children, results)
                    current_children.pop()

    def parse(self, words: list[str]) -> list[Tree]:
        n = len(words)
        if n == 0:
            return []

        # chart[i][j] stores all subtrees spanning from word index i to j
        chart = [[[] for _ in range(n + 1)] for _ in range(n)]

        # 1. Initialize terminal leaves
        for i in range(n):
            leaf = Tree(label="", children=[], word=words[i])
            for r in self.rules:
                if r.is_terminal and len(r.rhs) == 1 and r.rhs[0] == words[i]:
                    chart[i][i+1].append(Tree(label=r.lhs, children=[leaf], word=""))

        # 2. Bottom-up parsing spans
        for length in range(1, n + 1):
            for i in range(n - length + 1):
                j = i + length
                added = True
                
                # Allow unary rules to exhaustively evaluate
                while added:
                    added = False
                    for r in self.rules:
                        if r.is_terminal:
                            continue

                        results = []
                        self._find_matches(chart, i, j, r.rhs, 0, [], results)

                        for children in results:
                            new_tree = Tree(label=r.lhs, children=children, word="")
                            # Add if not a duplicate
                            if new_tree not in chart[i][j]:
                                chart[i][j].append(new_tree)
                                added = True

        # Extract valid start symbols ("S") spanning the entire sentence
        parsed_trees = [t for t in chart[0][n] if t.label == "S"]
        return parsed_trees


# --- Execution ---

def main() -> None:
    if len(sys.argv) == 2:
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                s = f.read()
        except IOError:
            print("Could not open file.", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            s = input("Sentence: ")
        except EOFError:
            return

    words = preprocess(s)
    rules = parse_cfg(TERMINALS, NONTERMINALS)
    parser = ChartParser(rules)
    
    trees = parser.parse(words)

    if not trees:
        print("Could not parse sentence.")
        return

    for tree in trees:
        pretty_print(tree)

        print("\nNoun Phrase Chunks")
        for np in np_chunk(tree):
            flat = flatten(np)
            print(" ".join(flat))
        print()  # Space out multiple parsed trees

if __name__ == "__main__":
    main()
