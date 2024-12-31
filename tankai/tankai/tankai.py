import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 900

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Tank dimensions
TANK_WIDTH, TANK_HEIGHT = 40, 40
BULLET_WIDTH, BULLET_HEIGHT = 10, 10
HEALTH_BAR_WIDTH = 50
HEALTH_BAR_HEIGHT = 5

# Movement speed
TANK_SPEED = 5
BOT_SPEED = 1.5  # Further reduced bot speed
BULLET_SPEED = 10

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Player vs AI Tank Game")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Tank class
class Tank:
    def __init__(self, x, y, color, label):
        self.x = x
        self.y = y
        self.color = color
        self.health = 5
        self.bullets = []
        self.direction = "UP"
        self.shots_fired = 0
        self.reloading = False
        self.reload_start_time = 0
        self.label = label  # Label to display inside the tank

    def move(self, keys=None, up=None, down=None, left=None, right=None, speed=TANK_SPEED):
        if keys:
            if keys[up] and self.y > 0:
                self.y -= speed
                self.direction = "UP"
            if keys[down] and self.y < SCREEN_HEIGHT - TANK_HEIGHT:
                self.y += speed
                self.direction = "DOWN"
            if keys[left] and self.x > 0:
                self.x -= speed
                self.direction = "LEFT"
            if keys[right] and self.x < SCREEN_WIDTH - TANK_WIDTH:
                self.x += speed
                self.direction = "RIGHT"

    def bot_move(self, target):
        if random.randint(1, 100) < 5 and not self.reloading:  # Reduced chance to shoot
            self.shoot()

        if abs(self.x - target.x) > abs(self.y - target.y):
            if self.x < target.x:
                self.x += BOT_SPEED
                self.direction = "RIGHT"
            elif self.x > target.x:
                self.x -= BOT_SPEED
                self.direction = "LEFT"
        else:
            if self.y < target.y:
                self.y += BOT_SPEED
                self.direction = "DOWN"
            elif self.y > target.y:
                self.y -= BOT_SPEED
                self.direction = "UP"

    def shoot(self):
        if self.reloading:
            return
        if self.shots_fired >= 10:  # Cooldown every 10 shots
            self.start_reload()
            return

        if self.direction == "UP":
            bullet = pygame.Rect(
                self.x + TANK_WIDTH // 2 - BULLET_WIDTH // 2, self.y, BULLET_WIDTH, BULLET_HEIGHT
            )
        elif self.direction == "DOWN":
            bullet = pygame.Rect(
                self.x + TANK_WIDTH // 2 - BULLET_WIDTH // 2, self.y + TANK_HEIGHT, BULLET_WIDTH, BULLET_HEIGHT
            )
        elif self.direction == "LEFT":
            bullet = pygame.Rect(
                self.x, self.y + TANK_HEIGHT // 2 - BULLET_HEIGHT // 2, BULLET_HEIGHT, BULLET_WIDTH
            )
        elif self.direction == "RIGHT":
            bullet = pygame.Rect(
                self.x + TANK_WIDTH, self.y + TANK_HEIGHT // 2 - BULLET_HEIGHT // 2, BULLET_HEIGHT, BULLET_WIDTH
            )
        self.bullets.append((bullet, self.direction))
        self.shots_fired += 1
       
    def start_reload(self):
        self.reloading = True
        self.reload_start_time = pygame.time.get_ticks()

    def reload(self):
        if self.reloading and pygame.time.get_ticks() - self.reload_start_time >= 2000:  # 2 seconds
            self.shots_fired = 0
            self.reloading = False

    def draw(self):
        # Draw tank
        pygame.draw.rect(screen, self.color, (self.x, self.y, TANK_WIDTH, TANK_HEIGHT))
        # Draw label inside the tank
        font = pygame.font.Font(None, 24)
        label_text = font.render(self.label, True, BLACK)
        label_rect = label_text.get_rect(center=(self.x + TANK_WIDTH // 2, self.y + TANK_HEIGHT // 2))
        screen.blit(label_text, label_rect)
        # Draw stick (barrel)
        if self.direction == "UP":
            pygame.draw.line(screen, self.color, (self.x + TANK_WIDTH // 2, self.y), (self.x + TANK_WIDTH // 2, self.y - 20), 5)
        elif self.direction == "DOWN":
            pygame.draw.line(screen, self.color, (self.x + TANK_WIDTH // 2, self.y + TANK_HEIGHT), (self.x + TANK_WIDTH // 2, self.y + TANK_HEIGHT + 20), 5)
        elif self.direction == "LEFT":
            pygame.draw.line(screen, self.color, (self.x, self.y + TANK_HEIGHT // 2), (self.x - 20, self.y + TANK_HEIGHT // 2), 5)
        elif self.direction == "RIGHT":
            pygame.draw.line(screen, self.color, (self.x + TANK_WIDTH, self.y + TANK_HEIGHT // 2), (self.x + TANK_WIDTH + 20, self.y + TANK_HEIGHT // 2), 5)
        # Draw bullets
        for bullet, direction in self.bullets:
            pygame.draw.rect(screen, WHITE, bullet)

        # Draw health bar
        health_bar_x = self.x + (TANK_WIDTH - HEALTH_BAR_WIDTH) // 2
        health_bar_y = self.y - 10
        pygame.draw.rect(screen, RED, (health_bar_x, health_bar_y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
        pygame.draw.rect(screen, GREEN, (health_bar_x, health_bar_y, HEALTH_BAR_WIDTH * (self.health / 5), HEALTH_BAR_HEIGHT))

# Initial state variables
show_start_screen = True
running = True
paused = False
show_game_over = False
winner = None

# Buttons
start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, "START", RED, WHITE)
pause_button = Button(SCREEN_WIDTH - 120, 20, 100, 40, "PAUSE", RED, WHITE)
resume_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, "RESUME", RED, WHITE)
play_again_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50, "PLAY AGAIN", GREEN, BLACK)

def start_screen():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 72)
    start_text = font.render("CLICK START TO PLAY", True, WHITE)
    text_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(start_text, text_rect)
    start_button.draw()

# Tanks
tank1 = Tank(100, 300, RED, "YOU")
bot_tank = Tank(600, 300, BLUE, "BOT")

# Game loop
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if show_start_screen and start_button.is_clicked(event.pos):
                show_start_screen = False
            elif pause_button.is_clicked(event.pos):
                paused = True
            elif resume_button.is_clicked(event.pos):
                paused = False
            elif show_game_over and play_again_button.is_clicked(event.pos):
                tank1 = Tank(100, 300, RED, "YOU")
                bot_tank = Tank(600, 300, BLUE, "BOT")
                show_game_over = False
                winner = None

        if event.type == pygame.KEYDOWN and not show_start_screen and not show_game_over and not paused:
            if event.key == pygame.K_SPACE:
                tank1.shoot()
            if event.key == pygame.K_e:
                tank1.start_reload()

    if show_start_screen:
        start_screen()

    elif paused:
        # Show pause screen
        font = pygame.font.Font(None, 72)
        pause_text = font.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(pause_text, text_rect)
        resume_button.draw()

    elif not show_game_over:
        # Handle keys
        keys = pygame.key.get_pressed()

        # Tank 1 movement (Arrow Keys)
        tank1.move(keys, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)

        # Bot movement and logic
        bot_tank.bot_move(tank1)

        # Reload bot if necessary
        bot_tank.reload()
        tank1.reload()

        # Move bullets
        for tank in [tank1, bot_tank]:
            for bullet, direction in tank.bullets[:]:
                if direction == "UP":
                    bullet.y -= BULLET_SPEED
                elif direction == "DOWN":
                    bullet.y += BULLET_SPEED
                elif direction == "LEFT":
                    bullet.x -= BULLET_SPEED
                elif direction == "RIGHT":
                    bullet.x += BULLET_SPEED

                # Collision and boundary checks
                if bullet.colliderect(pygame.Rect(bot_tank.x, bot_tank.y, TANK_WIDTH, TANK_HEIGHT)) and tank == tank1:
                    bot_tank.health -= 1
                    tank.bullets.remove((bullet, direction))
                elif bullet.colliderect(pygame.Rect(tank1.x, tank1.y, TANK_WIDTH, TANK_HEIGHT)) and tank == bot_tank:
                    tank1.health -= 1
                    tank.bullets.remove((bullet, direction))
                elif bullet.y < 0 or bullet.y > SCREEN_HEIGHT or bullet.x < 0 or bullet.x > SCREEN_WIDTH:
                    tank.bullets.remove((bullet, direction))

        # Draw tanks and bullets
        tank1.draw()
        bot_tank.draw()
        pause_button.draw()

        # Display health
        font = pygame.font.Font(None, 36)
        health_text1 = font.render(f"Player Health: {tank1.health}", True, WHITE)
        health_text2 = font.render(f"Bot Health: {bot_tank.health}", True, WHITE)
        screen.blit(health_text1, (10, 10))
        screen.blit(health_text2, (SCREEN_WIDTH - 200, 10))

        # Check for game over
        if tank1.health <= 0 or bot_tank.health <= 0:
            winner = "Player" if bot_tank.health <= 0 else "Bot"
            show_game_over = True

    else:
        # Show game over screen
        font = pygame.font.Font(None, 72)
        game_over_text = font.render("YOU WON!!" if winner == "Player" else "YOU LOST", True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(game_over_text, text_rect)
        play_again_button.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
