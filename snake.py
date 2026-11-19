from random import choice

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
START_POSITION = (GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
KEY_DIRECTIONS = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT,
}

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SPEED = 30

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс объектов на игровом поле."""

    def __init__(self, position=START_POSITION, body_color=None):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Нарисовать объект на игровом поле."""
        raise NotImplementedError

    def _draw_cell(self, position):
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Яблоко, появляющееся на свободной клетке."""

    def __init__(self, occupied=()):
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(occupied)

    def randomize_position(self, occupied=()):
        """Переместить яблоко и сообщить, нашлась ли свободная клетка."""
        occupied = set(occupied)
        free_cells = [
            (x, y)
            for y in range(0, SCREEN_HEIGHT, GRID_SIZE)
            for x in range(0, SCREEN_WIDTH, GRID_SIZE)
            if (x, y) not in occupied
        ]
        if not free_cells:
            return False
        self.position = choice(free_cells)
        return True

    def draw(self):
        """Нарисовать яблоко."""
        self._draw_cell(self.position)


class Snake(GameObject):
    """Змейка, у которой координаты головы идут первыми в списке."""

    def __init__(self):
        super().__init__(body_color=SNAKE_COLOR)
        self.reset(RIGHT)

    def reset(self, direction=None):
        """Вернуть змейку из одного сегмента в центр поля."""
        self.position = START_POSITION
        self.positions = [self.position]
        self.length = 1
        self.direction = direction or choice(tuple(KEY_DIRECTIONS.values()))
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Вернуть координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Применить выбранное направление перед следующим ходом."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Добавить новую голову и убрать прежний конец хвоста."""
        x, y = self.get_head_position()
        dx, dy = self.direction
        self.position = (
            (x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, self.position)
        self.last = self.positions.pop()

    def grow(self):
        """Удлинить змейку после хода, вернув убранный сегмент."""
        self.positions.append(self.last)
        self.length += 1
        self.last = None

    def draw(self):
        """Нарисовать все сегменты змейки."""
        for position in self.positions:
            self._draw_cell(position)


def handle_keys(game_object):
    """Обработать закрытие окна и запомнить допустимый поворот."""
    dx, dy = game_object.direction
    opposite = (-dx, -dy)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            direction = KEY_DIRECTIONS.get(event.key)
            if direction is not None and direction != opposite:
                game_object.next_direction = direction


def main():
    """Создать объекты и запустить игровой цикл."""
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head = snake.get_head_position()
        if head in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
        elif head == apple.position:
            snake.grow()
            if not apple.randomize_position(snake.positions):
                snake.reset()
                apple.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.flip()


if __name__ == '__main__':
    main()
