import heapq

import numpy as np


class Node:
    def __init__(self, position, parent, g, h):
        self.position = position
        self.parent = parent
        self.h = h
        self.g = g
        self.f = g + h

    def __lt__(self, other):
        return self.f < other.f


def manhattan_distance(position, goal_position):
    return abs(goal_position[0] - position[0]) + abs(goal_position[1] - position[1])


def a_star_search(grid: np.ndarray, head_position, snake_body, goal_position):
    GRID_SIZE = len(grid)

    open_list = []
    closed_list = set()

    # INITIAL NODE
    head_node = Node(
        position=head_position,
        parent=None,
        g=0,
        h=manhattan_distance(head_position, goal_position),
    )

    # ADD INITIAL NODE TO LIST
    heapq.heappush(open_list, head_node)

    while open_list:
        # PICK A NODE FROM THE LIST
        current_node = heapq.heappop(open_list)

        # POSITION OF THAT NODE
        current_position = current_node.position

        # ADD TO CLOSED LIST
        closed_list.add(current_position)

        # GOAL FOUND
        if current_position == goal_position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]

        # EXTRACT ALL THE NEIGHBORS
        for search_position in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_position = (
                current_node.position[0] + search_position[0],
                current_node.position[1] + search_position[1],
            )

            # OUT OF THE BOARD
            if (
                new_position[0] < 0
                or new_position[0] >= GRID_SIZE
                or new_position[1] < 0
                or new_position[1] >= GRID_SIZE
            ):
                continue

            # INSIDE THE BODY
            elif new_position in snake_body:
                continue

            # THIS NODE ALREADY SEEN
            elif new_position in closed_list:
                continue

            else:
                new_node = Node(
                    parent=current_node,
                    position=new_position,
                    g=current_node.g + 1,
                    h=manhattan_distance(new_position, goal_position),
                )
                heapq.heappush(open_list, new_node)

    # NO PATH FOUND
    return None

def flood_fill_reachable_area(grid, start_position, snake_body):
    """
    Calculate the number of reachable empty cells using Flood Fill.
    """
    rows, cols = len(grid), len(grid[0])
    visited = set()

    def dfs(r, c):
        if (
            r < 0
            or r >= rows
            or c < 0
            or c >= cols
            or (r, c) in snake_body
            or (r, c) in visited
            or grid[r][c] != 0
        ):
            return 0
        visited.add((r, c))
        count = 1
        count += dfs(r + 1, c)
        count += dfs(r - 1, c)
        count += dfs(r, c + 1)
        count += dfs(r, c - 1)
        return count

    return dfs(start_position[0], start_position[1])


def get_best_direction(board, snake, food):
    """
    Determine the best direction for the snake to move when no direct path exists.
    """
    head = snake[0]
    possible_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    max_reachable = -1
    best_direction = None

    for direction in possible_directions:
        new_head = (head[0] + direction[0], head[1] + direction[1])

        # Skip invalid moves
        if (
            new_head in snake
            or not (0 <= new_head[0] < len(board))
            or not (0 <= new_head[1] < len(board[0]))
        ):
            continue

        # Temporarily update the board and snake
        temp_snake = snake.copy()
        temp_snake.insert(0, new_head)
        temp_snake.pop()  # Remove tail

        # Calculate reachable area
        temp_board = [[cell for cell in row] for row in board]
        reachable = flood_fill_reachable_area(temp_board, new_head, set(temp_snake))

        # Select the direction with the largest reachable area
        if reachable > max_reachable:
            max_reachable = reachable
            best_direction = direction

    return best_direction


def calculate_direction(current_pos, next_pos):
    """
    Calculate the direction vector between two positions.
    """
    dif = (next_pos[0] - current_pos[0], next_pos[1] - current_pos[1])
    return None if dif == (0, 0) else dif

if __name__ == "__main__":

    board = np.array(
        [
            [0, 0, 0, 0, 2],
            [0, 0, 1, 0, 0],
            [0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
    )

    head_position = (2, 1)
    snake_body = set([(2, 2), (1, 2)])
    goal_position = (0, 4)

    # Find the path using A*
    path = a_star_search(
        grid=board,
        head_position=head_position,
        snake_body=snake_body,
        goal_position=goal_position,
    )

    if path:
        print("Path to food:", path)
    else:
        print("No path to food found!")
