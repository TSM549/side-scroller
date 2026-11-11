
import pygame
import random
import sys

pygame.init()

WIDTH = 900
HEIGHT = 500
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blob Adventure")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 25, bold=True)
big_font = pygame.font.SysFont("arial", 55, bold=True)

WHITE = (255, 255, 255)
BLACK = (25, 25, 35)
GREEN = (80, 230, 140)
RED = (240, 75, 90)
BLUE = (90, 160, 255)
YELLOW = (255, 220, 90)

GRAVITY = 0.7
PLAYER_SPEED = 5
JUMP_POWER = -14
SCROLL_SPEED = 2

LEVELS = [
    [(0, 420, 900, 80)],
    [(0, 420, 250, 80), (330, 370, 200, 20), (600, 420, 400, 80)],
    [(0, 420, 180, 80), (260, 350, 180, 20), (520, 300, 180, 20), (800, 420, 300, 80)],
    [(0, 420, 300, 80), (380, 390, 120, 20), (570, 340, 120, 20), (780, 420, 400, 80)],
    [(0, 420, 150, 80), (220, 370, 150, 20), (430, 320, 150, 20), (650, 370, 150, 20), (900, 420, 400, 80)],
    [(0, 420, 400, 80), (480, 360, 150, 20), (700, 300, 150, 20), (950, 420, 400, 80)],
    [(0, 420, 200, 80), (280, 320, 120, 20), (470, 380, 120, 20), (660, 300, 120, 20), (850, 420, 400, 80)],
    [(0, 420, 300, 80), (370, 340, 100, 20), (540, 280, 100, 20), (720, 340, 100, 20), (900, 420, 400, 80)],
    [(0, 420, 150, 80), (220, 350, 100, 20), (400, 290, 100, 20), (580, 350, 100, 20), (760, 290, 100, 20), (950, 420, 400, 80)],
    [(0, 420, 500, 80), (570, 360, 100, 20), (750, 300, 100, 20), (950, 350, 100, 20), (1150, 420, 400, 80)]
]

class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, 300, 42, 42)
        self.velocity_y = 0
        self.grounded = False
        self.health = 3

    def update(self, platforms):
        keys = pygame.key.get_pressed()

        dx = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -PLAYER_SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = PLAYER_SPEED

        self.rect.x += dx

        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        self.grounded = False

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.top
                    self.velocity_y = 0
                    self.grounded = True
                elif self.velocity_y < 0:
                    self.rect.top = platform.bottom
                    self.velocity_y = 0

    def jump(self):
        if self.grounded:
            self.velocity_y = JUMP_POWER
            self.grounded = False

    def draw(self, surface, camera):
        x = self.rect.x - camera
        pygame.draw.ellipse(surface, GREEN, (x, self.rect.y, 42, 42))
        pygame.draw.circle(surface, BLACK, (x + 13, self.rect.y + 16), 4)
        pygame.draw.circle(surface, BLACK, (x + 29, self.rect.y + 16), 4)


class Enemy:
    def __init__(self, x, y, platform):
        self.rect = pygame.Rect(x, y, 38, 35)
        self.speed = random.choice([-2, 2])
        self.left_limit = platform.left
        self.right_limit = platform.right - self.rect.width
        self.alive = True

    def update(self):
        self.rect.x += self.speed
        if self.rect.left <= self.left_limit:
            self.rect.left = self.left_limit
            self.speed = abs(self.speed)
        elif self.rect.left >= self.right_limit:
            self.rect.left = self.right_limit
            self.speed = -abs(self.speed)

    def draw(self, surface, camera):
        if self.alive:
            x = self.rect.x - camera
            pygame.draw.ellipse(surface, RED, (x, self.rect.y, 38, 35))
            pygame.draw.circle(surface, WHITE, (x + 11, self.rect.y + 12), 5)
            pygame.draw.circle(surface, WHITE, (x + 27, self.rect.y + 12), 5)
            pygame.draw.circle(surface, BLACK, (x + 11, self.rect.y + 12), 2)
            pygame.draw.circle(surface, BLACK, (x + 27, self.rect.y + 12), 2)


def create_level(offset=0):
    template = random.choice(LEVELS)
    platforms = [pygame.Rect(x + offset, y, w, h) for x, y, w, h in template]

    enemies = []

    for platform in platforms:
        if platform.width > 120 and random.random() < 0.8:
            x = random.randint(platform.left + 30, platform.right - 50)
            enemies.append(Enemy(x, platform.top - 35, platform))

    return platforms, enemies


def draw_text(text, x, y, color=WHITE):
    image = font.render(text, True, color)
    screen.blit(image, (x, y))


def main():
    player = Player()
    platforms, enemies = create_level()

    score = 0
    defeated_enemies = 0
    start_time = pygame.time.get_ticks()
    camera = 0
    game_over = False
    level = 1
    level_end = max(platform.right for platform in platforms)
    level_boundaries = []

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if not game_over:
                        player.jump()

                if event.key == pygame.K_r and game_over:
                    return main()

        if not game_over:
            player.update(platforms)

            for enemy in enemies:
                enemy.update()

                if enemy.alive and player.rect.colliderect(enemy.rect):
                    if player.velocity_y > 0 and player.rect.bottom < enemy.rect.top + 20:
                        player.rect.bottom = enemy.rect.top
                        player.velocity_y = JUMP_POWER * 0.65
                        enemy.alive = False
                        defeated_enemies += 1
                    else:
                        player.health -= 1
                        player.rect.x -= 70
                        player.velocity_y = -7

                        if player.health <= 0:
                            game_over = True

            elapsed = (pygame.time.get_ticks() - start_time) // 1000
            score = elapsed * 10 + defeated_enemies * 50

            if player.rect.y > HEIGHT + 100:
                player.health = 0
                game_over = True

            camera += SCROLL_SPEED
            if player.rect.right < camera:
                game_over = True

            while camera + WIDTH + 100 >= level_end:
                level_boundaries.append(level_end)
                new_platforms, new_enemies = create_level(level_end)
                platforms.extend(new_platforms)
                enemies.extend(new_enemies)
                level_end = max(platform.right for platform in new_platforms)

            passed_levels = sum(boundary <= camera for boundary in level_boundaries)
            if passed_levels:
                level += passed_levels
                level_boundaries = [
                    boundary for boundary in level_boundaries if boundary > camera
                ]

            platforms = [platform for platform in platforms if platform.right > camera - 100]
            enemies = [enemy for enemy in enemies if enemy.rect.right > camera - 100]

        screen.fill((100, 190, 255))

        pygame.draw.circle(screen, YELLOW, (750, 80), 40)

        for platform in platforms:
            pygame.draw.rect(
                screen,
                (110, 75, 55),
                (platform.x - camera, platform.y, platform.width, platform.height)
            )
            pygame.draw.rect(
                screen,
                GREEN,
                (platform.x - camera, platform.y, platform.width, 8)
            )

        for enemy in enemies:
            enemy.draw(screen, camera)

        player.draw(screen, camera)

        pygame.draw.rect(screen, BLACK, (15, 15, 230, 105), border_radius=12)

        draw_text(f"Score: {score}", 30, 25)
        draw_text(f"Health: {player.health}", 30, 55, RED)
        draw_text(f"Level: {level}", 30, 85, YELLOW)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))

            title = big_font.render("GAME OVER", True, RED)
            screen.blit(title, title.get_rect(center=(WIDTH // 2, 180)))

            result = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(result, result.get_rect(center=(WIDTH // 2, 250)))

            restart = font.render("Press R to Restart", True, YELLOW)
            screen.blit(restart, restart.get_rect(center=(WIDTH // 2, 310)))

        pygame.display.flip()


main()
