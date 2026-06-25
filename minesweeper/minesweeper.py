import random

class Minesweeper:
    def __init__(self, height: int = 8, width: int = 8, num_mines: int = 8):
        self.height = height
        self.width = width
        self.mines: set[tuple[int, int]] = set()
        self.mines_found: set[tuple[int, int]] = set()

        # Initialize an empty field with no mines
        self.board = [[False for _ in range(width)] for _ in range(height)]

        # Add mines randomly
        while len(self.mines) < num_mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

    def print(self) -> None:
        """Prints a text-based representation of the board."""
        for i in range(self.height):
            print("--" * self.width)
            row_display = []
            for j in range(self.width):
                if self.board[i][j]:
                    row_display.append("|X")
                else:
                    row_display.append("| ")
            print("".join(row_display) + "|")
        print("--" * self.width)

    def is_mine(self, cell: tuple[int, int]) -> bool:
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell: tuple[int, int]) -> int:
        """Returns the number of mines in neighboring cells."""
        count = 0
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1
        return count

    def won(self) -> bool:
        return self.mines_found == self.mines


class Sentence:
    def __init__(self, cells: set[tuple[int, int]], count: int):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Sentence):
            return False
        return self.cells == other.cells and self.count == other.count

    def __str__(self) -> str:
        return f"{self.cells} = {self.count}"

    def known_mines(self) -> set[tuple[int, int]]:
        """Returns the set of all cells in self.cells known to be mines."""
        if len(self.cells) == self.count:
            return self.cells.copy()
        return set()

    def known_safes(self) -> set[tuple[int, int]]:
        """Returns the set of all cells in self.cells known to be safe."""
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_mine(self, cell: tuple[int, int]) -> None:
        """Updates internal knowledge given the fact that a cell is a mine."""
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell: tuple[int, int]) -> None:
        """Updates internal knowledge given the fact that a cell is safe."""
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI:
    def __init__(self, height: int = 8, width: int = 8):
        self.height = height
        self.width = width
        self.moves_made: set[tuple[int, int]] = set()
        self.mines: set[tuple[int, int]] = set()
        self.safes: set[tuple[int, int]] = set()
        self.knowledge: list[Sentence] = []

    def mark_mine(self, cell: tuple[int, int]) -> None:
        """Marks a cell as a mine, and updates all knowledge."""
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell: tuple[int, int]) -> None:
        """Marks a cell as safe, and updates all knowledge."""
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell: tuple[int, int], count: int) -> None:
        """Updates knowledge base when the board reveals how many mines are nearby a safe cell."""
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Gather unresolved neighboring cells
        nearby_cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if 0 <= i < self.height and 0 <= j < self.width and (i, j) != cell:
                    nearby_cells.add((i, j))

        unresolved_cells = set()
        for c in nearby_cells:
            if c in self.safes:
                continue
            if c in self.mines:
                count -= 1
                continue
            unresolved_cells.add(c)

        self.knowledge.append(Sentence(unresolved_cells, count))

        # Repeatedly check for new safes/mines until no updates can be made
        def update_knowledge():
            changed = True
            while changed:
                changed = False
                for sentence in self.knowledge:
                    # Update safes
                    for safe_cell in sentence.known_safes():
                        if safe_cell not in self.safes:
                            self.mark_safe(safe_cell)
                            changed = True
                    # Update mines
                    for mine_cell in sentence.known_mines():
                        if mine_cell not in self.mines:
                            self.mark_mine(mine_cell)
                            changed = True

        update_knowledge()

        # Infer new sentences based on subset evaluation
        new_sentences = []
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 == sentence2:
                    continue

                # Python's strictly greater-than (>) operator on sets natively checks for a strict superset
                # This perfectly replaces C++'s std::ranges::includes alongside a size check.
                if sentence1.cells > sentence2.cells:
                    diff_cells = sentence1.cells - sentence2.cells
                    diff_count = sentence1.count - sentence2.count
                    
                    if diff_count >= 0:
                        newer_sentence = Sentence(diff_cells, diff_count)
                        if newer_sentence not in self.knowledge and newer_sentence not in new_sentences:
                            new_sentences.append(newer_sentence)

        # Append newly inferred knowledge
        self.knowledge.extend(new_sentences)
        update_knowledge()

    def make_safe_move(self) -> tuple[int, int] | None:
        """Returns a known safe move that hasn't been played, or None if none exist."""
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self) -> tuple[int, int] | None:
        """Returns a random valid move, or None if no valid moves exist."""
        max_attempts = self.height * self.width * 2
        
        while max_attempts > 0:
            random_move = (random.randrange(self.height), random.randrange(self.width))
            if random_move not in self.moves_made and random_move not in self.mines:
                return random_move
            max_attempts -= 1
            
        return None
