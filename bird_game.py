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
        original = pygame.image.load(BIRD_IMAGE).convert_alpha()
        self.image = pygame.transform.smoothscale(original, (58, 44))
        self.x = 170
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.alive = True
        self.invincible_timer = 0
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def reset(self):
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.alive = True
        self.invincible_timer = 90
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def flap(self, sound):
        if self.alive:
            self.velocity = FLAP_FORCE
            sound.play()

    def update(self):
        self.velocity += GRAVITY
        self.velocity = clamp(self.velocity, -12, 10)
        self.y += self.velocity
        self.rect.center = (self.x, int(self.y))

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        if self.y < 44:
            self.y = 44
            self.velocity = 0

        if self.y > SCREEN_HEIGHT - 20:
            self.alive = False

    def draw(self, screen):
        rotation = clamp(-self.velocity * 3.2, -35, 25)
        sprite = pygame.transform.rotate(self.image, rotation)
        draw_rect = sprite.get_rect(center=self.rect.center)
        glow = pygame.Surface((draw_rect.width + 24, draw_rect.height + 24), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (98, 205, 255, 90), glow.get_rect())
        screen.blit(glow, glow.get_rect(center=self.rect.center))

        if self.invincible_timer == 0 or self.invincible_timer % 8 < 4:
            screen.blit(sprite, draw_rect)


class Pipe:
    def __init__(self, x, speed, level):
        self.x = x
        self.speed = speed
        self.level = level
        self.gap = max(155, 220 - level * 6)
        self.top_height = random.randint(80, SCREEN_HEIGHT - self.gap - 180)
        top_original = pygame.image.load(PIPE_TOP_IMAGE).convert_alpha()
        bottom_original = pygame.image.load(PIPE_BOTTOM_IMAGE).convert_alpha()
        self.top_image = pygame.transform.smoothscale(top_original, (96, self.top_height))
        bottom_height = SCREEN_HEIGHT - (self.top_height + self.gap) 
        self.bottom_image = pygame.transform.smoothscale(bottom_original, (96, bottom_height))
        self.top_rect = self.top_image.get_rect(midbottom=(self.x, self.top_height))
        self.bottom_rect = self.bottom_image.get_rect(midtop=(self.x, self.top_height + self.gap))
        self.passed = False

    def update(self):
        self.x -= self.speed
        self.top_rect.centerx = int(self.x)
        self.bottom_rect.centerx = int(self.x)

    def collide(self, bird):
        return self.top_rect.colliderect(bird.rect) or self.bottom_rect.colliderect(bird.rect)

    def draw(self, screen):
        screen.blit(self.top_image, self.top_rect)
        screen.blit(self.bottom_image, self.bottom_rect)


class Enemy:
    def __init__(self, x, y, speed):
        original = pygame.image.load(ENEMY_IMAGE).convert_alpha()
        self.image = pygame.transform.smoothscale(original, (56, 56))
        self.x = x
        self.y = y
        self.speed = speed
        self.wave = random.uniform(0, math.tau)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.x -= self.speed
        self.wave += 0.06
        self.y += math.sin(self.wave) * 1.8
        self.rect.center = (int(self.x), int(self.y))

    def collide(self, bird):
        return self.rect.colliderect(bird.rect)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Energy:
    def __init__(self, x, y, speed):
        original = pygame.image.load(ENERGY_IMAGE).convert_alpha()
        self.image = pygame.transform.smoothscale(original, (40, 40))
        self.x = x
        self.y = y
        self.speed = speed
        self.float_angle = random.uniform(0, math.tau)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.collected = False

    def update(self):
        self.x -= self.speed
        self.float_angle += 0.08
        self.y += math.sin(self.float_angle) * 1.2
        self.rect.center = (int(self.x), int(self.y))

    def collide(self, bird):
        if not self.collected and self.rect.colliderect(bird.rect):
            self.collected = True
            return True
        return False

    def draw(self, screen):
        if not self.collected:
            glow = pygame.Surface((68, 68), pygame.SRCALPHA)
            pygame.draw.circle(glow, (123, 239, 193, 95), (34, 34), 30)
            screen.blit(glow, glow.get_rect(center=self.rect.center))
            screen.blit(self.image, self.rect)


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

    def spawn_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def take_hit(self):
        if self.bird.invincible_timer > 0:
            return
        self.lives -= 1
        self.combo = 0
        self.bird.invincible_timer = 110
        self.shake_frames = 14
        self.spawn_particles(self.bird.rect.centerx, self.bird.rect.centery, CORAL, 22)
        if self.lives <= 0:
            self.high_score = max(self.high_score, self.score)
            self.game_over_sound.play()
            self.state = "game_over"
            self.message = "Press R to restart"
        else:
            self.message = f"Hit taken. {self.lives} lives left"
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
        self.screen.blit(self.background, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 16, 34, 138))
        self.screen.blit(overlay, (0, 0))

        for cloud in self.clouds:
            cloud[0] -= cloud[3]
            if cloud[0] < -220:
                cloud[0] = SCREEN_WIDTH + random.randint(20, 140)
                cloud[1] = random.randint(60, SCREEN_HEIGHT - 80)
            cloud_surface = pygame.Surface((cloud[2], 54), pygame.SRCALPHA)
            pygame.draw.ellipse(cloud_surface, (255, 255, 255, 35), (0, 10, cloud[2], 28))
            pygame.draw.ellipse(cloud_surface, (255, 255, 255, 25), (16, 0, cloud[2] - 30, 34))
            self.screen.blit(cloud_surface, (cloud[0], cloud[1]))

    def draw_hud(self):
        hud = pygame.Rect(18, 16, SCREEN_WIDTH - 36, 62)
        pygame.draw.rect(self.screen, (18, 27, 51), hud, border_radius=18)
        pygame.draw.rect(self.screen, (88, 108, 156), hud, 2, border_radius=18)

        score_text = self.ui_font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.ui_font.render(f"Level: {self.level}", True, SKY)
        lives_text = self.ui_font.render(f"Lives: {self.lives}", True, GOLD)
        combo_text = self.small_font.render(f"Combo x{max(1, self.combo)}", True, MINT)

        self.screen.blit(score_text, (36, 29))
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 29))
        self.screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 38, 29))
        self.screen.blit(combo_text, (36, 56))

    def draw_message(self):
        if self.message_timer <= 0 and self.state == "playing":
            return
        text = self.small_font.render(self.message, True, WHITE)
        panel = pygame.Rect(0, 0, text.get_width() + 36, 38)
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 28)
        pygame.draw.rect(self.screen, (18, 27, 51), panel, border_radius=16)
        pygame.draw.rect(self.screen, SKY, panel, 2, border_radius=16)
        self.screen.blit(text, text.get_rect(center=panel.center))

    def draw_intro(self):
        panel = pygame.Rect(0, 0, 610, 290)
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, (17, 24, 45), panel, border_radius=28)
        pygame.draw.rect(self.screen, LAVENDER, panel, 2, border_radius=28)

        title = self.title_font.render("SKY SURVIVOR", True, WHITE)
        subtitle = self.heading_font.render("Dodge pipes. Outsmart enemies. Own the sky.", True, GOLD)
        controls = self.small_font.render("SPACE = flap/start    R = restart after defeat", True, WHITE)
        prompt = self.small_font.render("Press SPACE to begin", True, SKY)

        banner = pygame.transform.smoothscale(self.intro_banner, (270, 86))
        self.screen.blit(banner, banner.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 82)))
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 34)))
        self.screen.blit(controls, controls.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 86)))
        self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 128)))

    def draw_game_over(self):
        panel = pygame.Rect(0, 0, 500, 250)
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, (17, 24, 45), panel, border_radius=28)
        pygame.draw.rect(self.screen, CRIMSON, panel, 2, border_radius=28)

        banner = pygame.transform.smoothscale(self.game_over_banner, (260, 84))
        self.screen.blit(banner, banner.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 72)))

        score_text = self.heading_font.render(f"Score: {self.score}", True, WHITE)
        high_score_text = self.heading_font.render(f"High Score: {self.high_score}", True, GOLD)
        hint = self.small_font.render("Press R to restart or Q to quit", True, SKY)

        self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))
        self.screen.blit(high_score_text, high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 56)))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 106)))

    def draw(self):
        self.draw_background()

        shake_x = random.randint(-5, 5) if self.shake_frames > 0 else 0
        shake_y = random.randint(-4, 4) if self.shake_frames > 0 else 0
        layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        for pipe in self.pipes:
            pipe.draw(layer)
        for enemy in self.enemies:
            enemy.draw(layer)
        for energy in self.energies:
            energy.draw(layer)
        for particle in self.particles:
            particle.draw(layer)
        self.bird.draw(layer)

        self.screen.blit(layer, (shake_x, shake_y))
        self.draw_hud()
        self.draw_message()

        if self.state == "intro":
            self.draw_intro()
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
