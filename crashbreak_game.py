import math
import os
import random
import sys

import pygame


pygame.init()
pygame.mixer.init()


WIDTH = 960
HEIGHT = 640
FPS = 60

ASSETS_DIR = "Assets"
BG_IMAGE = os.path.join(ASSETS_DIR, "bg.png")
HIT_SOUND = os.path.join(ASSETS_DIR, "collid.wav")
LOSE_SOUND = os.path.join(ASSETS_DIR, "collideout.wav")
BG_MUSIC = os.path.join(ASSETS_DIR, "bgmusic.mp3")

WHITE = (245, 247, 255)
BLACK = (12, 16, 30)
NAVY = (18, 24, 46)
SKY = (107, 199, 255)
GOLD = (255, 209, 102)
CORAL = (255, 111, 97)
MINT = (126, 234, 196)
LAVENDER = (184, 156, 255)
SLATE = (136, 147, 176)
CRIMSON = (255, 71, 87)


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


class Particle:
    def __init__(self, x, y, color):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.2, 4.6)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = random.randint(2, 5)
        self.life = random.randint(24, 42)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.06
        self.life -= 1
        self.radius = max(1, self.radius - 0.04)

    def draw(self, surface):
        if self.life <= 0:
            return
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))


class Paddle:
    def __init__(self):
        self.width = 150
        self.height = 18
        self.speed = 9
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.centerx = WIDTH // 2
        self.rect.y = HEIGHT - 58

    def reset(self):
        self.width = 150
        self.rect.width = self.width
        self.rect.centerx = WIDTH // 2

    def update(self):
        keys = pygame.key.get_pressed()
        move = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += self.speed

        self.rect.x += move
        self.rect.x = clamp(self.rect.x, 0, WIDTH - self.rect.width)

    def grow(self):
        center = self.rect.centerx
        self.width = min(220, self.width + 24)
        self.rect.width = self.width
        self.rect.centerx = center
        self.rect.x = clamp(self.rect.x, 0, WIDTH - self.rect.width)

    def draw(self, surface):
        glow_rect = self.rect.inflate(18, 18)
        pygame.draw.rect(surface, (56, 197, 255), glow_rect, border_radius=18)
        pygame.draw.rect(surface, GOLD, self.rect, border_radius=14)
        inner = self.rect.inflate(-18, -6)
        pygame.draw.rect(surface, WHITE, inner, border_radius=12)


class Ball:
    def __init__(self):
        self.radius = 11
        self.reset()

    def reset(self, attach_to_paddle=True, paddle=None):
        self.speed_x = random.choice([-4, 4])
        self.speed_y = -5
        self.base_speed = 6.4
        self.max_speed = 11.5
        self.attached = attach_to_paddle
        if paddle:
            self.x = paddle.rect.centerx
            self.y = paddle.rect.top - self.radius - 2
        else:
            self.x = WIDTH // 2
            self.y = HEIGHT // 2

    def launch(self):
        self.attached = False

    def update(self, paddle):
        if self.attached:
            self.x = paddle.rect.centerx
            self.y = paddle.rect.top - self.radius - 2
            return

        self.x += self.speed_x
        self.y += self.speed_y

        if self.x - self.radius <= 0:
            self.x = self.radius
            self.speed_x *= -1
        elif self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.speed_x *= -1

        if self.y - self.radius <= 0:
            self.y = self.radius
            self.speed_y *= -1

    def bounce_from_paddle(self, paddle):
        offset = (self.x - paddle.rect.centerx) / (paddle.rect.width / 2)
        self.speed_x = offset * 7.2
        self.speed_y = -abs(self.speed_y)
        speed = min(self.max_speed, math.hypot(self.speed_x, self.speed_y) + 0.35)
        angle = math.atan2(self.speed_y, self.speed_x)
        self.speed_x = math.cos(angle) * speed
        self.speed_y = math.sin(angle) * speed
        self.y = paddle.rect.top - self.radius - 1

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def draw(self, surface):
        pygame.draw.circle(surface, SKY, (int(self.x), int(self.y)), self.radius + 7)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, MINT, (int(self.x - 3), int(self.y - 3)), self.radius // 2)


class Brick:
    COLORS = [CORAL, GOLD, MINT, SKY, LAVENDER]

    def __init__(self, x, y, hits):
        self.rect = pygame.Rect(x, y, 76, 28)
        self.hits = hits
        self.max_hits = hits

    @property
    def color(self):
        return self.COLORS[self.hits - 1]

    def hit(self):
        self.hits -= 1
        return self.hits <= 0

    def draw(self, surface):
        shadow = self.rect.move(0, 6)
        pygame.draw.rect(surface, (24, 30, 52), shadow, border_radius=10)
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        shine = self.rect.inflate(-10, -12)
        pygame.draw.rect(surface, WHITE, shine, border_radius=8)
        if self.max_hits > 1:
            font = pygame.font.SysFont("arial", 16, bold=True)
            text = font.render(str(self.hits), True, NAVY)
            surface.blit(text, text.get_rect(center=self.rect.center))


class PowerUp:
    def __init__(self, x, y, kind):
        self.kind = kind
        self.rect = pygame.Rect(x, y, 26, 26)
        self.speed = 3
        self.color = MINT if kind == "expand" else GOLD

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)
        label = "+" if self.kind == "expand" else "*"
        font = pygame.font.SysFont("arial", 18, bold=True)
        text = font.render(label, True, NAVY)
        surface.blit(text, text.get_rect(center=self.rect.center))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Crash Breaker Deluxe")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("arialblack", 48)
        self.subtitle_font = pygame.font.SysFont("arial", 24, bold=True)
        self.ui_font = pygame.font.SysFont("arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("arial", 18)

        self.background = pygame.image.load(BG_IMAGE).convert()
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        self.hit_sound = pygame.mixer.Sound(HIT_SOUND)
        self.lose_sound = pygame.mixer.Sound(LOSE_SOUND)

        pygame.mixer.music.load(BG_MUSIC)
        pygame.mixer.music.set_volume(0.18)
        pygame.mixer.music.play(-1)

        self.stars = [
            [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)]
            for _ in range(60)
        ]
        self.reset(full_reset=True)

    def reset(self, full_reset=False):
        self.state = "intro"
        self.level = 1
        self.score = 0
        self.high_score = 0 if full_reset else self.high_score
        self.lives = 3
        self.combo = 0
        self.shake_frames = 0
        self.message_timer = 0
        self.message = "Press SPACE to launch"
        self.particles = []
        self.powerups = []
        self.paddle = Paddle()
        self.ball = Ball()
        self.ball.reset(True, self.paddle)
        self.bricks = self.build_level(self.level)

    def build_level(self, level):
        bricks = []
        rows = min(5 + level, 8)
        cols = 10
        brick_width = 76
        brick_height = 28
        gap = 12
        offset_x = (WIDTH - (cols * brick_width + (cols - 1) * gap)) // 2
        offset_y = 90

        for row in range(rows):
            for col in range(cols):
                if random.random() < min(0.08 + level * 0.015, 0.18):
                    continue
                hits = 1 + (1 if row > 1 and random.random() < 0.28 + level * 0.03 else 0)
                hits = min(hits, 2 + level // 3)
                x = offset_x + col * (brick_width + gap)
                y = offset_y + row * (brick_height + gap)
                bricks.append(Brick(x, y, hits))

        return bricks

    def start_game(self):
        self.state = "playing"
        self.message = "Break the wall. Protect your lives."
        self.message_timer = FPS * 2

    def next_level(self):
        self.level += 1
        self.score += 150
        self.combo = 0
        self.message = f"Level {self.level} unlocked!"
        self.message_timer = FPS * 2
        self.paddle.reset()
        self.ball.reset(True, self.paddle)
        self.powerups.clear()
        self.bricks = self.build_level(self.level)

    def lose_life(self):
        self.lives -= 1
        self.combo = 0
        self.shake_frames = 16
        self.lose_sound.play()
        if self.lives <= 0:
            self.high_score = max(self.high_score, self.score)
            self.state = "game_over"
            self.message = "Press R to restart"
        else:
            self.ball.reset(True, self.paddle)
            self.message = "Life lost. Press SPACE to relaunch"
            self.message_timer = FPS * 2

    def spawn_particles(self, x, y, color, amount=12):
        for _ in range(amount):
            self.particles.append(Particle(x, y, color))

    def spawn_powerup(self, brick):
        roll = random.random()
        if roll < 0.12:
            self.powerups.append(PowerUp(brick.rect.centerx - 13, brick.rect.centery - 13, "expand"))
        elif roll < 0.19:
            self.powerups.append(PowerUp(brick.rect.centerx - 13, brick.rect.centery - 13, "bonus"))

    def update(self):
        if self.state != "playing":
            self.update_particles()
            return

        self.paddle.update()
        self.ball.update(self.paddle)

        if self.ball.rect.colliderect(self.paddle.rect) and self.ball.speed_y > 0:
            self.ball.bounce_from_paddle(self.paddle)
            self.hit_sound.play()

        if self.ball.y - self.ball.radius > HEIGHT:
            self.lose_life()

        hit_index = self.ball.rect.collidelist([brick.rect for brick in self.bricks])
        if hit_index != -1:
            brick = self.bricks[hit_index]
            overlap = self.ball.rect.clip(brick.rect)
            if overlap.width >= overlap.height:
                self.ball.speed_y *= -1
            else:
                self.ball.speed_x *= -1

            destroyed = brick.hit()
            self.hit_sound.play()
            self.spawn_particles(self.ball.x, self.ball.y, brick.color, 14 if destroyed else 8)

            if destroyed:
                self.score += 10 + self.combo * 2
                self.combo += 1
                self.spawn_powerup(brick)
                self.bricks.pop(hit_index)
            else:
                self.score += 4

            self.high_score = max(self.high_score, self.score)

        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.rect.top > HEIGHT:
                self.powerups.remove(powerup)
            elif powerup.rect.colliderect(self.paddle.rect):
                if powerup.kind == "expand":
                    self.paddle.grow()
                    self.message = "Paddle expanded!"
                else:
                    self.score += 75
                    self.message = "Bonus captured!"
                self.message_timer = FPS
                self.spawn_particles(powerup.rect.centerx, powerup.rect.centery, powerup.color, 16)
                self.powerups.remove(powerup)

        if not self.bricks:
            self.next_level()

        self.update_particles()
        if self.message_timer > 0:
            self.message_timer -= 1
        if self.shake_frames > 0:
            self.shake_frames -= 1

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

    def draw_background(self):
        self.screen.blit(self.background, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 12, 24, 170))
        self.screen.blit(overlay, (0, 0))

        for star in self.stars:
            pygame.draw.circle(self.screen, (255, 255, 255, 180), (star[0], star[1]), star[2])
            star[1] += star[2] * 0.4
            if star[1] > HEIGHT:
                star[0] = random.randint(0, WIDTH)
                star[1] = -5

    def draw_hud(self):
        hud = pygame.Rect(18, 16, WIDTH - 36, 58)
        pygame.draw.rect(self.screen, (20, 28, 54), hud, border_radius=18)
        pygame.draw.rect(self.screen, (74, 96, 140), hud, 2, border_radius=18)

        score_text = self.ui_font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.ui_font.render(f"Level: {self.level}", True, SKY)
        lives_text = self.ui_font.render(f"Lives: {self.lives}", True, GOLD)
        combo_text = self.small_font.render(f"Combo x{max(1, self.combo)}", True, MINT)

        self.screen.blit(score_text, (36, 28))
        self.screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 28))
        self.screen.blit(lives_text, (WIDTH - lives_text.get_width() - 38, 28))
        self.screen.blit(combo_text, (36, 56))

    def draw_message(self):
        if self.state == "playing" and self.message_timer <= 0:
            return
        text = self.subtitle_font.render(self.message, True, WHITE)
        panel = pygame.Rect(0, 0, text.get_width() + 36, 42)
        panel.center = (WIDTH // 2, HEIGHT - 24)
        pygame.draw.rect(self.screen, (20, 28, 54), panel, border_radius=16)
        pygame.draw.rect(self.screen, SKY, panel, 2, border_radius=16)
        self.screen.blit(text, text.get_rect(center=panel.center))

    def draw_intro(self):
        title = self.title_font.render("CRASH BREAKER", True, WHITE)
        subtitle = self.subtitle_font.render("Fast bricks, sharp rebounds, zero mercy.", True, GOLD)
        controls = self.small_font.render("Move: Left/Right or A/D   Launch: SPACE", True, WHITE)
        hint = self.small_font.render("Press SPACE to start", True, SKY)

        panel = pygame.Rect(0, 0, 560, 250)
        panel.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(self.screen, (17, 24, 45), panel, border_radius=26)
        pygame.draw.rect(self.screen, LAVENDER, panel, 2, border_radius=26)

        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 58)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 8)))
        self.screen.blit(controls, controls.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 44)))
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 92)))

    def draw_game_over(self):
        title = self.title_font.render("GAME OVER", True, CRIMSON)
        score_text = self.subtitle_font.render(f"Score: {self.score}", True, WHITE)
        high_score_text = self.subtitle_font.render(f"High Score: {self.high_score}", True, GOLD)
        hint = self.small_font.render("Press R to restart or Q to quit", True, SKY)

        panel = pygame.Rect(0, 0, 430, 220)
        panel.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(self.screen, (17, 24, 45), panel, border_radius=26)
        pygame.draw.rect(self.screen, CRIMSON, panel, 2, border_radius=26)

        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
        self.screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 12)))
        self.screen.blit(high_score_text, high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 48)))
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 92)))

    def draw(self):
        self.draw_background()

        shake_x = random.randint(-6, 6) if self.shake_frames > 0 else 0
        shake_y = random.randint(-4, 4) if self.shake_frames > 0 else 0
        arena = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for brick in self.bricks:
            brick.draw(arena)

        for powerup in self.powerups:
            powerup.draw(arena)

        self.paddle.draw(arena)
        self.ball.draw(arena)

        for particle in self.particles:
            particle.draw(arena)

        self.screen.blit(arena, (shake_x, shake_y))
        self.draw_hud()
        self.draw_message()

        if self.state == "intro":
            self.draw_intro()
        elif self.state == "game_over":
            self.draw_game_over()

        pygame.display.flip()

    def handle_keydown(self, key):
        if self.state == "intro" and key == pygame.K_SPACE:
            self.start_game()
        elif self.state == "playing" and key == pygame.K_SPACE and self.ball.attached:
            self.ball.launch()
            self.message = "Ball launched!"
            self.message_timer = FPS // 2
        elif self.state == "game_over" and key == pygame.K_r:
            high_score = self.high_score
            self.reset()
            self.high_score = high_score
        elif key == pygame.K_q:
            pygame.quit()
            sys.exit()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)

            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
