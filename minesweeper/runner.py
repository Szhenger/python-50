import pygame
import sys
import os
from minesweeper import Minesweeper, MinesweeperAI

# Constants
HEIGHT, WIDTH, MINES = 8, 8, 8
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)

def center_text(text_surf, rect):
    text_rect = text_surf.get_rect(center=rect.center)
    return text_rect

def main():
    pygame.init()
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Minesweeper")
    clock = pygame.time.Clock()

    # Load Assets
    font_path = "assets/fonts/OpenSans-Regular.ttf"
    small_font = pygame.font.Font(font_path, 20)
    medium_font = pygame.font.Font(font_path, 28)
    large_font = pygame.font.Font(font_path, 40)
    
    flag_img = pygame.image.load("assets/images/flag.png")
    mine_img = pygame.image.load("assets/images/mine.png")

    # Board Setup
    board_padding = 20
    board_w = ((2/3) * SCREEN_WIDTH) - (board_padding * 2)
    board_h = SCREEN_HEIGHT - (board_padding * 2)
    cell_size = min(board_w / WIDTH, board_h / HEIGHT)

    # Scale images
    flag_img = pygame.transform.scale(flag_img, (int(cell_size), int(cell_size)))
    mine_img = pygame.transform.scale(mine_img, (int(cell_size), int(cell_size)))

    game = Minesweeper(HEIGHT, WIDTH, MINES)
    ai = MinesweeperAI(HEIGHT, WIDTH)
    revealed, flags = set(), set()
    lost, instructions = False, True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        window.fill(BLACK)
        mx, my = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()

        if instructions:
            title = large_font.render("Play Minesweeper", True, WHITE)
            window.blit(title, center_text(title, pygame.Rect(0, 0, SCREEN_WIDTH, 100)))
            
            play_btn = pygame.Rect(SCREEN_WIDTH//4, (3/4)*SCREEN_HEIGHT, SCREEN_WIDTH//2, 50)
            pygame.draw.rect(window, WHITE, play_btn)
            play_text = medium_font.render("Play Game", True, BLACK)
            window.blit(play_text, center_text(play_text, play_btn))
            
            if clicked[0] and play_btn.collidepoint(mx, my):
                instructions = False
        else:
            # Draw Board
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    rect = pygame.Rect(board_padding + j * cell_size, board_padding + i * cell_size, cell_size, cell_size)
                    pygame.draw.rect(window, GRAY, rect)
                    pygame.draw.rect(window, WHITE, rect, 3)

                    cell = (i, j)
                    if lost and game.is_mine(cell):
                        window.blit(mine_img, rect)
                    elif cell in flags:
                        window.blit(flag_img, rect)
                    elif cell in revealed:
                        count = game.nearby_mines(cell)
                        text = small_font.render(str(count), True, BLACK)
                        window.blit(text, center_text(text, rect))

            # Interaction
            if clicked[2] and not lost: # Right click
                for i in range(HEIGHT):
                    for j in range(WIDTH):
                        rect = pygame.Rect(board_padding + j*cell_size, board_padding + i*cell_size, cell_size, cell_size)
                        if rect.collidepoint(mx, my) and (i, j) not in revealed:
                            if (i, j) in flags: flags.remove((i, j))
                            else: flags.add((i, j))
                            pygame.time.delay(200)

            # (Add AI/Reset logic following similar collision patterns...)
            
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
