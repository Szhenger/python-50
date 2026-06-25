import copy
import math
from typing import Final, TypeAlias

# Constants
X: Final = "X"
O: Final = "O"
EMPTY: Final = None

# Type Aliases
Board: TypeAlias = list[list[str | None]]
Action: TypeAlias = tuple[int, int]

def initial_state() -> Board:
    return [[EMPTY for _ in range(3)] for _ in range(3)]

def player(board: Board) -> str | None:
    if terminal(board):
        return None
    
    # Flatten board and count pieces
    flat = [cell for row in board for cell in row]
    x_count = flat.count(X)
    o_count = flat.count(O)
    
    return X if x_count == o_count else O

def actions(board: Board) -> list[Action]:
    if terminal(board):
        return []
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == EMPTY]

def result(board: Board, action: Action) -> Board:
    if action not in actions(board):
        raise ValueError("Invalid action")
    
    new_board = copy.deepcopy(board)
    current_player = player(board)
    if current_player:
        new_board[action[0]][action[1]] = current_player
    return new_board

def winner(board: Board) -> str | None:
    # Check rows, columns, and diagonals
    lines = (
        board +  # Rows
        [[board[r][c] for r in range(3)] for c in range(3)] + # Cols
        [[board[i][i] for i in range(3)], [board[i][2-i] for i in range(3)]] # Diags
    )
    
    for line in lines:
        if line[0] is not None and line[0] == line[1] == line[2]:
            return line[0]
    return None

def terminal(board: Board) -> bool:
    return winner(board) is not None or all(cell is not None for row in board for cell in row)

def utility(board: Board) -> int:
    match winner(board):
        case "X": return 1
        case "O": return -1
        case _: return 0

def minimax(board: Board) -> Action | None:
    if terminal(board):
        return None
    
    current_player = player(board)
    possible_moves = actions(board)

    def play(b: Board) -> int:
        if terminal(b):
            return utility(b)
        
        move_values = [play(result(b, move)) for move in actions(b)]
        return max(move_values) if player(b) == X else min(move_values)

    # Return the action leading to the optimal utility score
    if current_player == X:
        return max(possible_moves, key=lambda m: play(result(board, m)))
    else:
        return min(possible_moves, key=lambda m: play(result(board, m)))
