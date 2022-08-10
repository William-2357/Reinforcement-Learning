import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


point = namedtuple('Point', 'x, y')

# rgb colors
white = (255, 255, 255)
red = (200, 0, 0)
blue1 = (0, 0, 255)
blue2 = (0, 100, 255)
black = (0, 0, 0)

length = 20
speed = 40


class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.direction = Direction.RIGHT

        self.head = point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      point(self.head.x - length, self.head.y),
                      point(self.head.x - (2 * length), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w - length) // length) * length
        y = random.randint(0, (self.h - length) // length) * length
        self.food = point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self._move(action)
        self.snake.insert(0, self.head)

        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        self._update_ui()
        self.clock.tick(speed)
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        if pt.x > self.w - length or pt.x < 0 or pt.y > self.h - length or pt.y < 0:
            return True
        if pt in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        self.display.fill(black)

        for pt in self.snake:
            pygame.draw.rect(self.display, blue1, pygame.Rect(pt.x, pt.y, length, length))
            pygame.draw.rect(self.display, blue2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        pygame.draw.rect(self.display, red, pygame.Rect(self.food.x, self.food.y, length, length))

        text = font.render("Score: " + str(self.score), True, white)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, action):

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        else:
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += length
        elif self.direction == Direction.LEFT:
            x -= length
        elif self.direction == Direction.DOWN:
            y += length
        elif self.direction == Direction.UP:
            y -= length

        self.head = point(x, y)