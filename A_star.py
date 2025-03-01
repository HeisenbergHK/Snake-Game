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