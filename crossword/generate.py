import sys
from collections import deque
from enum import Enum
from typing import Optional

# ============================================================================
# Core Crossword Structures
# ============================================================================

class Direction(Enum):
    ACROSS = "across"
    DOWN = "down"

    def __str__(self) -> str:
        return self.value


class Variable:
    def __init__(self, i: int, j: int, direction: Direction, length: int):
        self.i = i
        self.j = j
        self.direction = direction
        self.length = length
        
        # Pre-calculate cells spanned by this variable
        self.cells: list[tuple[int, int]] = []
        for k in range(self.length):
            self.cells.append((
                self.i + (k if self.direction == Direction.DOWN else 0),
                self.j + (k if self.direction == Direction.ACROSS else 0)
            ))

    # Python's hash and eq magic methods replace the C++20 <=> spaceship operator
    # to allow Variable instances to act seamlessly as dict keys and set items.
    def __hash__(self) -> int:
        return hash((self.i, self.j, self.direction, self.length))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Variable):
            return NotImplemented
        return (
            self.i == other.i and
            self.j == other.j and
            self.direction == other.direction and
            self.length == other.length
        )

    def __str__(self) -> str:
        return f"({self.i}, {self.j}) {self.direction} : {self.length}"

    def __repr__(self) -> str:
        return f"Variable({self.i}, {self.j}, Direction.{self.direction.name}, {self.length})"


class Crossword:
    def __init__(self, structure_file: str, words_file: str):
        self.height = 0
        self.width = 0
        self.structure: list[list[bool]] = []
        self.words: set[str] = set()
        self.variables: set[Variable] = set()
        self.overlaps: dict[tuple[Variable, Variable], Optional[tuple[int, int]]] = {}

        # 1. Parse puzzle structure
        try:
            with open(structure_file, "r", encoding="utf-8") as f:
                # splitlines() safely strips Windows CRLF (\r\n) boundaries automatically
                contents = f.splitlines()
        except OSError as e:
            raise RuntimeError(f"Could not open structure file: {e}")

        self.height = len(contents)
        self.width = max(len(line) for line in contents) if contents else 0

        self.structure = [[False] * self.width for _ in range(self.height)]
        for i in range(self.height):
            for j in range(self.width):
                if j < len(contents[i]) and contents[i][j] == '_':
                    self.structure[i][j] = True

        # 2. Load and normalize vocabulary dictionary
        try:
            with open(words_file, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip().upper()
                    if word:
                        self.words.add(word)
        except OSError as e:
            raise RuntimeError(f"Could not open words file: {e}")

        # 3. Detect grid variables
        for i in range(self.height):
            for j in range(self.width):
                if self.structure[i][j] and (i == 0 or not self.structure[i - 1][j]):
                    length = 1
                    k = i + 1
                    while k < self.height and self.structure[k][j]:
                        length += 1
                        k += 1
                    if length > 1:
                        self.variables.add(Variable(i, j, Direction.DOWN, length))

                if self.structure[i][j] and (j == 0 or not self.structure[i][j - 1]):
                    length = 1
                    k = j + 1
                    while k < self.width and self.structure[i][k]:
                        length += 1
                        k += 1
                    if length > 1:
                        self.variables.add(Variable(i, j, Direction.ACROSS, length))

        # 4. Map geometric line intersections
        for v1 in self.variables:
            for v2 in self.variables:
                if v1 == v2:
                    continue
                intersection = None
                for idx1, cell1 in enumerate(v1.cells):
                    for idx2, cell2 in enumerate(v2.cells):
                        if cell1 == cell2:
                            intersection = (idx1, idx2)
                            break
                    if intersection:
                        break
                self.overlaps[(v1, v2)] = intersection

    def neighbors(self, var: Variable) -> set[Variable]:
        result = set()
        for v in self.variables:
            if v == var:
                continue
            if self.overlaps.get((v, var)) is not None:
                result.add(v)
        return result


# ============================================================================
# Crossword Creator & Solver Logic
# ============================================================================

class CrosswordCreator:
    def __init__(self, crossword: Crossword):
        self.crossword = crossword
        # Track active domain pool for each grid entry variable
        self.domains = {var: set(crossword.words) for var in crossword.variables}

    def letter_grid(self, assignment: dict[Variable, str]) -> list[list[Optional[str]]]:
        letters: list[list[Optional[str]]] = [[None] * self.crossword.width for _ in range(self.crossword.height)]
        for variable, word in assignment.items():
            direction = variable.direction
            for k, char in enumerate(word):
                i = variable.i + (k if direction == Direction.DOWN else 0)
                j = variable.j + (k if direction == Direction.ACROSS else 0)
                letters[i][j] = char
        return letters

    def print(self, assignment: dict[Variable, str]) -> None:
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] if letters[i][j] is not None else " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment: dict[Variable, str], filename: str) -> None:
        print(f"[Info] Image saving triggered for '{filename}'.")

    def enforce_node_consistency(self) -> None:
        # Replaces std::erase_if with a clean Python set comprehension filtering pass
        for var, word_set in self.domains.items():
            self.domains[var] = {word for word in word_set if len(word) == var.length}

    def revise(self, x: Variable, y: Variable) -> bool:
        revision = False
        overlap = self.crossword.overlaps.get((x, y))
        
        if overlap is not None:
            idx_x, idx_y = overlap
            words_to_remove = []

            corresponding_chars = {y_word[idx_y] for y_word in self.domains[y]}

            for x_word in self.domains[x]:
                if x_word[idx_x] not in corresponding_chars:
                    words_to_remove.append(x_word)
                    revision = True

            for word in words_to_remove:
                self.domains[x].remove(word)
                
        return revision

    def ac3(self, arcs: Optional[deque[tuple[Variable, Variable]]] = None) -> bool:
        queue = deque()
        if arcs is None:
            for var1 in self.crossword.variables:
                for var2 in self.crossword.variables:
                    if var1 != var2:
                        queue.append((var1, var2))
        else:
            queue = deque(arcs)

        while queue:
            var1, var2 = queue.popleft()

            if self.revise(var1, var2):
                if not self.domains[var1]:
                    return False
                for var3 in self.crossword.neighbors(var1):
                    if var3 != var1 and var3 != var2:
                        queue.append((var3, var1))
        return True

    def assignment_complete(self, assignment: dict[Variable, str]) -> bool:
        return len(assignment) == len(self.crossword.variables)

    def consistent(self, assignment: dict[Variable, str]) -> bool:
        for var1, word1 in assignment.items():
            if len(word1) != var1.length:
                return False
            for var2 in self.crossword.neighbors(var1):
                overlap = self.crossword.overlaps.get((var1, var2))
                if overlap is not None and var2 in assignment:
                    idx1, idx2 = overlap
                    if word1[idx1] != assignment[var2][idx2]:
                        return False
        return True

    def order_domain_values(self, var: Variable, assignment: dict[Variable, str]) -> list[str]:
        domain = list(self.domains[var])
        neighborhood = self.crossword.neighbors(var)
        
        maps_values_to_numbers = {}
        for value in domain:
            count = 0
            for neighbor in neighborhood:
                if neighbor in assignment:
                    continue
                overlap = self.crossword.overlaps.get((var, neighbor))
                if overlap is not None:
                    idx1, idx2 = overlap
                    for word in self.domains[neighbor]:
                        if value[idx1] != word[idx2]:
                            count += 1
            maps_values_to_numbers[value] = count

        # Sort values based on the calculated Least Constraining Value (LCV) heuristic values
        domain.sort(key=lambda val: maps_values_to_numbers[val])
        return domain

    def select_unassigned_variable(self, assignment: dict[Variable, str]) -> Variable:
        unassigned = [var for var in self.domains if var not in assignment]

        # Explicitly matches C++ sorting logic:
        # Primary: Domain Size ascending (Minimum Remaining Values - MRV)
        # Secondary: Neighbor Count ascending (Degree Heuristic fallback tier)
        unassigned.sort(key=lambda v: (len(self.domains[v]), len(self.crossword.neighbors(v))))
        return unassigned[0]

    def backtrack(self, assignment: dict[Variable, str]) -> Optional[dict[Variable, str]]:
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            del assignment[var]
        return None

    def solve(self) -> Optional[dict[Variable, str]]:
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack({})


# ============================================================================
# Execution Core
# ============================================================================

def main() -> int:
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Usage: python generate.py structure words [output]", file=sys.stderr)
        return 1

    structure_file = sys.argv[1]
    words_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) == 4 else ""

    try:
        crossword = Crossword(structure_file, words_file)
        creator = CrosswordCreator(crossword)
        assignment = creator.solve()

        if assignment is None:
            print("No solution.")
        else:
            creator.print(assignment)
            if output_file:
                creator.save(assignment, output_file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
