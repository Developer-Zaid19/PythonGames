import subprocess
import sys

import pygame


pygame.init()


WIDTH = 960
HEIGHT = 640
FPS = 60

WHITE = (245, 247, 255)
BLACK = (8, 11, 20)
PANEL = (19, 28, 52)
PANEL_LINE = (72, 92, 132)
SKY = (94, 198, 255)
GOLD = (255, 211, 105)
MINT = (112, 238, 190)
CRIMSON = (255, 70, 105)
SLATE = (143, 154, 185)


GAMES = [
    {
        "title": "Sky Survivor",
        "file": "birdgame.py",
        "tagline": "Dodge pipes and enemies in the sky.",
        "color": SKY,
    },
    {
        "title": "Crash Breaker",
        "file": "crashbreak_game.py",
        "tagline": "Break bricks with sharp rebounds.",
        "color": GOLD,
    },
    {
        "title": "Neon Snake Rush",
        "file": "snake_game.py",
        "tagline": "Eat points, grow longer, chase red bonuses.",
        "color": MINT,
    },
]


class Launcher:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Python Games Arcade")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("arialblack", 48)
        self.heading_font = pygame.font.SysFont("arial", 27, bold=True)
        self.ui_font = pygame.font.SysFont("arial", 20, bold=True)
        self.small_font = pygame.font.SysFont("arial", 16)
        self.selected = 0
        self.cards = []

    def launch_selected(self):
        pygame.quit()
        subprocess.run([sys.executable, GAMES[self.selected]["file"]], check=False)
        sys.exit()

    def draw_background(self):
        self.screen.fill(BLACK)
        for y in range(HEIGHT):
            blend = y / HEIGHT
            color = (int(8 + blend * 8), int(11 + blend * 18), int(20 + blend * 30))
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

        for x in range(0, WIDTH, 48):
            pygame.draw.line(self.screen, (25, 36, 62), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 48):
            pygame.draw.line(self.screen, (25, 36, 62), (0, y), (WIDTH, y))

    def draw_card(self, index, rect):
        game = GAMES[index]
        selected = index == self.selected
        color = game["color"]
        fill = (24, 36, 66) if selected else PANEL
        border = color if selected else PANEL_LINE

        pygame.draw.rect(self.screen, fill, rect, border_radius=18)
        pygame.draw.rect(self.screen, border, rect, 3 if selected else 2, border_radius=18)

        number = self.ui_font.render(str(index + 1), True, BLACK)
        badge = pygame.Rect(rect.x + 22, rect.y + 24, 34, 34)
        pygame.draw.ellipse(self.screen, color, badge)
        self.screen.blit(number, number.get_rect(center=badge.center))

        title = self.heading_font.render(game["title"], True, WHITE)
        tagline = self.small_font.render(game["tagline"], True, SLATE)
        launch = self.ui_font.render("ENTER", True, BLACK if selected else WHITE)
        launch_rect = pygame.Rect(rect.right - 112, rect.bottom - 50, 82, 30)
        pygame.draw.rect(self.screen, color if selected else (36, 48, 78), launch_rect, border_radius=10)

        self.screen.blit(title, (rect.x + 72, rect.y + 24))
        self.screen.blit(tagline, (rect.x + 72, rect.y + 62))
        self.screen.blit(launch, launch.get_rect(center=launch_rect.center))

    def draw(self):
        self.draw_background()
        title = self.title_font.render("PYTHON GAMES ARCADE", True, WHITE)
        subtitle = self.small_font.render("Choose a game with Up/Down, number keys, mouse, or Enter.", True, SLATE)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 74)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 122)))

        self.cards = []
        start_y = 176
        for index in range(len(GAMES)):
            rect = pygame.Rect(190, start_y + index * 122, 580, 92)
            self.cards.append(rect)
            self.draw_card(index, rect)

        hint = self.small_font.render("Q quits the launcher", True, CRIMSON)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 48)))
        pygame.display.flip()

    def handle_keydown(self, key):
        if key == pygame.K_q:
            pygame.quit()
            sys.exit()
        if key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % len(GAMES)
        elif key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % len(GAMES)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.launch_selected()
        elif pygame.K_1 <= key <= pygame.K_3:
            self.selected = key - pygame.K_1
            self.launch_selected()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)
                if event.type == pygame.MOUSEMOTION:
                    for index, rect in enumerate(self.cards):
                        if rect.collidepoint(event.pos):
                            self.selected = index
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for index, rect in enumerate(self.cards):
                        if rect.collidepoint(event.pos):
                            self.selected = index
                            self.launch_selected()

            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Launcher().run()
