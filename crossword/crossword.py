import typing

class Variable:
    """
    Represents a slot in the crossword puzzle where a word can be placed.
    """
    def __init__(self, i: int, j: int, direction: str, length: int):
        self.i = i
        self.j = j
        self.direction = direction
        self.length = length
        self.cells = []
        
        # Calculate all grid coordinate pairs that this variable spans
        for k in range(self.length):
            self.cells.append(
                (self.i + (k if self.direction == "down" else 0),
                 self.j + (k if self.direction == "across" else 0))
            )

    # Replaces the C++ <=> and == operators. 
    # Python relies on these methods to compare objects in sets or as dictionary keys.
    def __hash__(self):
        return hash((self.i, self.j, self.direction, self.length))

    def __eq__(self, other):
        return (
            (self.i == other.i) and
            (self.j == other.j) and
            (self.direction == other.direction) and
            (self.length == other.length)
        )

    # Replaces the C++ to_string() and to_repr() methods
    def __str__(self):
        return f"({self.i}, {self.j}) {self.direction} : {self.length}"

    def __repr__(self):
        return f"Variable({self.i}, {self.j}, {self.direction}, {self.length})"


class Crossword:
    """
    Parses a crossword grid structure and vocabulary list.
    """
    def __init__(self, structure_file: str, words_file: str):
        # 1. Determine structure of crossword
        with open(structure_file, "r") as f:
            # .splitlines() automatically handles carriage returns and newlines cleanly
            contents = f.read().splitlines()
            
            # Python's built-in max() easily finds the length of the longest row
            self.height = len(contents)
            self.width = max(len(line) for line in contents)

            self.structure = []
            for i in range(self.height):
                row = []
                for j in range(self.width):
                    if j >= len(contents[i]):
                        row.append(False)
                    elif contents[i][j] == "_":
                        row.append(True)
                    else:
                        row.append(False)
                self.structure.append(row)

        # 2. Save vocabulary list
        with open(words_file, "r") as f:
            self.words = set(f.read().upper().splitlines())

        # 3. Determine variable set
        self.variables = set()
        for i in range(self.height):
            for j in range(self.width):

                # Vertical words
                starts_word_down = (
                    self.structure[i][j]
                    and (i == 0 or not self.structure[i - 1][j])
                )
                if starts_word_down:
                    length = 1
                    for k in range(i + 1, self.height):
                        if self.structure[k][j]:
                            length += 1
                        else:
                            break
                    if length > 1:
                        self.variables.add(Variable(
                            i=i, j=j,
                            direction="down",
                            length=length
                        ))

                # Horizontal words
                starts_word_across = (
                    self.structure[i][j]
                    and (j == 0 or not self.structure[i][j - 1])
                )
                if starts_word_across:
                    length = 1
                    for k in range(j + 1, self.width):
                        if self.structure[i][k]:
                            length += 1
                        else:
                            break
                    if length > 1:
                        self.variables.add(Variable(
                            i=i, j=j,
                            direction="across",
                            length=length
                        ))

        # 4. Compute overlaps for each word
        # In Python, we represent intersections safely using either a Tuple or None
        self.overlaps: dict[tuple[Variable, Variable], typing.Optional[tuple[int, int]]] = {}
        
        for v1 in self.variables:
            for v2 in self.variables:
                if v1 == v2:
                    continue
                
                # Default intersection state
                self.overlaps[v1, v2] = None
                
                # Check cross-reference of coordinate pairs
                for idx1, cell1 in enumerate(v1.cells):
                    for idx2, cell2 in enumerate(v2.cells):
                        if cell1 == cell2:
                            self.overlaps[v1, v2] = (idx1, idx2)
                            break
                            
                    # Break outer loop if an overlap was already found
                    if self.overlaps[v1, v2] is not None:
                        break

    def neighbors(self, var: Variable) -> set[Variable]:
        """Given a variable, return set of overlapping variables."""
        return set(
            v for v in self.variables
            if v != var and self.overlaps[v, var] is not None
        )
