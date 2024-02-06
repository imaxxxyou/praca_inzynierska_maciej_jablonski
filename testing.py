import pygame
import random
import sys

# Inicjalizacja Pygame
pygame.init()

# Ustawienia gry
WIDTH, HEIGHT = 500, 500
CELL_SIZE = 10
FPS = 60

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Inicjalizacja okna gry
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kombajn koszący zboże")

# Inicjalizacja zegara
clock = pygame.time.Clock()

class Game:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.field = [['.' for _ in range(cols)] for _ in range(rows)]
        self.player_pos = (0, 0)
        self.goal_pos = (random.randint(0, rows-1), random.randint(0, cols-1))
        self.field[self.goal_pos[0]][self.goal_pos[1]] = 'W'

    def move_player(self, direction):
        x, y = self.player_pos
        if direction == 'left' and y > 0:
            y -= 1
        elif direction == 'right' and y < self.cols - 1:
            y += 1
        elif direction == 'up' and x > 0:
            x -= 1
        elif direction == 'down' and x < self.rows - 1:
            x += 1

        self.field[self.player_pos[0]][self.player_pos[1]] = '.'
        self.player_pos = (x, y)
        self.field[x][y] = 'K'

    def check_win(self):
        return self.player_pos == self.goal_pos

    def draw(self):
        for row in range(self.rows):
            for col in range(self.cols):
                color = WHITE if self.field[row][col] == '.' else RED
                pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Funkcja główna gry
def main():
    rows = 100
    cols = 100
    game = Game(rows, cols)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and game.player_pos[1] > 0:
            game.move_player('left')
        elif keys[pygame.K_RIGHT] and game.player_pos[1] < game.cols - 1:
            game.move_player('right')
        elif keys[pygame.K_UP] and game.player_pos[0] > 0:
            game.move_player('up')
        elif keys[pygame.K_DOWN] and game.player_pos[0] < game.rows - 1:
            game.move_player('down')

        screen.fill(BLACK)
        game.draw()
        pygame.display.flip()

        if game.check_win():
            pygame.time.delay(1000)  # Opóźnienie na chwilę, aby gracz zauważył wygraną
            print("Gratulacje! Dotarłeś do obszaru zboża. Wygrałeś!")
            pygame.quit()
            sys.exit()

        clock.tick(FPS)

if __name__ == "__main__":
    main()
