import pygame
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker Game")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Clock
clock = pygame.time.Clock()

# Paddle settings
platform_width = 100
platform_height = 10
platform_position = [WIDTH // 2 - platform_width // 2, HEIGHT - 40]
platform_speed = 7

# Ball settings
ball_radius = 8
ball_position = [WIDTH // 2, HEIGHT // 2]
ball_speed = [4, -4]

# Score
score = 0
font = pygame.font.SysFont(None, 36)
brick_sound = pygame.mixer.Sound("Assets/collid.wav")
gameover_sound = pygame.mixer.Sound("Assets/collideout.wav")

# Brick class
class Brick:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 20)
        self.is_broken = False

# Create bricks
bricks = []
rows = 5
cols = 10
brick_width = 60
brick_height = 20
padding = 10
offset_x = 35
offset_y = 50

for row in range(rows):
    for col in range(cols):
        x = offset_x + col * (brick_width + padding)
        y = offset_y + row * (brick_height + padding)
        bricks.append(Brick(x, y))

# theme music
pygame.mixer.music.load("Assets/bgmusic.mp3")
pygame.mixer.music.set_volume(0.2)  # 0.0 se 1.0 tak volume
pygame.mixer.music.play(-1) # infinite music

# Game loop
running = True
while running:
    clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and platform_position[0] > 0:
        platform_position[0] -= platform_speed
    if keys[pygame.K_RIGHT] and platform_position[0] < WIDTH - platform_width:
        platform_position[0] += platform_speed

    # Ball movement
    ball_position[0] += ball_speed[0]
    ball_position[1] += ball_speed[1]

    # Wall collision (left & right)
    if ball_position[0] - ball_radius <= 0 or ball_position[0] + ball_radius >= WIDTH:
        ball_speed[0] = -ball_speed[0]

    # Top wall collision
    if ball_position[1] - ball_radius <= 0:
        ball_speed[1] = -ball_speed[1]

    # Bottom wall (Game Over reset)
    if ball_position[1] + ball_radius >= HEIGHT:
        gameover_sound.play()
        ball_position = [WIDTH // 2, HEIGHT // 2]
        ball_speed = [4, -4]
        score = 0

    # Paddle collision
    if (platform_position[0] <= ball_position[0] <= platform_position[0] + platform_width and
        platform_position[1] <= ball_position[1] + ball_radius <= platform_position[1] + platform_height):
        ball_speed[1] = -ball_speed[1]

    # Brick collision
    for brick in bricks[:]:
        ball_rect = pygame.Rect(ball_position[0] - ball_radius,
                                ball_position[1] - ball_radius,
                                ball_radius * 2,
                                ball_radius * 2)        

        if not brick.is_broken and brick.rect.colliderect(ball_rect):
            brick.is_broken = True
            score += 1
            ball_speed[1] = -ball_speed[1]
            bricks.remove(brick)
            brick_sound.play()

    # Draw paddle
    pygame.draw.rect(screen, BLUE,
                     (platform_position[0], platform_position[1],
                      platform_width, platform_height))

    # Draw ball
    pygame.draw.circle(screen, WHITE,
                       (int(ball_position[0]), int(ball_position[1])),
                       ball_radius)

    # Draw bricks
    for brick in bricks:
        if not brick.is_broken:
            pygame.draw.rect(screen, RED, brick.rect)

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
