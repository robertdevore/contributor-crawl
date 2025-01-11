import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Contributor Crawl")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREY = (200, 200, 200)

# Fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Load sounds
pygame.mixer.init()
collision_sound = pygame.mixer.Sound("collision.flac")
level_up_sound = pygame.mixer.Sound("level_up.wav")
background_music = "background_music.wav"
pygame.mixer.music.load(background_music)
pygame.mixer.music.play(-1)  # Loop background music indefinitely

# Game variables
player_size = 50
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - player_size - 10]
obstacles = []
score = 0
lives = 3
level = 1
game_started = False
fail_animation = False
fail_timer = 0
level_complete = False  # Flag to prevent repeated level-up calls

# Load emoji images
emoji_images = [
    pygame.image.load(os.path.join("emojis", "cool.png")),
    pygame.image.load(os.path.join("emojis", "funny.png")),
    pygame.image.load(os.path.join("emojis", "crying.png")),
    pygame.image.load(os.path.join("emojis", "angry.png"))
]
emoji_images = [pygame.transform.scale(emoji, (50, 50)) for emoji in emoji_images]
selected_emoji = None  # Placeholder for the selected emoji

# Words for obstacles
words = ["trademark fees", "sponsorships", "core contributions", "money", "first born"]

# Clock
clock = pygame.time.Clock()

# Functions
def draw_text_with_background(text, size, text_color, bg_color, x, y, center=True):
    """Draw text with a background color."""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x, y) if center else (x, y))
    bg_rect = text_rect.inflate(20, 10)  # Add padding to the background
    pygame.draw.rect(screen, bg_color, bg_rect)
    screen.blit(text_surface, text_rect)

def create_obstacle():
    """Create a new obstacle with randomized speed, size, and movement pattern."""
    word = random.choice(words)
    base_speed = max(1, level)  # Ensure minimum speed
    speed = random.randint(base_speed, base_speed + 2)  # Start slower for Level 1
    size = 100  # Fixed size to align with word rendering
    direction = random.choice(["straight", "zigzag"])
    return {
        "rect": pygame.Rect(random.randint(0, SCREEN_WIDTH - size), 0, size, 30),
        "text": word,
        "speed": speed,
        "size": size,
        "direction": direction,
        "zigzag_offset": random.randint(10, 30),
    }

def move_obstacles():
    """Move all obstacles with random patterns."""
    global obstacles, score
    for obs in obstacles[:]:
        if obs["direction"] == "straight":
            obs["rect"].y += obs["speed"]
        elif obs["direction"] == "zigzag":
            obs["rect"].y += obs["speed"]
            obs["rect"].x += obs["zigzag_offset"] * (1 if obs["rect"].y // 50 % 2 == 0 else -1)

        if obs["rect"].top > SCREEN_HEIGHT or obs["rect"].left > SCREEN_WIDTH or obs["rect"].right < 0:
            obstacles.remove(obs)
            score += 1

def detect_collision(player, obstacles):
    """Detect collision between the player and any obstacle."""
    for obs in obstacles:
        if player.colliderect(obs["rect"]):
            return True
    return False

def reset_player():
    """Reset player position to the start."""
    global level_complete
    player_pos[0] = SCREEN_WIDTH // 2
    player_pos[1] = SCREEN_HEIGHT - player_size - 10
    level_complete = False  # Reset level complete flag

def game_over_screen():
    """Display the game over screen."""
    screen.fill(RED)
    draw_text_with_background("GAME OVER", 72, WHITE, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text_with_background(f"Score: {score}", 36, WHITE, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

def start_screen():
    """Display the start screen for emoji selection."""
    screen.fill(WHITE)
    draw_text_with_background("Select Your Emoji!", 50, BLACK, GREY, SCREEN_WIDTH // 2, 100)
    for i, emoji in enumerate(emoji_images):
        x = SCREEN_WIDTH // 2 - 150 + (i * 100)
        y = SCREEN_HEIGHT // 2
        screen.blit(emoji, (x - 25, y - 25))
    draw_text_with_background("Press the corresponding number key (1-4)", 36, BLACK, GREY, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)

def level_up():
    """Increase difficulty and play level-up sound."""
    global level, obstacles, level_complete
    level += 1
    obstacles = []
    level_complete = True
    pygame.mixer.Sound.play(level_up_sound)

# Main loop
while True:
    if not game_started:
        start_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_emoji = emoji_images[0]
                elif event.key == pygame.K_2:
                    selected_emoji = emoji_images[1]
                elif event.key == pygame.K_3:
                    selected_emoji = emoji_images[2]
                elif event.key == pygame.K_4:
                    selected_emoji = emoji_images[3]
                if selected_emoji:
                    game_started = True
        pygame.display.flip()  # Ensure the start screen renders properly
        continue

    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Handle FAIL animation
    if fail_animation:
        draw_text_with_background("FAIL", 72, RED, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.display.flip()
        fail_timer -= 1
        if fail_timer <= 0:
            fail_animation = False
            reset_player()
        continue

    # Character movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= 10
    if keys[pygame.K_RIGHT] and player_pos[0] < SCREEN_WIDTH - player_size:
        player_pos[0] += 10
    if keys[pygame.K_UP] and player_pos[1] > 0:
        player_pos[1] -= 10
    if keys[pygame.K_DOWN] and player_pos[1] < SCREEN_HEIGHT - player_size:
        player_pos[1] += 10

    # Player rectangle
    player = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)

    # Create obstacles
    if len(obstacles) < 3 + level and random.random() < 0.03:  # Adjust density per level
        obstacles.append(create_obstacle())

    # Move obstacles
    move_obstacles()

    # Detect collisions
    if detect_collision(player, obstacles):
        pygame.mixer.Sound.play(collision_sound)
        lives -= 1
        fail_animation = True
        fail_timer = 60  # 1 second at 60 FPS
        if lives == 0:
            game_over_screen()

    # Check level completion
    if player_pos[1] <= 0 and not level_complete:
        level_up()
        reset_player()

    # Draw player
    screen.blit(selected_emoji, (player_pos[0], player_pos[1]))

    # Draw obstacles
    for obs in obstacles:
        draw_text_with_background(obs["text"], 24, WHITE, BLUE, obs["rect"].x + 5, obs["rect"].y + 15, center=False)

    # Draw score and lives
    draw_text_with_background(f"Score: {score}", 36, BLACK, GREY, 80, 20, center=False)
    for i in range(lives):
        screen.blit(selected_emoji, (20 + i * 60, SCREEN_HEIGHT - 60))

    # Update display
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
