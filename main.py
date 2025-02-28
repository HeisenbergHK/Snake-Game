import pygame
import random
import sqlite3
from datetime import datetime

# Game Constants
BOARD_SIZE = 10  # Flexible board size
CELL_SIZE = 40  # Pixel size of each cell
WIDTH, HEIGHT = BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# Database Setup
conn = sqlite3.connect("snake_game.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS game_records (
    game_id TEXT PRIMARY KEY,
    board_size INTEGER,
    result TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS game_states (
    game_id TEXT,
    step INTEGER,
    snake TEXT,
    food TEXT,
    action TEXT,
    FOREIGN KEY(game_id) REFERENCES game_records(game_id)
)
""")
conn.commit()

def save_game_state(game_id, step, snake, food, action):
    cursor.execute("""
    INSERT INTO game_states (game_id, step, snake, food, action)
    VALUES (?, ?, ?, ?, ?)
    """, (game_id, step, str(snake), str(food), action))
    conn.commit()

class SnakeGame:
    def __init__(self):
        self.snake = [(BOARD_SIZE // 2, BOARD_SIZE // 2)]
        self.direction = (0, -1)  # Initially moving up
        self.food = self.place_food()
        self.running = True
        self.score = 0
        self.step = 0
        self.game_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    def place_food(self):
        while True:
            food = (random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1))
            if food not in self.snake:
                return food

    def move(self):
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        if new_head in self.snake or not (0 <= new_head[0] < BOARD_SIZE and 0 <= new_head[1] < BOARD_SIZE):
            self.running = False
            cursor.execute("INSERT INTO game_records (game_id, board_size, result) VALUES (?, ?, ?)",
                           (self.game_id, BOARD_SIZE, "Lost"))
            conn.commit()
            return
        
        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            self.food = self.place_food()
            self.score += 1
        else:
            self.snake.pop()
        
        save_game_state(self.game_id, self.step, self.snake, self.food, str(self.direction))
        self.step += 1
        
        if len(self.snake) == BOARD_SIZE * BOARD_SIZE:
            self.running = False
            cursor.execute("INSERT INTO game_records (game_id, board_size, result) VALUES (?, ?, ?)",
                           (self.game_id, BOARD_SIZE, "Won"))
            conn.commit()

    def change_direction(self, direction):
        if (direction[0] != -self.direction[0] or direction[1] != -self.direction[1]):
            self.direction = direction

    def draw(self):
        screen.fill(BACKGROUND_COLOR)
        for segment in self.snake:
            pygame.draw.rect(screen, SNAKE_COLOR, (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, FOOD_COLOR, (self.food[0] * CELL_SIZE, self.food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.display.flip()


def main():
    game = SnakeGame()
    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    game.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    game.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    game.change_direction((1, 0))
        
        game.move()
        game.draw()
        clock.tick(10)
    
    pygame.quit()
    conn.close()

if __name__ == "__main__":
    main()
