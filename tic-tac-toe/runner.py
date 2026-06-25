import pygame
import sys
import copy
import math
from typing import List, Tuple, Optional

# --- Constants ---
EMPTY, X, O = 0, 1, 2
WIDTH, HEIGHT = 600, 400
WHITE, BLACK = (255, 255, 255), (0, 0, 0)

# --- Game Logic ---
def initial_state() -> List[List[int]]:
    return [[EMPTY for _ in range(3)] for _ in range(3)]

def player(board: List[List[int]]) -> int:
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)
    return X if x_count <= o_count else O

def winner(board: List[List[int]]) -> int:
    for i in range(3):
        if board[i][0] != EMPTY and board[i][0] == board[i][1] == board[i][2]: return board[i][0]
        if board[0][i] != EMPTY and board[0][i] == board[1][i] == board[2][i]: return board[0][i]
    if board[0][0] != EMPTY and board[0][0] == board[1][1] == board[2][2]: return board[0][0]
    if board[0][2] != EMPTY and board[0][2] == board[1][1] == board[2][0]: return board[0][2]
    return EMPTY

def terminal(board: List[List[int]]) -> bool:
    return winner(board) != EMPTY or all(cell != EMPTY for row in board for cell in row)

def utility(board: List[List[int]]) -> int:
    w = winner(board)
    return 1 if w == X else -1 if w == O else 0

def result(board: List[List[int]], move: Tuple[int, int]) -> List[List[int]]:
    if board[move[0]][move[1]] != EMPTY: raise ValueError("Invalid move")
    new_board = copy.deepcopy(board)
    new_board[move[0]][move[1]] = player(board)
    return new_board

def minimax(board: List[List[int]]) -> Tuple[int, int]:
    if terminal(board): return (-1, -1)
    
    curr = player(board)
    best_val = -math.inf if curr == X else math.inf
    best_move = (-1, -1)

    def helper(b: List[List[int]], maximizing: bool) -> int:
        if terminal(b): return utility(b)
        best = -1000 if maximizing else 1000
        for r in range(3):
            for c in range(3):
                if b[r][c] == EMPTY:
                    val = helper(result(b, (r, c)), not maximizing)
                    best = max(best, val) if maximizing else min(best, val)
        return best

    for r in range(3):
        for c in range(3):
            if board[r][c] == EMPTY:
                val = helper(result(board, (r, c)), curr == O)
                if (curr == X and val > best_val) or (curr == O and val < best_val):
                    best_val, best_move = val, (r, c)
    return best_move

# --- Application ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.SysFont("Arial", 40)
    user: Optional[int] = None
    board = initial_state()

    while True:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if user is None: # Menu logic
                    if pygame.Rect(WIDTH//8, HEIGHT//2, WIDTH//4, 50).collidepoint(mouse_pos): user = X
                    elif pygame.Rect(5*WIDTH//8, HEIGHT//2, WIDTH//4, 50).collidepoint(mouse_pos): user = O
                elif terminal(board) and pygame.Rect(WIDTH//3, HEIGHT-65, WIDTH//3, 50).collidepoint(mouse_pos):
                    user, board = None, initial_state()
                elif user == player(board) and not terminal(board):
                    for r in range(3):
                        for c in range(3):
                            if board[r][c] == EMPTY and pygame.Rect(WIDTH//2-120+c*80, HEIGHT//2-120+r*80, 80, 80).collidepoint(mouse_pos):
                                board = result(board, (r, c))

        # Rendering
        if user is None:
            text = font.render("Play Tic-Tac-Toe", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 50))
            for rect, label in [(pygame.Rect(WIDTH//8, HEIGHT//2, WIDTH//4, 50), "Play as X"), 
                                (pygame.Rect(5*WIDTH//8, HEIGHT//2, WIDTH//4, 50), "Play as O")]:
                pygame.draw.rect(screen, WHITE, rect)
                btn_text = font.render(label, True, BLACK)
                screen.blit(btn_text, (rect.x + (rect.width - btn_text.get_width())//2, rect.y))
        else:
            # Game Board
            for r in range(3):
                for c in range(3):
                    rect = pygame.Rect(WIDTH//2 - 120 + c*80, HEIGHT//2 - 120 + r*80, 80, 80)
                    pygame.draw.rect(screen, WHITE, rect, 3)
                    if board[r][c] != EMPTY:
                        val = "X" if board[r][c] == X else "O"
                        text = font.render(val, True, WHITE)
                        screen.blit(text, (rect.x + 25, rect.y + 10))
            
            # AI Logic
            if player(board) != user and not terminal(board):
                board = result(board, minimax(board))
            
            # Status/End Game
            msg = "Game Over" if terminal(board) else f"Playing as {'X' if user == X else 'O'}"
            screen.blit(font.render(msg, True, WHITE), (WIDTH//2 - 100, 20))
            if terminal(board):
                pygame.draw.rect(screen, WHITE, (WIDTH//3, HEIGHT-65, WIDTH//3, 50))
                screen.blit(font.render("Again", True, BLACK), (WIDTH//3 + 20, HEIGHT-60))

        pygame.display.flip()

if __name__ == "__main__":
    main()
