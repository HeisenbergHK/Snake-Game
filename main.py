import random
import sqlite3
import time
from datetime import datetime

import pygame

from A_star import a_star_search  # Import external A* search function

# Game Constants
BOARD_SIZE = 10  # Flexible board size
CELL_SIZE = 40  # Pixel size of each cell
WIDTH, HEIGHT = BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
font = pygame.font.Font(None, 36)

# Database Setup
conn = sqlite3.connect("snake_game.db")
cursor = conn.cursor()
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS game_records (
    game_id TEXT PRIMARY KEY,
    board_size INTEGER,
    result TEXT,
    score INTEGER,
    time_elapsed REAL
)
"""
)
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS game_states (
    game_id TEXT,
    step INTEGER,
    snake TEXT,
    food TEXT,
    action TEXT,
    FOREIGN KEY(game_id) REFERENCES game_records(game_id)
)
"""
)
conn.commit()


def save_game_state(game_id, step, snake, food, action):
    cursor.execute(
        """
    INSERT INTO game_states (game_id, step, snake, food, action)
    VALUES (?, ?, ?, ?, ?)
    """,
        (game_id, step, str(snake), str(food), action),
    )
    conn.commit()


class SnakeGame:
    def __init__(self, mode):
        self.snake = [(BOARD_SIZE // 2, BOARD_SIZE // 2)]
        self.head = self.snake[0]
        self.direction = None  # Initially no movement
        self.food = self.place_food()
        self.running = True
        self.score = 0
        self.step = 0
        self.start_time = pygame.time.get_ticks()
        self.game_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.mode = mode

    def place_food(self):
        while True:
            food = (
                random.randint(0, BOARD_SIZE - 1),
                random.randint(0, BOARD_SIZE - 1),
            )
            if food not in self.snake:
                return food

    def get_board(self):
        board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for segment in self.snake:
            board[segment[1]][segment[0]] = 1
        board[self.food[1]][self.food[0]] = 2
        return board

    def move(self):
        if self.direction is None:
            return  # Do nothing if no direction is given

        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        print(new_head)

        if new_head in self.snake or not (
            0 <= new_head[0] < BOARD_SIZE and 0 <= new_head[1] < BOARD_SIZE
        ):
            self.show_message("Game Over")
            self.running = False
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.food = self.place_food()
            self.score += 1
        else:
            self.snake.pop()

        save_game_state(
            self.game_id, self.step, self.snake, self.food, str(self.direction)
        )
        self.step += 1

        if len(self.snake) == BOARD_SIZE * BOARD_SIZE:
            self.show_message("You Win!")
            self.running = False

        self.direction = None  # Reset direction after each move

    def draw(self):
        screen.fill(BACKGROUND_COLOR)
        for segment in self.snake:
            pygame.draw.rect(
                screen,
                SNAKE_COLOR,
                (segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
            )
        pygame.draw.rect(
            screen,
            FOOD_COLOR,
            (self.food[0] * CELL_SIZE, self.food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
        )

        # Display Score and Timer
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        score_text = font.render(f"Score: {self.score}", True, TEXT_COLOR)
        time_text = font.render(f"Time: {elapsed_time}s", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (WIDTH - 150, 10))

        pygame.display.flip()

    def show_message(self, message):
        screen.fill(BACKGROUND_COLOR)
        text = font.render(message, True, TEXT_COLOR)
        screen.blit(
            text,
            (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2),
        )
        pygame.display.flip()
        pygame.time.delay(3000)


def calculate_direction(current_pos, nex_pos):
    dif = (nex_pos[0] - current_pos[0], nex_pos[1] - current_pos[1])

    return None if dif == (0, 0) else dif


def main():
    mode = input("Select mode:\n1) manual\n2) ai\n-- ").strip().lower()
    if mode == "1":
        mode = "manual"
    elif mode == "2":
        mode = "ai"
    else:
        print("Invalid mode selected. Exiting.")
        return

    game = SnakeGame(mode)
    path = []

    while game.running:
        # Process events to keep the window responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False

        if mode == "manual":
            # Handle manual input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                game.direction = (0, -1)
            elif keys[pygame.K_DOWN]:
                game.direction = (0, 1)
            elif keys[pygame.K_LEFT]:
                game.direction = (-1, 0)
            elif keys[pygame.K_RIGHT]:
                game.direction = (1, 0)
        else:  # AI mode
            # Use A* algorithm to determine the next move
            if path:
                dir = calculate_direction(game.snake[0], path[0])
                game.direction = dir  # Take the first step from the A* path
                path.pop(0)
            else:
                board = game.get_board()
                path = a_star_search(
                    grid=board,
                    snake_body=game.snake,
                    head_position=game.snake[0],
                    goal_position=game.food,
                )

        # Move the snake and redraw the screen
        game.move()
        game.draw()

        # Add a small delay to make the game playable
        pygame.time.delay(100)  # Adjust the delay as needed

    pygame.quit()
    conn.close()


if __name__ == "__main__":
    main()
