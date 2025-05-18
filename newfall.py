# 🚧 Dodge Game with Menu - Now a Shooter with Falling Blocks and Powerups
import pygame
import random
import time
import sys

# Initialize
pygame.init()
WIDTH, HEIGHT = 500, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚧 Dodge Shooter")

# Fonts & Colors
font = pygame.font.SysFont("Arial", 30)
small_font = pygame.font.SysFont("Arial", 20)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLOCK_COLOR = (255, 100, 100)
POWERUP_COLOR = (0, 255, 0)
SHIELD_COLOR = (255, 255, 0)
BULLET_COLOR = (255, 255, 255)

# Player color default
player_color = (0, 200, 255)


def draw_text_centered(surface, text, y, font, color=WHITE):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2, y))
    surface.blit(rendered, rect)


def main_menu():
    global player_color
    while True:
        win.fill(BLACK)
        draw_text_centered(win, "🚧 Dodge the Falling Blocks 🚧", 100, font)
        draw_text_centered(win, "[1] Start Game", 200, small_font)
        draw_text_centered(win, "[2] Change Square Color (RGB)", 250, small_font)
        draw_text_centered(win, "[3] Quit", 300, small_font)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return  # Start game
                elif event.key == pygame.K_2:
                    player_color = prompt_color_input()
                elif event.key == pygame.K_3:
                    pygame.quit()
                    sys.exit()


def prompt_color_input():
    print("\nEnter RGB values (0–255) for your square.")
    try:
        r = int(input("Red: "))
        g = int(input("Green: "))
        b = int(input("Blue: "))
        if all(0 <= val <= 255 for val in (r, g, b)):
            return (r, g, b)
        else:
            print("Invalid values. Using default.")
    except:
        print("Invalid input. Using default.")
    return (0, 200, 255)


def run_game():
    global player_color

    player_size = 50
    base_speed = 7
    player_speed = base_speed
    block_speed = 5
    block_size = 50
    powerup_size = 30
    bullet_width, bullet_height = 5, 10

    player_x = WIDTH // 2
    player_y = HEIGHT - player_size - 10
    block_list = []
    powerup_list = []
    bullets = []
    powerup_timer = 0
    powerup_active = None
    shield_used = False
    score = 0

    clock = pygame.time.Clock()
    FPS = 30
    running = True

    def drop_blocks():
        if len(block_list) < 10 and random.random() < 0.05:
            x_pos = random.randint(0, WIDTH - block_size)
            block_list.append([x_pos, 0])

    def draw_blocks():
        for block in block_list:
            pygame.draw.rect(win, BLOCK_COLOR, (block[0], block[1], block_size, block_size))

    def update_block_positions():
        nonlocal score, block_speed
        for block in block_list[:]:
            block[1] += block_speed
            if block[1] > HEIGHT:
                block_list.remove(block)
                score += 1
                block_speed = 5 + score // 10

    def spawn_powerup():
        if random.randint(1, 200) == 1:
            x_pos = random.randint(0, WIDTH - powerup_size)
            power_type = random.choice(['speed', 'shield'])
            powerup_list.append({'pos': [x_pos, 0], 'type': power_type})

    def draw_powerups():
        for powerup in powerup_list:
            color = POWERUP_COLOR if powerup['type'] == 'speed' else SHIELD_COLOR
            pygame.draw.rect(win, color, (*powerup['pos'], powerup_size, powerup_size))

    def update_powerups(player_rect):
        nonlocal player_speed, powerup_timer, powerup_active, shield_used
        for powerup in powerup_list[:]:
            powerup['pos'][1] += 3
            powerup_rect = pygame.Rect(*powerup['pos'], powerup_size, powerup_size)
            if powerup_rect.colliderect(player_rect):
                if powerup['type'] == 'speed':
                    powerup_active = 'speed'
                    player_speed = base_speed + 5
                    powerup_timer = time.time()
                elif powerup['type'] == 'shield':
                    powerup_active = 'shield'
                    shield_used = False
                powerup_list.remove(powerup)
            elif powerup['pos'][1] > HEIGHT:
                powerup_list.remove(powerup)

    def detect_collision(a, b):
        return a.colliderect(b)

    while running:
        clock.tick(FPS)
        win.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if powerup_active == 'speed' and time.time() - powerup_timer > 5:
            player_speed = base_speed
            powerup_active = None

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_d] and player_x < WIDTH - player_size:
            player_x += player_speed
        if keys[pygame.K_w] and player_y > 50:
            player_y -= player_speed
        if keys[pygame.K_s] and player_y < HEIGHT - player_size:
            player_y += player_speed
        if keys[pygame.K_SPACE]:
            if len(bullets) < 5:
                bullet_rect = pygame.Rect(player_x + player_size // 2 - bullet_width // 2, player_y, bullet_width, bullet_height)
                bullets.append(bullet_rect)

        drop_blocks()
        update_block_positions()
        spawn_powerup()

        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        update_powerups(player_rect)

        for block in block_list[:]:
            block_rect = pygame.Rect(block[0], block[1], block_size, block_size)
            if detect_collision(player_rect, block_rect):
                if powerup_active == 'shield' and not shield_used:
                    shield_used = True
                    block_list.remove(block)
                else:
                    running = False

        for bullet in bullets[:]:
            bullet.y -= 10
            if bullet.bottom < 0:
                bullets.remove(bullet)
            else:
                for block in block_list[:]:
                    block_rect = pygame.Rect(block[0], block[1], block_size, block_size)
                    if bullet.colliderect(block_rect):
                        bullets.remove(bullet)
                        block_list.remove(block)
                        score += 1
                        block_speed = 5 + score // 10
                        break

        draw_blocks()
        draw_powerups()
        pygame.draw.rect(win, player_color, player_rect)

        for bullet in bullets:
            pygame.draw.rect(win, BULLET_COLOR, bullet)

        score_text = small_font.render(f"Score: {score}", True, WHITE)
        win.blit(score_text, (10, 10))

        if powerup_active == 'speed':
            power_text = small_font.render("Speed Boost!", True, POWERUP_COLOR)
            win.blit(power_text, (10, 40))
        elif powerup_active == 'shield' and not shield_used:
            power_text = small_font.render("Shield Active!", True, SHIELD_COLOR)
            win.blit(power_text, (10, 40))

        pygame.display.update()

    win.fill(BLACK)
    draw_text_centered(win, f"Game Over! Score: {score}", HEIGHT // 2, font)
    pygame.display.update()
    pygame.time.wait(3000)


while True:
    main_menu()
    run_game()
