import math
import os
import random
import sys

import pygame


pygame.init()
pygame.mixer.init()


SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60

GRAVITY = 0.42
FLAP_FORCE = -9.2
BASE_SCROLL_SPEED = 4.5

WHITE = (245, 247, 255)
BLACK = (13, 17, 28)
NAVY = (17, 25, 47)
SKY = (100, 200, 255)
GOLD = (255, 210, 102)
CORAL = (255, 112, 92)
MINT = (124, 238, 195)
LAVENDER = (182, 160, 255)
SLATE = (134, 145, 176)
CRIMSON = (255, 74, 110)

ASSETS_DIR = "Assets"
BG_IMAGE = os.path.join(ASSETS_DIR, "Images\\bg-flappy.png")
BIRD_IMAGE = os.path.join(ASSETS_DIR, "Images\\bird-flappy.png")
PIPE_TOP_IMAGE = os.path.join(ASSETS_DIR, "Images\\pillar_top-flappy.png")
PIPE_BOTTOM_IMAGE = os.path.join(ASSETS_DIR, "Images\\pillar_bottom-flappy.png")
ENEMY_IMAGE = os.path.join(ASSETS_DIR, "Images\\enemy-flappy.png")
ENERGY_IMAGE = os.path.join(ASSETS_DIR, "Images\\energy.png")
INTRO_BANNER = os.path.join(ASSETS_DIR, "Images\\intro_banner-flappy.png")
GAME_OVER_BANNER = os.path.join(ASSETS_DIR, "Images\\gameover-image-flappy.png")

INTRO_SOUND = os.path.join(ASSETS_DIR, "Musics\\collid.wav")
GAME_OVER_SOUND = os.path.join(ASSETS_DIR, "Musics\\gameover-flappy.mp3")
FLAP_SOUND = os.path.join(ASSETS_DIR, "Musics\\jump-flappy.mp3")
SCORE_SOUND = os.path.join(ASSETS_DIR, "Musics\\collid.wav")
BG_MUSIC = os.path.join(ASSETS_DIR, "Musics\\bgmusic-flappy.mp3")


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


class Particle:
    def __init__(self, x, y, color):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.0, 4.2)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = random.randint(2, 5)
        self.life = random.randint(18, 34)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08
        self.life -= 1
        self.radius = max(1, self.radius - 0.05)

    def draw(self, screen):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))


class Bird:
    def __init__(self):
        self.x = 170
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.alive = True
        self.invincible_timer = 0

        self.width = 58
        self.height = 44

        self.rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height,
        )

        self.wing_phase = 0

    def reset(self):
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.alive = True
        self.invincible_timer = 90

        self.rect.center = (self.x, self.y)

    def flap(self, sound):
        if self.alive:
            self.velocity = FLAP_FORCE
            sound.play()

    def update(self):
        self.velocity += GRAVITY
        self.velocity = clamp(self.velocity, -12, 10)

        self.y += self.velocity

        self.rect.center = (self.x, int(self.y))

        self.wing_phase += 0.35

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        if self.y < 44:
            self.y = 44
            self.velocity = 0

        if self.y > SCREEN_HEIGHT - 20:
            self.alive = False

    def draw(self, screen):
        if self.invincible_timer > 0 and self.invincible_timer % 8 >= 4:
            return

        cx, cy = self.rect.center

        rotation = clamp(-self.velocity * 3.2, -35, 25)

        bird_surface = pygame.Surface((120, 120), pygame.SRCALPHA)

        local_x = 60
        local_y = 60

        glow_radius = 42

        pygame.draw.circle(
            bird_surface,
            (94, 198, 255, 50),
            (local_x, local_y),
            glow_radius,
        )

        wing_offset = math.sin(self.wing_phase) * 6

        pygame.draw.ellipse(
            bird_surface,
            (255, 210, 102),
            (local_x - 26, local_y - 18, 52, 36),
        )

        pygame.draw.ellipse(
            bird_surface,
            (255, 230, 160),
            (local_x - 18, local_y - 10, 22, 16),
        )

        pygame.draw.ellipse(
            bird_surface,
            (255, 180, 70),
            (
                local_x - 10,
                local_y - 6 + wing_offset,
                24,
                16,
            ),
        )

        pygame.draw.polygon(
            bird_surface,
            (255, 112, 92),
            [
                (local_x + 22, local_y),
                (local_x + 36, local_y - 5),
                (local_x + 36, local_y + 5),
            ],
        )

        pygame.draw.circle(
            bird_surface,
            WHITE,
            (local_x + 10, local_y - 6),
            5,
        )

        pygame.draw.circle(
            bird_surface,
            BLACK,
            (local_x + 11, local_y - 6),
            2,
        )

        rotated = pygame.transform.rotate(
            bird_surface,
            rotation,
        )

        rect = rotated.get_rect(center=(cx, cy))

        screen.blit(rotated, rect)

class Pipe:
    WIDTH = 96

    def __init__(self, x, speed, level):
        self.x = x
        self.speed = speed
        self.level = level

        self.gap = max(155, 220 - level * 6)

        self.top_height = random.randint(
            80,
            SCREEN_HEIGHT - self.gap - 180,
        )

        self.bottom_y = self.top_height + self.gap
        self.bottom_height = SCREEN_HEIGHT - self.bottom_y

        self.top_rect = pygame.Rect(
            self.x - self.WIDTH // 2,
            0,
            self.WIDTH,
            self.top_height,
        )

        self.bottom_rect = pygame.Rect(
            self.x - self.WIDTH // 2,
            self.bottom_y,
            self.WIDTH,
            self.bottom_height,
        )

        self.passed = False

        self.glow_phase = random.uniform(0, math.tau)

    def update(self):
        self.x -= self.speed

        self.top_rect.centerx = int(self.x)
        self.bottom_rect.centerx = int(self.x)

        self.glow_phase += 0.03

    def collide(self, bird):
        return (
            self.top_rect.colliderect(bird.rect)
            or self.bottom_rect.colliderect(bird.rect)
        )

    def draw_pipe_segment(self, screen, rect, top_pipe=True):
        glow_strength = (
            70 + int(math.sin(self.glow_phase) * 25)
        )

        glow_rect = rect.inflate(28, 28)

        glow_surface = pygame.Surface(
            (glow_rect.width, glow_rect.height),
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            glow_surface,
            (94, 198, 255, glow_strength),
            glow_surface.get_rect(),
            border_radius=20,
        )

        screen.blit(
            glow_surface,
            glow_rect.topleft,
        )

        pygame.draw.rect(
            screen,
            (32, 48, 92),
            rect,
            border_radius=12,
        )

        inner = rect.inflate(-12, 0)

        pygame.draw.rect(
            screen,
            (72, 220, 255),
            inner,
            border_radius=10,
        )

        highlight = pygame.Rect(
            inner.x + 6,
            inner.y + 6,
            10,
            inner.height - 12,
        )

        pygame.draw.rect(
            screen,
            (190, 245, 255),
            highlight,
            border_radius=6,
        )

        cap_height = 24

        if top_pipe:
            cap_rect = pygame.Rect(
                rect.x - 8,
                rect.bottom - cap_height,
                rect.width + 16,
                cap_height,
            )
        else:
            cap_rect = pygame.Rect(
                rect.x - 8,
                rect.y,
                rect.width + 16,
                cap_height,
            )

        pygame.draw.rect(
            screen,
            (110, 235, 255),
            cap_rect,
            border_radius=10,
        )

        pygame.draw.rect(
            screen,
            WHITE,
            cap_rect,
            2,
            border_radius=10,
        )

    def draw(self, screen):
        self.draw_pipe_segment(
            screen,
            self.top_rect,
            True,
        )

        self.draw_pipe_segment(
            screen,
            self.bottom_rect,
            False,
        )

class Enemy:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

        self.wave = random.uniform(0, math.tau)

        self.size = 56

        self.rect = pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size,
        )

        self.rotation = random.uniform(0, 360)

    def update(self):
        self.x -= self.speed

        self.wave += 0.06
        self.rotation += 2

        self.y += math.sin(self.wave) * 1.8

        self.rect.center = (
            int(self.x),
            int(self.y),
        )

    def collide(self, bird):
        return self.rect.colliderect(bird.rect)

    def draw(self, screen):
        cx, cy = self.rect.center

        pulse = (
            70
            + int(
                math.sin(
                    pygame.time.get_ticks() * 0.008
                )
                * 20
            )
        )

        glow_surface = pygame.Surface(
            (120, 120),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            glow_surface,
            (255, 70, 105, pulse),
            (60, 60),
            38,
        )

        screen.blit(
            glow_surface,
            (
                cx - 60,
                cy - 60,
            ),
        )

        drone_surface = pygame.Surface(
            (100, 100),
            pygame.SRCALPHA,
        )

        center = (50, 50)

        pygame.draw.circle(
            drone_surface,
            (255, 70, 105),
            center,
            18,
        )

        pygame.draw.circle(
            drone_surface,
            WHITE,
            center,
            6,
        )

        pygame.draw.circle(
            drone_surface,
            NAVY,
            center,
            2,
        )

        ring_rect = pygame.Rect(
            20,
            20,
            60,
            60,
        )

        pygame.draw.ellipse(
            drone_surface,
            (255, 130, 150),
            ring_rect,
            4,
        )

        pygame.draw.line(
            drone_surface,
            (255, 180, 200),
            (50, 10),
            (50, 90),
            2,
        )

        pygame.draw.line(
            drone_surface,
            (255, 180, 200),
            (10, 50),
            (90, 50),
            2,
        )

        rotated = pygame.transform.rotate(
            drone_surface,
            self.rotation,
        )

        rect = rotated.get_rect(
            center=(cx, cy)
        )

        screen.blit(
            rotated,
            rect,
        )

class Energy:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

        self.float_angle = random.uniform(0, math.tau)

        self.size = 40

        self.rect = pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size,
        )

        self.collected = False

        self.rotation = random.uniform(0, 360)

    def update(self):
        self.x -= self.speed

        self.float_angle += 0.08
        self.rotation += 1.5

        self.y += math.sin(self.float_angle) * 1.2

        self.rect.center = (
            int(self.x),
            int(self.y),
        )

    def collide(self, bird):
        if (
            not self.collected
            and self.rect.colliderect(bird.rect)
        ):
            self.collected = True
            return True

        return False

    def draw(self, screen):
        if self.collected:
            return

        cx, cy = self.rect.center

        pulse = (
            90
            + int(
                math.sin(
                    pygame.time.get_ticks() * 0.01
                )
                * 40
            )
        )

        glow = pygame.Surface(
            (90, 90),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            glow,
            (124, 238, 195, pulse),
            (45, 45),
            30,
        )

        screen.blit(
            glow,
            (
                cx - 45,
                cy - 45,
            ),
        )

        crystal = pygame.Surface(
            (80, 80),
            pygame.SRCALPHA,
        )

        points = [
            (40, 12),
            (62, 40),
            (40, 68),
            (18, 40),
        ]

        pygame.draw.polygon(
            crystal,
            (124, 238, 195),
            points,
        )

        pygame.draw.polygon(
            crystal,
            WHITE,
            points,
            2,
        )

        pygame.draw.line(
            crystal,
            (220, 255, 240),
            (40, 12),
            (40, 68),
            2,
        )

        pygame.draw.line(
            crystal,
            (220, 255, 240),
            (18, 40),
            (62, 40),
            2,
        )

        pygame.draw.circle(
            crystal,
            WHITE,
            (40, 40),
            4,
        )

        rotated = pygame.transform.rotate(
            crystal,
            self.rotation,
        )

        rect = rotated.get_rect(
            center=(cx, cy)
        )

        screen.blit(
            rotated,
            rect,
        )

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sky Survivor Deluxe")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("arialblack", 48)
        self.heading_font = pygame.font.SysFont("arial", 28, bold=True)
        self.ui_font = pygame.font.SysFont("arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("arial", 18)

        self.background = pygame.image.load(BG_IMAGE).convert()
        self.background = pygame.transform.smoothscale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.intro_banner = pygame.image.load(INTRO_BANNER).convert_alpha()
        self.game_over_banner = pygame.image.load(GAME_OVER_BANNER).convert_alpha()

        self.intro_sound = pygame.mixer.Sound(INTRO_SOUND)
        self.game_over_sound = pygame.mixer.Sound(GAME_OVER_SOUND)
        self.flap_sound = pygame.mixer.Sound(FLAP_SOUND)
        self.score_sound = pygame.mixer.Sound(SCORE_SOUND)

        pygame.mixer.music.load(BG_MUSIC)
        pygame.mixer.music.set_volume(0.16)
        pygame.mixer.music.play(-1)

        self.high_score = 0
        self.clouds = [
            [random.randint(0, SCREEN_WIDTH), random.randint(60, SCREEN_HEIGHT - 80), random.randint(80, 180), random.uniform(0.4, 1.1)]
            for _ in range(8)
        ]
        self.reset_game()

    def reset_game(self):
        self.hit_flash = 0
        self.state = "intro"
        self.bird = Bird()
        self.bird.reset()
        self.pipes = []
        self.enemies = []
        self.energies = []
        self.particles = []
        self.score = 0
        self.level = 1
        self.lives = 3
        self.combo = 0
        self.distance = 0
        self.pipe_timer = 0
        self.enemy_timer = 0
        self.energy_timer = 0
        self.shake_frames = 0
        self.message = "Press SPACE to start flying"
        self.message_timer = FPS * 2

    def start_run(self):
        self.state = "playing"
        self.message = "Stay sharp. Dodge, survive, collect energy."
        self.message_timer = FPS * 2
        self.intro_sound.play()

    def current_scroll_speed(self):
        return BASE_SCROLL_SPEED + self.level * 0.35


    def spawn_particles(
    self,
    x,
    y,
    color,
    count=18,
    ):
        for _ in range(count):

            particle = Particle(
                x,
                y,
                color,
            )

            particle.vx *= random.uniform(
                0.8,
                1.8,
            )

            particle.vy *= random.uniform(
                0.8,
                1.8,
            )

            particle.life = random.randint(
                24,
                48,
            )

            self.particles.append(
                particle
            )

    def take_hit(self):
        if self.bird.invincible_timer > 0:
            return

        self.lives -= 1

        self.combo = 0

        self.bird.invincible_timer = 120

        self.shake_frames = 28

        self.hit_flash = 18

        self.spawn_particles(
            self.bird.rect.centerx,
            self.bird.rect.centery,
            CRIMSON,
            40,
        )

        if self.lives <= 0:

            self.high_score = max(
                self.high_score,
                self.score,
            )

            self.game_over_sound.play()

            self.state = "game_over"

            self.message = (
                "Press R to restart"
            )

        else:

            self.message = (
                f"Hit Taken! "
                f"{self.lives} Lives Left"
            )

            self.message_timer = FPS * 2


    def game_over(self):
        if self.state != "game_over":
            self.high_score = max(self.high_score, self.score)
            self.game_over_sound.play()
            self.state = "game_over"
            self.message = "Press R to restart"

    def update_level(self):
        self.level = min(9, 1 + self.score // 10)

    def update_objects(self):
        speed = self.current_scroll_speed()

        self.pipe_timer += 1
        if self.pipe_timer >= max(72, 110 - self.level * 4):
            self.pipes.append(Pipe(SCREEN_WIDTH + 80, speed, self.level))
            self.pipe_timer = 0

        self.enemy_timer += 1
        if self.enemy_timer >= max(150, 230 - self.level * 10):
            y = random.randint(100, SCREEN_HEIGHT - 180)
            self.enemies.append(Enemy(SCREEN_WIDTH + 60, y, speed + 1.4))
            self.enemy_timer = 0

        self.energy_timer += 1
        if self.energy_timer >= 210:
            y = random.randint(110, SCREEN_HEIGHT - 170)
            self.energies.append(Energy(SCREEN_WIDTH + 40, y, speed - 1.2))
            self.energy_timer = 0

        for pipe in self.pipes[:]:
            pipe.update()
            if pipe.x < -120:
                self.pipes.remove(pipe)
            elif not pipe.passed and pipe.x < self.bird.x:
                pipe.passed = True
                self.score += 1
                self.combo += 1
                self.score_sound.play()
                self.spawn_particles(self.bird.x + 20, self.bird.y, GOLD, 8)

        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.x < -100:
                self.enemies.remove(enemy)

        for energy in self.energies[:]:
            energy.update()
            if energy.x < -80:
                self.energies.remove(energy)
            elif energy.collide(self.bird):
                self.score += 3
                self.lives = min(5, self.lives + 1) if self.score % 15 == 0 else self.lives
                self.message = "Energy collected!"
                self.message_timer = FPS
                self.spawn_particles(energy.rect.centerx, energy.rect.centery, MINT, 16)
                self.energies.remove(energy)

    def check_collisions(self):
        for pipe in self.pipes:
            if pipe.collide(self.bird):
                self.take_hit()
                break

        for enemy in self.enemies:
            if enemy.collide(self.bird):
                self.take_hit()
                break

        if not self.bird.alive:
            self.game_over()

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

    def update(self):
        if self.state == "playing":
            self.bird.update()
            self.update_objects()
            self.check_collisions()
            self.update_level()
            self.high_score = max(self.high_score, self.score)
            self.distance += self.current_scroll_speed()

        self.update_particles()

        if self.message_timer > 0:
            self.message_timer -= 1
        if self.shake_frames > 0:
            self.shake_frames -= 1

    def draw_background(self):
        self.screen.fill(BLACK)

        for y in range(SCREEN_HEIGHT):
            blend = y / SCREEN_HEIGHT

            color = (
                int(8 + blend * 10),
                int(12 + blend * 22),
                int(24 + blend * 36),
            )

            pygame.draw.line(
                self.screen,
                color,
                (0, y),
                (SCREEN_WIDTH, y),
            )

        if not hasattr(self, "stars"):
            self.stars = [
                [
                    random.randint(0, SCREEN_WIDTH),
                    random.randint(0, SCREEN_HEIGHT),
                    random.choice([1, 2]),
                    random.uniform(0.1, 0.5),
                ]
                for _ in range(120)
            ]

        for star in self.stars:
            star[1] += star[3]

            if star[1] > SCREEN_HEIGHT:
                star[0] = random.randint(0, SCREEN_WIDTH)
                star[1] = -5

            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                (int(star[0]), int(star[1])),
                star[2],
            )

        if not hasattr(self, "mountain_offset"):
            self.mountain_offset = 0

        self.mountain_offset += 0.35

        for i in range(-2, 8):
            x = i * 180 - (self.mountain_offset % 180)

            pygame.draw.polygon(
                self.screen,
                (18, 28, 52),
                [
                    (x, SCREEN_HEIGHT),
                    (x + 90, SCREEN_HEIGHT - 160),
                    (x + 180, SCREEN_HEIGHT),
                ],
            )

        for cloud in self.clouds:
            cloud[0] -= cloud[3]

            if cloud[0] < -220:
                cloud[0] = SCREEN_WIDTH + random.randint(20, 140)
                cloud[1] = random.randint(
                    60,
                    SCREEN_HEIGHT - 80,
                )

            surf = pygame.Surface(
                (cloud[2], 60),
                pygame.SRCALPHA,
            )

            pygame.draw.ellipse(
                surf,
                (255, 255, 255, 35),
                (0, 15, cloud[2], 25),
            )

            pygame.draw.ellipse(
                surf,
                (255, 255, 255, 20),
                (20, 0, cloud[2] - 40, 35),
            )

            self.screen.blit(
                surf,
                (cloud[0], cloud[1]),
            )

    def draw_hud(self):
        hud = pygame.Rect(
            18,
            16,
            SCREEN_WIDTH - 36,
            66,
        )

        pygame.draw.rect(
            self.screen,
            (18, 27, 51),
            hud,
            border_radius=20,
        )

        pygame.draw.rect(
            self.screen,
            (88, 108, 156),
            hud,
            2,
            border_radius=20,
        )

        score_text = self.ui_font.render(
            f"Score: {self.score}",
            True,
            WHITE,
        )

        level_text = self.ui_font.render(
            f"Level: {self.level}",
            True,
            SKY,
        )

        lives_text = self.ui_font.render(
            f"Lives: {self.lives}",
            True,
            GOLD,
        )

        combo_multiplier = max(
            1,
            self.combo,
        )

        combo_text = self.small_font.render(
            f"Combo x{combo_multiplier}",
            True,
            MINT,
        )

        self.screen.blit(
            score_text,
            (34, 28),
        )

        self.screen.blit(
            combo_text,
            (34, 55),
        )

        self.screen.blit(
            level_text,
            level_text.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    40,
                )
            ),
        )

        self.screen.blit(
            lives_text,
            (
                SCREEN_WIDTH
                - lives_text.get_width()
                - 36,
                28,
            ),
        )

        for i in range(self.lives):
            x = (
                SCREEN_WIDTH
                - 180
                + i * 26
            )

            y = 58

            pygame.draw.circle(
                self.screen,
                GOLD,
                (x, y),
                8,
            )

            pygame.draw.circle(
                self.screen,
                WHITE,
                (x - 2, y - 2),
                2,
            )

        if self.level >= 5:
            level_bar = pygame.Rect(
                SCREEN_WIDTH // 2 - 100,
                58,
                200,
                8,
            )

            pygame.draw.rect(
                self.screen,
                (40, 55, 90),
                level_bar,
                border_radius=4,
            )

            fill = level_bar.copy()

            fill.width = int(
                (self.score % 10)
                / 10
                * level_bar.width
            )

            pygame.draw.rect(
                self.screen,
                SKY,
                fill,
                border_radius=4,
            )

    def draw_message(self):

        if (
            self.message_timer <= 0
            and self.state == "playing"
        ):
            return

        pulse = (
            math.sin(
                pygame.time.get_ticks()
                * 0.008
            )
            * 4
        )

        text = self.small_font.render(
            self.message,
            True,
            WHITE,
        )

        panel = pygame.Rect(
            0,
            0,
            text.get_width() + 48,
            42,
        )

        panel.center = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 30 + pulse,
        )

        glow = pygame.Surface(
            (
                panel.width + 24,
                panel.height + 24,
            ),
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            glow,
            (94, 198, 255, 25),
            glow.get_rect(),
            border_radius=18,
        )

        self.screen.blit(
            glow,
            glow.get_rect(
                center=panel.center
            ),
        )

        pygame.draw.rect(
            self.screen,
            (18, 27, 51),
            panel,
            border_radius=16,
        )

        pygame.draw.rect(
            self.screen,
            SKY,
            panel,
            2,
            border_radius=16,
        )

        self.screen.blit(
            text,
            text.get_rect(
                center=panel.center
            ),
        )

    def draw_intro(self):
        panel = pygame.Rect(
            0,
            0,
            640,
            320,
        )

        panel.center = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
        )

        pygame.draw.rect(
            self.screen,
            (15, 23, 44),
            panel,
            border_radius=30,
        )

        pygame.draw.rect(
            self.screen,
            LAVENDER,
            panel,
            2,
            border_radius=30,
        )

        glow = pygame.Surface(
            (700, 380),
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            glow,
            (184, 156, 255, 25),
            glow.get_rect(),
            border_radius=40,
        )

        self.screen.blit(
            glow,
            glow.get_rect(
                center=panel.center
            ),
        )

        title = self.title_font.render(
            "SKY SURVIVOR",
            True,
            WHITE,
        )

        subtitle = self.heading_font.render(
            "Neon Edition",
            True,
            GOLD,
        )

        controls = self.small_font.render(
            "SPACE = Start / Fly",
            True,
            WHITE,
        )

        controls2 = self.small_font.render(
            "P = Pause     R = Restart",
            True,
            WHITE,
        )

        hint = self.small_font.render(
            "Collect energy. Avoid enemies.",
            True,
            SKY,
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 80,
                )
            ),
        )

        self.screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 25,
                )
            ),
        )

        self.screen.blit(
            controls,
            controls.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 40,
                )
            ),
        )

        self.screen.blit(
            controls2,
            controls2.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 75,
                )
            ),
        )

        self.screen.blit(
            hint,
            hint.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 125,
                )
            ),
        )

    def draw_game_over(self):
        panel = pygame.Rect(
            0,
            0,
            520,
            260,
        )

        panel.center = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
        )

        pygame.draw.rect(
            self.screen,
            (15, 23, 44),
            panel,
            border_radius=30,
        )

        pygame.draw.rect(
            self.screen,
            CRIMSON,
            panel,
            2,
            border_radius=30,
        )

        title = self.title_font.render(
            "GAME OVER",
            True,
            CRIMSON,
        )

        score_text = self.heading_font.render(
            f"Score : {self.score}",
            True,
            WHITE,
        )

        best_text = self.heading_font.render(
            f"Best : {self.high_score}",
            True,
            GOLD,
        )

        hint = self.small_font.render(
            "Press R to Restart",
            True,
            SKY,
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 65,
                )
            ),
        )

        self.screen.blit(
            score_text,
            score_text.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 15,
                )
            ),
        )

        self.screen.blit(
            best_text,
            best_text.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 55,
                )
            ),
        )

        self.screen.blit(
            hint,
            hint.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 105,
                )
            ),
        )

    def draw_pause(self):
        panel = pygame.Rect(
            0,
            0,
            420,
            180,
        )

        panel.center = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
        )

        glow = pygame.Surface(
            (520, 280),
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            glow,
            (255, 211, 105, 20),
            glow.get_rect(),
            border_radius=40,
        )

        self.screen.blit(
            glow,
            glow.get_rect(
                center=panel.center
            ),
        )

        pygame.draw.rect(
            self.screen,
            (17, 24, 45),
            panel,
            border_radius=28,
        )

        pygame.draw.rect(
            self.screen,
            GOLD,
            panel,
            2,
            border_radius=28,
        )

        title = self.heading_font.render(
            "PAUSED",
            True,
            GOLD,
        )

        hint = self.small_font.render(
            "Press P to Continue",
            True,
            WHITE,
        )

        info = self.small_font.render(
            f"Score: {self.score}",
            True,
            SKY,
        )

        self.screen.blit(
            title,
            title.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 35,
                )
            ),
        )

        self.screen.blit(
            info,
            info.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 10,
                )
            ),
        )

        self.screen.blit(
            hint,
            hint.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 55,
                )
            ),
        )
        

    def draw(self):

        self.draw_background()

        shake_x = (
            random.randint(-7, 7)
            if self.shake_frames > 0
            else 0
        )

        shake_y = (
            random.randint(-5, 5)
            if self.shake_frames > 0
            else 0
        )

        layer = pygame.Surface(
            (
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
            ),
            pygame.SRCALPHA,
        )

        for pipe in self.pipes:
            pipe.draw(layer)

        for enemy in self.enemies:
            enemy.draw(layer)

        for energy in self.energies:
            energy.draw(layer)

        for particle in self.particles:
            particle.draw(layer)

        self.bird.draw(layer)

        self.screen.blit(
            layer,
            (
                shake_x,
                shake_y,
            ),
        )

        if self.hit_flash > 0:

            flash = pygame.Surface(
                (
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT,
                ),
                pygame.SRCALPHA,
            )

            flash.fill(
                (
                    255,
                    60,
                    60,
                    self.hit_flash * 8,
                )
            )

            self.screen.blit(
                flash,
                (0, 0),
            )

            self.hit_flash -= 1

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
            self.start_run()
            return

        if key == pygame.K_p and self.state in ("playing", "paused"):
            self.state = "paused" if self.state == "playing" else "playing"
            self.message = "Paused" if self.state == "paused" else "Back in the sky"
            self.message_timer = FPS
            return

        if self.state == "playing" and key == pygame.K_SPACE:
            self.bird.flap(self.flap_sound)
            self.spawn_particles(self.bird.rect.left, self.bird.rect.centery, SKY, 6)
            return

        if self.state == "game_over" and key == pygame.K_r:
            self.reset_game()

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
