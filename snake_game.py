import math
import random
import sys
import os

import pygame


pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass


WIDTH = 960
HEIGHT = 640
FPS = 60
CELL_SIZE = 24
GRID_WIDTH = 34
GRID_HEIGHT = 21
BOARD_LEFT = (WIDTH - GRID_WIDTH * CELL_SIZE) // 2
BOARD_TOP = 96
MOVE_EVENT = pygame.USEREVENT + 1
BONUS_EVENT = pygame.USEREVENT + 2
BONUS_LIFETIME_MS = 5000

WHITE = (245, 247, 255)
BLACK = (8, 11, 20)
NAVY = (15, 22, 42)
PANEL = (20, 29, 54)
PANEL_LINE = (72, 92, 132)
GRID_LINE = (31, 42, 70)
MINT = (112, 238, 190)
SKY = (94, 198, 255)
GOLD = (255, 211, 105)
CRIMSON = (255, 70, 105)
SLATE = (143, 154, 185)
LAVENDER = (184, 156, 255)

ASSETS_DIR = "Assets"
INTRO_SOUND = os.path.join(ASSETS_DIR, "Musics\\collid.wav")
GAME_OVER_SOUND = os.path.join(ASSETS_DIR, "Musics\\gameover-flappy.mp3")
FLAP_SOUND = os.path.join(ASSETS_DIR, "Musics\\jump-flappy.mp3")
SCORE_SOUND = os.path.join(ASSETS_DIR, "Musics\\collid.wav")
BG_MUSIC = os.path.join(ASSETS_DIR, "Musics\\bgmusic-flappy.mp3")


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


class Particle:
    def __init__(self, x, y, color, speed=3.6):
        angle = random.uniform(0, math.tau)
        velocity = random.uniform(1.0, speed)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * velocity
        self.vy = math.sin(angle) * velocity
        self.radius = random.randint(2, 5)
        self.life = random.randint(22, 42)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.03
        self.radius = max(1, self.radius - 0.04)
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = clamp(self.life * 6, 0, 220)
        pygame.draw.circle(surface, (*self.color, alpha), (int(self.x), int(self.y)), int(self.radius))


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        center = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.body = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
        self.direction = (1, 0)
        self.pending_direction = (1, 0)
        self.last_tail = self.body[-1]

    @property
    def head(self):
        return self.body[0]

    def set_direction(self, direction):
        if direction[0] + self.direction[0] == 0 and direction[1] + self.direction[1] == 0:
            return
        self.pending_direction = direction

    def move(self):
        self.direction = self.pending_direction
        new_head = (self.head[0] + self.direction[0], self.head[1] + self.direction[1])
        self.last_tail = self.body[-1]
        self.body.insert(0, new_head)
        self.body.pop()

    def grow(self):
        self.body.append(self.last_tail)

    def hit_wall(self):
        x, y = self.head
        return x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT

    def hit_self(self):
        return self.head in self.body[1:]


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Neon Snake Rush")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("arialblack", 46)
        self.heading_font = pygame.font.SysFont("arial", 28, bold=True)
        self.ui_font = pygame.font.SysFont("arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("arial", 18)
        self.tiny_font = pygame.font.SysFont("arial", 14, bold=True)
        self.snake = Snake()
        self.food = None
        self.bonus = None
        self.stars = [
            [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.choice([1, 1, 2]), random.uniform(0.15, 0.55)]
            for _ in range(90)
        ]
        self.particles = []
        self.high_score = 0
        self.reset_game()

        self.intro_sound = pygame.mixer.Sound(INTRO_SOUND)
        self.game_over_sound = pygame.mixer.Sound(GAME_OVER_SOUND)
        self.eat_sound = pygame.mixer.Sound(FLAP_SOUND)
        self.score_sound = pygame.mixer.Sound(SCORE_SOUND)
        self.bg_music = pygame.mixer.Sound(BG_MUSIC)

    def reset_game(self):
        self.snake.reset()
        self.score = 0
        self.state = "intro"
        self.food = self.random_empty_cell()
        self.bonus = None
        self.bonus_spawned_at = 0
        self.message = "Press SPACE to start"
        self.message_timer = FPS * 2
        self.shake_frames = 0
        self.move_delay = 135
        pygame.time.set_timer(MOVE_EVENT, self.move_delay)
        pygame.time.set_timer(BONUS_EVENT, 5500)

    def start_game(self):        
        self.snake.reset()
        self.bg_music.play(-1)
        self.score = 0
        self.food = self.random_empty_cell()
        self.bonus = None
        self.bonus_spawned_at = 0
        self.state = "playing"
        self.message = "Eat green points. Red bonus vanishes fast."
        self.message_timer = FPS * 2
        self.move_delay = 135
        pygame.time.set_timer(MOVE_EVENT, self.move_delay)
        pygame.time.set_timer(BONUS_EVENT, 5500)

    def random_empty_cell(self):
        occupied = set(self.snake.body)
        if self.food:
            occupied.add(self.food)
        if self.bonus:
            occupied.add(self.bonus)
        choices = [
            (x, y)
            for y in range(GRID_HEIGHT)
            for x in range(GRID_WIDTH)
            if (x, y) not in occupied
        ]
        return random.choice(choices) if choices else (0, 0)

    def grid_to_screen(self, cell):
        return (
            BOARD_LEFT + cell[0] * CELL_SIZE + CELL_SIZE // 2,
            BOARD_TOP + cell[1] * CELL_SIZE + CELL_SIZE // 2,
        )

    def spawn_particles(self, cell, color, amount=18, speed=4.0):
        x, y = self.grid_to_screen(cell)
        for _ in range(amount):
            self.particles.append(Particle(x, y, color, speed))

    def update_speed(self):
        new_delay = max(72, 135 - (self.score // 5) * 7)
        if new_delay != self.move_delay:
            self.move_delay = new_delay
            pygame.time.set_timer(MOVE_EVENT, self.move_delay)

    def spawn_bonus(self):
        if self.state != "playing" or self.bonus is not None:
            return
        self.bonus = self.random_empty_cell()
        self.bonus_spawned_at = pygame.time.get_ticks()
        self.message = "Red bonus active: +5"
        self.message_timer = FPS

    def expire_bonus_if_needed(self):
        if self.bonus is None:
            return
        if pygame.time.get_ticks() - self.bonus_spawned_at >= BONUS_LIFETIME_MS:
            self.spawn_particles(self.bonus, CRIMSON, 10, 2.8)
            self.bonus = None
            self.message = "Bonus vanished"
            self.message_timer = FPS

    def step_snake(self):
        if self.state != "playing":
            return

        self.snake.move()

        if self.snake.hit_wall() or self.snake.hit_self():
            self.game_over()
            return

        if self.snake.head == self.food:
            self.eat_sound.play()
            self.score += 1
            self.high_score = max(self.high_score, self.score)
            self.snake.grow()
            self.spawn_particles(self.food, MINT, 22, 4.5)
            self.food = self.random_empty_cell()
            self.message = "+1 point"
            self.message_timer = FPS // 2
            self.update_speed()

        if self.bonus and self.snake.head == self.bonus:
            self.score_sound.play()
            self.score += 5
            self.high_score = max(self.high_score, self.score)
            self.spawn_particles(self.bonus, CRIMSON, 36, 5.2)
            self.bonus = None
            self.message = "Bonus eaten: +5"
            self.message_timer = FPS
            self.update_speed()

    def game_over(self):
        self.state = "game_over"
        self.high_score = max(self.high_score, self.score)
        self.shake_frames = 18
        self.spawn_particles(self.snake.head, CRIMSON, 42, 5.4)
        self.message = "Game over"
        self.message_timer = FPS * 2
        self.bg_music.stop()
        self.game_over_sound.play()

        pygame.time.set_timer(BONUS_EVENT, 0)


    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

    def update(self):
        if self.state == "playing":
            self.expire_bonus_if_needed()

        self.update_particles()
        if self.message_timer > 0:
            self.message_timer -= 1
        if self.shake_frames > 0:
            self.shake_frames -= 1

    def draw_background(self):
        self.screen.fill(BLACK)
        for y in range(HEIGHT):
            blend = y / HEIGHT
            color = (int(8 + blend * 6), int(11 + blend * 15), int(20 + blend * 26))
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

        for star in self.stars:
            star[1] += star[3]
            if star[1] > HEIGHT:
                star[0] = random.randint(0, WIDTH)
                star[1] = -4
            pygame.draw.circle(self.screen, (255, 255, 255, 115), (int(star[0]), int(star[1])), star[2])

    def draw_hud(self):
        hud = pygame.Rect(18, 16, WIDTH - 36, 58)
        pygame.draw.rect(self.screen, PANEL, hud, border_radius=18)
        pygame.draw.rect(self.screen, PANEL_LINE, hud, 2, border_radius=18)

        score_text = self.ui_font.render(f"Score: {self.score}", True, WHITE)
        high_score_text = self.ui_font.render(f"Best: {self.high_score}", True, GOLD)
        length_text = self.ui_font.render(f"Length: {len(self.snake.body)}", True, MINT)

        self.screen.blit(score_text, (36, 29))
        self.screen.blit(length_text, (WIDTH // 2 - length_text.get_width() // 2, 29))
        self.screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 38, 29))

    def draw_board(self, target):
        board = pygame.Rect(BOARD_LEFT - 8, BOARD_TOP - 8, GRID_WIDTH * CELL_SIZE + 16, GRID_HEIGHT * CELL_SIZE + 16)
        pygame.draw.rect(target, (9, 16, 32), board, border_radius=22)
        pygame.draw.rect(target, (71, 97, 151), board, 2, border_radius=22)

        play_area = pygame.Rect(BOARD_LEFT, BOARD_TOP, GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
        pygame.draw.rect(target, (11, 18, 35), play_area, border_radius=14)

        for x in range(GRID_WIDTH + 1):
            line_x = BOARD_LEFT + x * CELL_SIZE
            pygame.draw.line(target, GRID_LINE, (line_x, BOARD_TOP), (line_x, BOARD_TOP + GRID_HEIGHT * CELL_SIZE))
        for y in range(GRID_HEIGHT + 1):
            line_y = BOARD_TOP + y * CELL_SIZE
            pygame.draw.line(target, GRID_LINE, (BOARD_LEFT, line_y), (BOARD_LEFT + GRID_WIDTH * CELL_SIZE, line_y))

    def draw_food(self, target):
        center = self.grid_to_screen(self.food)
        pulse = math.sin(pygame.time.get_ticks() * 0.008) * 2
        pygame.draw.circle(target, (66, 255, 181, 70), center, int(18 + pulse))
        pygame.draw.circle(target, MINT, center, 9)
        pygame.draw.circle(target, WHITE, (center[0] - 3, center[1] - 3), 3)

        if not self.bonus:
            return
        bonus_center = self.grid_to_screen(self.bonus)
        remaining = clamp(1 - (pygame.time.get_ticks() - self.bonus_spawned_at) / BONUS_LIFETIME_MS, 0, 1)
        radius = int(14 + math.sin(pygame.time.get_ticks() * 0.014) * 2)
        pygame.draw.circle(target, (255, 70, 105, 90), bonus_center, 24)
        pygame.draw.circle(target, CRIMSON, bonus_center, radius)
        pygame.draw.circle(target, WHITE, (bonus_center[0] - 4, bonus_center[1] - 4), 4)

        timer_rect = pygame.Rect(0, 0, 46, 6)
        timer_rect.center = (bonus_center[0], bonus_center[1] + 24)
        pygame.draw.rect(target, (60, 20, 34), timer_rect, border_radius=4)
        fill = timer_rect.copy()
        fill.width = int(timer_rect.width * remaining)
        pygame.draw.rect(target, GOLD if remaining > 0.35 else CRIMSON, fill, border_radius=4)

    def draw_snake(self, target):
        for index, cell in enumerate(reversed(self.snake.body)):
            actual_index = len(self.snake.body) - index - 1
            center = self.grid_to_screen(cell)
            rect = pygame.Rect(0, 0, CELL_SIZE - 3, CELL_SIZE - 3)
            rect.center = center
            color_shift = clamp(actual_index * 5, 0, 80)
            color = (
                clamp(MINT[0] - color_shift, 40, 255),
                clamp(MINT[1] - color_shift // 2, 120, 255),
                clamp(MINT[2] - color_shift // 3, 110, 255),
            )
            pygame.draw.rect(target, (38, 220, 164, 55), rect.inflate(8, 8), border_radius=10)
            pygame.draw.rect(target, color, rect, border_radius=8)

            if actual_index == 0:
                pygame.draw.rect(target, WHITE, rect.inflate(-8, -8), border_radius=6)
                dx, dy = self.snake.direction
                if dx:
                    eyes = [(center[0] + dx * 5, center[1] - 5), (center[0] + dx * 5, center[1] + 5)]
                else:
                    eyes = [(center[0] - 5, center[1] + dy * 5), (center[0] + 5, center[1] + dy * 5)]
                for eye in eyes:
                    pygame.draw.circle(target, NAVY, eye, 2)

    def draw_message(self):
        if self.state == "playing" and self.message_timer <= 0:
            return
        text = self.small_font.render(self.message, True, WHITE)
        panel = pygame.Rect(0, 0, text.get_width() + 36, 38)
        panel.center = (WIDTH // 2, HEIGHT - 28)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=16)
        pygame.draw.rect(self.screen, SKY, panel, 2, border_radius=16)
        self.screen.blit(text, text.get_rect(center=panel.center))

    def draw_intro(self):
        panel = pygame.Rect(0, 0, 620, 282)
        panel.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(self.screen, (15, 23, 44), panel, border_radius=28)
        pygame.draw.rect(self.screen, LAVENDER, panel, 2, border_radius=28)

        title = self.title_font.render("NEON SNAKE RUSH", True, WHITE)
        subtitle = self.heading_font.render("Grow with green points. Chase red bonuses.", True, GOLD)
        controls = self.small_font.render("Move: Arrow Keys or W/A/S/D   Pause: P", True, WHITE)
        hint = self.small_font.render("Press SPACE to begin", True, SKY)
        badge = self.tiny_font.render("Red bonus: +5 score, no growth, 5 seconds only", True, CRIMSON)

        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 74)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        self.screen.blit(controls, controls.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 34)))
        self.screen.blit(badge, badge.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 72)))
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 116)))

    def draw_pause(self):
        panel = pygame.Rect(0, 0, 350, 150)
        panel.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(self.screen, (15, 23, 44), panel, border_radius=24)
        pygame.draw.rect(self.screen, GOLD, panel, 2, border_radius=24)
        title = self.heading_font.render("PAUSED", True, GOLD)
        hint = self.small_font.render("Press P to continue", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 24)))
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 28)))

    def draw_game_over(self):
        panel = pygame.Rect(0, 0, 470, 230)
        panel.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(self.screen, (15, 23, 44), panel, border_radius=28)
        pygame.draw.rect(self.screen, CRIMSON, panel, 2, border_radius=28)

        title = self.title_font.render("GAME OVER", True, CRIMSON)
        score_text = self.heading_font.render(f"Score: {self.score}", True, WHITE)
        high_score_text = self.heading_font.render(f"Best: {self.high_score}", True, GOLD)
        hint = self.small_font.render("Press R to restart or Q to quit", True, SKY)

        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 56)))
        self.screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 6)))
        self.screen.blit(high_score_text, high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 44)))
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 92)))

    def draw(self):
        self.draw_background()
        shake_x = random.randint(-6, 6) if self.shake_frames > 0 else 0
        shake_y = random.randint(-4, 4) if self.shake_frames > 0 else 0

        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.draw_board(layer)
        self.draw_food(layer)
        self.draw_snake(layer)
        for particle in self.particles:
            particle.draw(layer)

        self.screen.blit(layer, (shake_x, shake_y))
        self.draw_hud()
        self.draw_message()

        if self.state == "intro":
            self.draw_intro()
        elif self.state == "paused":
            self.draw_pause()
        elif self.state == "game_over":
            self.draw_game_over()

        pygame.display.flip()

    def handle_keydown(self, key):
        if key == pygame.K_q:
            pygame.quit()
            sys.exit()

        if self.state == "intro" and key == pygame.K_SPACE:
            self.start_game()
            return

        if self.state == "game_over" and key == pygame.K_r:
            self.reset_game()
            self.start_game()
            return

        if key == pygame.K_p and self.state in ("playing", "paused"):
            self.state = "paused" if self.state == "playing" else "playing"
            return

        if self.state != "playing":
            return

        controls = {
            pygame.K_UP: (0, -1),
            pygame.K_w: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_s: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_a: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_d: (1, 0),
        }
        if key in controls:
            self.snake.set_direction(controls[key])

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)
                if event.type == MOVE_EVENT:
                    self.step_snake()
                if event.type == BONUS_EVENT:
                    self.spawn_bonus()

            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
