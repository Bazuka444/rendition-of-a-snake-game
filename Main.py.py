
import math  # For distance calculations in defender spawning
import random  # For randomization of positions, directions, and food spawns
import sys  # For system-specific functions, used to exit the game
import os  # For file path operations to load images and audio
import pygame  # type: ignore # Core library for graphics, input handling, and sound management

# Rugby Snake Game
# Created by Kamohelo Ngwenya
# A Pygame-based game where a player controls a single rugby player icon to collect rugby balls
# for points while avoiding defenders. Features a menu, difficulty selection, color selection,
# time selection, and settings with sound, theme, and rules. Uses a grid-based movement system
# and a rugby pitch design for immersion.


# Window Setup

WINDOW_WIDTH = 800  # Width of the game window in pixels
WINDOW_HEIGHT = 600  # Height of the game window in pixels
FPS = 60  # Frames per second, controls game update rate for smooth gameplay

# File paths for assets, stored in a 'Pictures' folder relative to the script
LOGO_RELATIVE_PATH = os.path.join(
    'Pictures', 'snakelogo.png')  # Path to game logo
RUGBY_BALL_PATH = os.path.join(
    'Pictures', 'Settings.png')  # Path to rugby ball image
# Path to background music
BG_MUSIC_PATH = os.path.join('Pictures', 'BackgroundSound.wav')

# Game state constants to manage different screens
MENU = "menu"  # Main menu with logo and play button
WELCOME = "welcome"  # Screen for selecting game difficulty
SETTINGS = "settings"  # Screen for sound, volume, theme, and rules
PLAYING = "playing"  # Core gameplay state
COLOR_SELECT = "color_select"  # Screen for choosing player color
TIME_SELECT = "time_select"  # Screen for selecting round duration
GAME_OVER = "game_over"  # Game over screen with score and replay options


# Button Class


class Button:  # Class for creating interactive UI buttons
    # Initialize button with position, text, font, and colors
    def __init__(self, rect, text, font, bg_color=(0, 0, 0), text_color=(255, 255, 255)):
        # Create Pygame Rect for positioning and collision
        self.rect = pygame.Rect(rect)
        self.text = text  # Store button label
        self.font = font  # Store font for text rendering
        self.bg_color = bg_color  # Background color (default black)
        self.text_color = text_color  # Text color (default white)
        self.hover = False  # Flag to track mouse hover
        self.alpha = 255  # Alpha for transparency, starts fully opaque

    def _render_text(self):  # Render button text and center it
        # Render text with antialiasing to make edges smooth
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(
            center=self.rect.center)  # Center text in button
        return text_surf, text_rect  # Return text surface and rectangle

    def draw(self, surface):  # Draw button on the given surface
        button_surface = pygame.Surface(
            self.rect.size, pygame.SRCALPHA)  # Create transparent surface
        button_surface.set_alpha(self.alpha)  # Set transparency level
        pygame.draw.ellipse(button_surface, self.bg_color,
                            button_surface.get_rect())  # Draw filled ellipse
        pygame.draw.ellipse(button_surface, (255, 255, 255),
                            button_surface.get_rect(), 2)  # Draw white border
        text_surf, text_rect = self._render_text()  # Render text
        text_rect.center = button_surface.get_rect().center  # Center text on button
        # Blit text to button surface
        button_surface.blit(text_surf, text_rect)
        # Blit button to main surface
        surface.blit(button_surface, self.rect.topleft)

    def update(self, mouse_pos):  # Update button state based on mouse position
        # Set hover if mouse is over button
        self.hover = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):  # Check if button is clicked
        # True if left-clicked while hovering
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover

# Image Helpers


def load_image(path, max_w, max_h):  # Load and scale an image
    if not os.path.isfile(path):  # Check if file exists
        print(f"Warning: File not found - {path}")  # Warn if missing
        return None  # Return None for missing file
    try:  # Try to load image
        # Load with alpha transparency
        img = pygame.image.load(path).convert_alpha()
    except pygame.error as e:  # Catch Pygame-specific errors
        print(f"Error loading image '{path}': {e}")  # Print error
        return None  # Return None on failure
    except Exception as e:  # Catch unexpected errors
        print(f"Unexpected error loading '{path}': {e}")  # Print error
        return None  # Return None
    iw, ih = img.get_size()  # Get original dimensions
    scale = min(max_w / iw, max_h / ih, 1.0)  # Calculate scale factor
    new_size = (int(iw * scale), int(ih * scale))  # Compute scaled dimensions
    return pygame.transform.smoothscale(img, new_size)  # Return scaled image


def draw_placeholder(surface, rect, text):  # Draw placeholder for missing images
    pygame.draw.rect(surface, (210, 210, 210), rect,
                     border_radius=8)  # Draw light gray rectangle
    pygame.draw.rect(surface, (140, 140, 140), rect, width=3,
                     border_radius=8)  # Draw darker border
    font = pygame.font.SysFont(None, 20)  # Use default system font
    txt = font.render(text, True, (60, 60, 60))  # Render text in dark gray
    surface.blit(txt, txt.get_rect(center=rect.center))  # Blit centered text


# Rugby Pitch
# Define centered rugby pitch rectangle
pitch_rect = pygame.Rect(100, 100, 600, 400)


def draw_pitch(screen):  # Draw rugby pitch with grass, borders, and goal posts
    for i in range(0, pitch_rect.height, 40):  # Create alternating grass stripes
        pygame.draw.rect(screen, (50, 150, 50), (pitch_rect.left,
                         pitch_rect.top + i, pitch_rect.width, 20))  # Draw light green stripe
    # Draw dark green grass
    pygame.draw.rect(screen, (34, 139, 34), pitch_rect)
    pygame.draw.rect(screen, (255, 255, 255),
                     pitch_rect, 5)  # Draw white border
    pygame.draw.line(screen, (255, 255, 255), (pitch_rect.centerx, pitch_rect.top),
                     (pitch_rect.centerx, pitch_rect.bottom), 3)  # Draw midline
    try_line_offset = 50  # Offset for try lines
    pygame.draw.line(screen, (255, 255, 255), (pitch_rect.left, pitch_rect.top + try_line_offset),
                     # Top try line
                     (pitch_rect.right, pitch_rect.top + try_line_offset), 3)
    pygame.draw.line(screen, (255, 255, 255), (pitch_rect.left, pitch_rect.bottom - try_line_offset),
                     # Bottom try line
                     (pitch_rect.right, pitch_rect.bottom - try_line_offset), 3)
    pole_height = 40  # Height of goal posts
    crossbar_width = 60  # Width of crossbar
    center_x = pitch_rect.centerx  # Center x for symmetry
    pygame.draw.line(screen, (255, 255, 255), (center_x - crossbar_width // 2, pitch_rect.top + try_line_offset -
                     # Top left pole
                                               pole_height), (center_x - crossbar_width // 2, pitch_rect.top + try_line_offset), 5)
    pygame.draw.line(screen, (255, 255, 255), (center_x + crossbar_width // 2, pitch_rect.top + try_line_offset -
                     # Top right pole
                                               pole_height), (center_x + crossbar_width // 2, pitch_rect.top + try_line_offset), 5)
    pygame.draw.line(screen, (255, 255, 255), (center_x - crossbar_width // 2, pitch_rect.top + try_line_offset - pole_height //
                     # Top crossbar
                                               2), (center_x + crossbar_width // 2, pitch_rect.top + try_line_offset - pole_height // 2), 5)
    pygame.draw.line(screen, (255, 255, 255), (center_x - crossbar_width // 2, pitch_rect.bottom - try_line_offset +
                     # Bottom left pole
                                               pole_height), (center_x - crossbar_width // 2, pitch_rect.bottom - try_line_offset), 5)
    pygame.draw.line(screen, (255, 255, 255), (center_x + crossbar_width // 2, pitch_rect.bottom - try_line_offset +
                     # Bottom right pole
                                               pole_height), (center_x + crossbar_width // 2, pitch_rect.bottom - try_line_offset), 5)
    pygame.draw.line(screen, (255, 255, 255), (center_x - crossbar_width // 2, pitch_rect.bottom - try_line_offset + pole_height // 2),
                     # Bottom crossbar
                     (center_x + crossbar_width // 2, pitch_rect.bottom - try_line_offset + pole_height // 2), 5)

# Menu Background Players


class MenuBackgroundPlayer:  # Class for decorative players in menu
    def __init__(self, color):  # Initialize with color
        # Random x within pitch
        self.x = random.randint(pitch_rect.left + 20, pitch_rect.right - 20)
        # Random y within pitch
        self.y = random.randint(pitch_rect.top + 20, pitch_rect.bottom - 20)
        self.radius = 15  # Circle radius
        self.color = color  # Player color
        self.dx = random.choice([-2, -1, 1, 2])  # Random x velocity
        self.dy = random.choice([-2, -1, 1, 2])  # Random y velocity

    def move(self):  # Move player and bounce off pitch edges
        self.x += self.dx  # Update x
        self.y += self.dy  # Update y
        if self.x - self.radius < pitch_rect.left or self.x + self.radius > pitch_rect.right:  # Check x bounds
            self.dx *= -1  # Reverse x direction
        if self.y - self.radius < pitch_rect.top or self.y + self.radius > pitch_rect.bottom:  # Check y bounds
            self.dy *= -1  # Reverse y direction

    def draw(self, screen):  # Draw player as a circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(
            self.y)), self.radius, 0)  # Draw filled circle

# Gameplay Defenders


class BackgroundPlayer:  # Class for defenders chasing the player
    # Initialize with player color, player ref, difficulty, and cell size
    def __init__(self, player_color, player, difficulty, cell_size):
        self.radius = 15  # Defender radius
        color_options = [(255, 255, 0), (255, 0, 255),
                         (0, 255, 255)]  # Color options
        self.color = next((c for c in color_options if c != player_color),
                          color_options[0])  # Choose non-player color
        self.player = player  # Store player reference
        if difficulty == "Easy":  # Set speed for Easy
            self.speed = 1.5
        elif difficulty == "Medium":  # Set speed for Medium
            self.speed = 2.0
        else:  # Set speed for Hard
            self.speed = 2.5
        min_distance = 100  # Minimum spawn distance from player
        player_x = pitch_rect.left + player.x * \
            cell_size + cell_size // 2  # Player center x
        player_y = pitch_rect.top + player.y * \
            cell_size + cell_size // 2  # Player center y
        spawn_attempts = 0  # Spawn attempt counter
        max_attempts = 100  # Max attempts to prevent infinite loop
        while True:  # Loop to find safe spawn
            self.x = random.randint(
                pitch_rect.left + 20, pitch_rect.right - 20)  # Random x
            self.y = random.randint(
                pitch_rect.top + 20, pitch_rect.bottom - 20)  # Random y
            dist = math.sqrt((self.x - player_x)**2 +
                             (self.y - player_y)**2)  # Distance to player
            if dist >= min_distance:  # If safe
                break  # Exit loop
            spawn_attempts += 1  # Increment attempts
            if spawn_attempts > max_attempts:  # If exceeded
                # Warn
                print(
                    "Warning: Could not find safe spawn position for defender. Using default.")
                self.x = pitch_rect.left + 20  # Default x
                self.y = pitch_rect.top + 20  # Default y
                break  # Exit

    def move(self, cell_size, countdown_timer):  # Move defender towards player
        if countdown_timer > 0:  # Skip if countdown active
            return
        head_x = pitch_rect.left + self.player.x * \
            cell_size + cell_size // 2  # Player center x
        head_y = pitch_rect.top + self.player.y * \
            cell_size + cell_size // 2  # Player center y
        dx = head_x - self.x  # Delta x
        dy = head_y - self.y  # Delta y
        dist = (dx**2 + dy**2)**0.5  # Euclidean distance
        if dist > 0:  # Prevent division by zero
            self.x += (dx / dist) * self.speed  # Move x
            self.y += (dy / dist) * self.speed  # Move y
        self.x = max(pitch_rect.left + self.radius, min(self.x,
                     pitch_rect.right - self.radius))  # Clamp x
        self.y = max(pitch_rect.top + self.radius, min(self.y,
                     pitch_rect.bottom - self.radius))  # Clamp y

    def draw(self, screen):  # Draw defender
        pygame.draw.circle(screen, self.color, (int(self.x),
                           int(self.y)), self.radius, 0)  # Draw circle

    def collides_with_player(self, player, cell_size):  # Check collision with player
        head_x = pitch_rect.left + player.x * \
            cell_size + cell_size // 2  # Player center x
        head_y = pitch_rect.top + player.y * cell_size + cell_size // 2  # Player center y
        dist = ((self.x - head_x)**2 + (self.y - head_y)**2)**0.5  # Distance
        return dist < self.radius + (cell_size // 2)  # True if collision

# Player Class


class Player:  # Class for the player
    def __init__(self, color, grid_w, grid_h):  # Initialize player
        if color is None:  # Validate color
            raise ValueError("Player color cannot be None")
        self.color = color  # Set color
        self.x = grid_w // 2  # Start x at grid center
        self.y = grid_h // 2  # Start y at grid center
        self.direction = (1, 0)  # Initial direction right
        self.radius = 15  # Player radius

    def change_direction(self, new_dir):  # Change movement direction
        # Allow non-opposite turns
        if (new_dir[0] != -self.direction[0] or new_dir[1] != -self.direction[1]) or (new_dir[0] == 0 and new_dir[1] == 0):
            self.direction = new_dir  # Update direction

    def move(self, food_pos, grid_w, grid_h):  # Move player on grid
        new_x = self.x + self.direction[0]  # Calculate new x
        new_y = self.y + self.direction[1]  # Calculate new y
        hit_wall = not (0 <= new_x < grid_w and 0 <=
                        new_y < grid_h)  # Check bounds
        if hit_wall:  # If hit wall
            return True, False, True  # Continue, no eat, hit wall
        self.x = new_x  # Update x
        self.y = new_y  # Update y
        ate = (self.x, self.y) == food_pos  # Check if ate food
        return True, ate, False  # Continue, ate status, no wall

    def draw(self, screen, cell_size):  # Draw player
        cx = pitch_rect.left + self.x * cell_size + cell_size // 2  # Center x
        cy = pitch_rect.top + self.y * cell_size + cell_size // 2  # Center y
        pygame.draw.circle(screen, self.color, (cx, cy),
                           self.radius)  # Draw circle

# Render Screens


def render_menu(screen, logo_img, play_button, title_font, small_font, bg_players):  # Render main menu
    w, h = screen.get_size()  # Get dimensions
    screen.fill((0, 0, 51))  # Fill dark blue
    for p in bg_players:  # Update and draw background players
        p.move()  # Move player
        p.draw(screen)  # Draw player
    if logo_img:  # If logo exists
        logo_rect = logo_img.get_rect(
            center=(w // 2, int(h * 0.3)))  # Center logo
        screen.blit(logo_img, logo_rect)  # Blit logo
    else:  # No logo
        placeholder_rect = pygame.Rect(
            w // 2 - 200, int(h * 0.3) - 75, 400, 150)  # Placeholder rect
        draw_placeholder(screen, placeholder_rect, "Logo")  # Draw placeholder
    title_surf = title_font.render(
        "RUGBY SNAKE", True, (255, 255, 255))  # Render title
    screen.blit(title_surf, title_surf.get_rect(
        center=(w // 2, int(h * 0.15))))  # Blit title
    play_button.draw(screen)  # Draw play button
    note = small_font.render(
        # Render instruction
        "Press SPACE or click Play to start", True, (255, 255, 0))
    screen.blit(note, note.get_rect(
        center=(w // 2, int(h * 0.85))))  # Blit instruction


def render_welcome(screen, title_font, small_font, easy_btn, med_btn, hard_btn, logo_side_img, rugby_ball_img, bg_players):  # Render welcome screen
    w, h = screen.get_size()  # Get dimensions
    screen.fill((0, 0, 51))  # Fill background
    draw_pitch(screen)  # Draw pitch
    crowd_dots = [(random.randint(0, 80), random.randint(0, 600)) for _ in range(
        # Generate crowd dots
        50)] + [(random.randint(720, 800), random.randint(0, 600)) for _ in range(50)]
    for x, y in crowd_dots:  # Draw crowd
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 2)  # Draw dot
    for p in bg_players:  # Draw background players
        p.move()  # Move
        p.draw(screen)  # Draw
    welcome_surf = title_font.render(
        "SELECT DIFFICULTY", True, (255, 255, 255))  # Render title
    screen.blit(welcome_surf, welcome_surf.get_rect(
        center=(w // 2, 60)))  # Blit title
    if logo_side_img:  # If side logo
        screen.blit(logo_side_img, logo_side_img.get_rect(
            topleft=(20, 20)))  # Blit logo
    if rugby_ball_img:  # If ball image
        rugby_ball_img_scaled = pygame.transform.scale(
            rugby_ball_img, (60, 60))  # Scale ball
        ball_rect = rugby_ball_img_scaled.get_rect(
            topright=(w - 10, 10))  # Get rect
        screen.blit(rugby_ball_img_scaled, ball_rect)  # Blit ball
    else:  # No ball
        ball_rect = pygame.Rect(w - 70, 10, 60, 60)  # Placeholder rect
        draw_placeholder(screen, ball_rect, "Rugby Ball")  # Draw placeholder
    spacing = 200  # Button spacing
    easy_btn.rect.center = (w // 2 - spacing, int(h * 0.8))  # Position easy
    med_btn.rect.center = (w // 2, int(h * 0.8))  # Position medium
    hard_btn.rect.center = (w // 2 + spacing, int(h * 0.8))  # Position hard
    easy_btn.draw(screen)  # Draw easy
    med_btn.draw(screen)  # Draw medium
    hard_btn.draw(screen)  # Draw hard
    return ball_rect  # Return ball rect for click detection


# Render color selection
def render_color_selection(screen, title_font, small_font, color_buttons):
    w, h = screen.get_size()  # Get dimensions
    screen.fill((0, 0, 51))  # Fill background
    title_surf = title_font.render(
        "SELECT YOUR TEAM COLOR", True, (255, 255, 255))  # Render title
    screen.blit(title_surf, title_surf.get_rect(
        center=(w // 2, 80)))  # Blit title
    for btn in color_buttons:  # Draw buttons
        btn.draw(screen)


# Render time selection
def render_time_selection(screen, title_font, small_font, time_buttons):
    w, h = screen.get_size()  # Get dimensions
    screen.fill((0, 0, 51))  # Fill background
    title_surf = title_font.render(
        "SELECT ROUND LENGTH (MIN)", True, (255, 255, 255))  # Render title
    screen.blit(title_surf, title_surf.get_rect(
        center=(w // 2, 80)))  # Blit title
    for btn in time_buttons:  # Draw buttons
        btn.draw(screen)


# Render settings screen with rules
def render_settings(screen, title_font, small_font, sound_on, dark_mode, volume_level):
    # Create overlay surface
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(220)  # Set transparency
    overlay.fill((10, 10, 40) if dark_mode else (
        180, 200, 255))  # Fill based on theme
    screen.blit(overlay, (0, 0))  # Blit overlay
    title = title_font.render(
        # Render title
        "SETTINGS ⚙️", True, (255, 255, 255) if dark_mode else (0, 0, 80))
    screen.blit(title, title.get_rect(
        center=(WINDOW_WIDTH // 2, 80)))  # Blit title
    sound_status = "ON" if sound_on else "OFF"  # Sound status text
    sound_text = small_font.render(
        # Render sound
        f"Sound: {sound_status}  (Press S to toggle)", True, (255, 255, 0))
    screen.blit(sound_text, sound_text.get_rect(
        center=(WINDOW_WIDTH // 2, 180)))  # Blit sound
    volume_text = small_font.render(
        # Render volume
        f"Volume: {int(volume_level * 100)}%  (Use ↑ / ↓)", True, (255, 255, 255))
    screen.blit(volume_text, volume_text.get_rect(
        center=(WINDOW_WIDTH // 2, 230)))  # Blit volume
    theme_text = small_font.render(
        # Render theme
        f"Theme: {'Dark' if dark_mode else 'Light'} (Press T to toggle)", True, (255, 255, 255))
    screen.blit(theme_text, theme_text.get_rect(
        center=(WINDOW_WIDTH // 2, 280)))  # Blit theme
    rules_title = small_font.render(
        "Rules:", True, (255, 255, 255))  # Render rules title
    screen.blit(rules_title, rules_title.get_rect(
        center=(WINDOW_WIDTH // 2, 330)))  # Blit rules title
    rules = [  # List of game rules
        "Move your player to collect rugby balls for points.",  # Rule 1: Core objective
        "Each ball adds 10 points; speed increases slightly.",  # Rule 2: Scoring
        # Rule 3: Defenders and lives
        "Avoid defenders; collision costs 1 life (3 total).",
        "Hitting walls deducts 5 points.",  # Rule 4: Wall penalty
        "Game ends when time runs out or lives reach zero.",  # Rule 5: Game over conditions
        "Choose difficulty, color, and time before starting."  # Rule 6: Setup
    ]
    for i, line in enumerate(rules):  # Render each rule
        text = small_font.render(
            line, True, (200, 200, 200))  # Render rule text
        # Blit rule, spaced vertically
        screen.blit(text, text.get_rect(
            center=(WINDOW_WIDTH // 2, 360 + i * 25)))
    controls_title = small_font.render(
        "Controls:", True, (255, 255, 255))  # Render controls title
    screen.blit(controls_title, controls_title.get_rect(
        # Blit below rules
        center=(WINDOW_WIDTH // 2, 360 + len(rules) * 25 + 30)))
    controls = [  # List of controls
        "Arrow Keys or A/W/S/D to move",
        "ESC to return to Menu",
        "S - Toggle Sound | T - Toggle Theme",
        "↑ / ↓ - Adjust Volume",
        "P - Pause/Resume"
    ]
    for i, line in enumerate(controls):  # Render controls
        text = small_font.render(
            line, True, (200, 200, 200))  # Render control text
        screen.blit(text, text.get_rect(center=(WINDOW_WIDTH // 2, 360 +
                    len(rules) * 25 + 60 + i * 25)))  # Blit below rules title
    note = small_font.render(
        "Press ESC to return to Menu", True, (255, 100, 100))  # Render note
    screen.blit(note, note.get_rect(center=(WINDOW_WIDTH // 2, 360 +
                len(rules) * 25 + 60 + len(controls) * 25 + 30)))  # Blit at bottom


def render_playing(screen, title_font, small_font, player, food_pos, score, time_left_frames, countdown_timer, paused, rugby_ball_img, bg_players, pause_btn, quit_btn, cell_size, pitch_rect, lives):  # Render gameplay
    if player is None:  # Validate player
        raise ValueError("Player object is None in render_playing")
    w, h = screen.get_size()  # Get dimensions
    screen.fill((0, 0, 51))  # Fill background
    draw_pitch(screen)  # Draw pitch
    crowd_dots = [(random.randint(0, 80), random.randint(0, 600)) for _ in range(
        # Generate crowd
        50)] + [(random.randint(720, 800), random.randint(0, 600)) for _ in range(50)]
    for x, y in crowd_dots:  # Draw crowd
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 2)  # Draw dot
    for p in bg_players:  # Draw defenders
        p.draw(screen)
    player.draw(screen, cell_size)  # Draw player
    if rugby_ball_img:  # Draw ball
        ball_scaled = pygame.transform.smoothscale(
            rugby_ball_img, (cell_size, cell_size))  # Scale
        screen.blit(ball_scaled, (pitch_rect.left +
                    # Blit
                                  food_pos[0] * cell_size, pitch_rect.top + food_pos[1] * cell_size))
    else:  # Fallback
        pygame.draw.ellipse(screen, (150, 75, 0), (pitch_rect.left +
                            # Draw ellipse
                                                   food_pos[0] * cell_size, pitch_rect.top + food_pos[1] * cell_size, cell_size, cell_size))
    time_left_sec = max(time_left_frames // FPS, 0)  # Calculate time
    minn = time_left_sec // 60  # Minutes
    sec = time_left_sec % 60  # Seconds
    time_str = f"{minn:02d}:{sec:02d}"  # Format time
    score_surf = small_font.render(
        f"Score: {score}", True, (255, 255, 255))  # Render score
    time_surf = small_font.render(
        f"Time: {time_str}", True, (255, 255, 255))  # Render time
    lives_surf = small_font.render(
        f"Lives: {lives}", True, (255, 255, 255))  # Render lives
    screen.blit(score_surf, (pitch_rect.left, 20))  # Blit score
    screen.blit(time_surf, (pitch_rect.left +
                score_surf.get_width() + 20, 20))  # Blit time
    screen.blit(lives_surf, (pitch_rect.right -
                lives_surf.get_width(), 20))  # Blit lives
    pause_btn.draw(screen)  # Draw pause
    quit_btn.draw(screen)  # Draw quit
    if countdown_timer > 0:  # Draw countdown
        cd_num = (countdown_timer // FPS) + 1  # Calculate number
        cd_surf = title_font.render(str(cd_num), True, (255, 0, 0))  # Render
        screen.blit(cd_surf, cd_surf.get_rect(center=(w // 2, h // 2)))  # Blit
    if paused:  # Draw pause overlay
        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT))  # Create overlay
        overlay.set_alpha(200)  # Set alpha
        overlay.fill((10, 10, 40))  # Fill
        screen.blit(overlay, (0, 0))  # Blit
        paused_surf = title_font.render(
            "PAUSED", True, (255, 255, 0))  # Render paused
        pause_score = small_font.render(
            f"Score: {score}", True, (255, 255, 255))  # Render score
        pause_time = small_font.render(
            f"Time Left: {time_str}", True, (255, 255, 255))  # Render time
        screen.blit(paused_surf, paused_surf.get_rect(
            center=(w // 2, h // 2 - 50)))  # Blit paused
        screen.blit(pause_score, pause_score.get_rect(
            center=(w // 2, h // 2)))  # Blit score
        screen.blit(pause_time, pause_time.get_rect(
            center=(w // 2, h // 2 + 50)))  # Blit time


def render_game_over(screen, title_font, small_font, final_score, restart_same_btn, restart_diff_btn, quit_btn):  # Render game over
    w, h = screen.get_size()  # Get dimensions
    screen.fill((0, 0, 51))  # Fill background
    title_surf = title_font.render(
        "Game Over!", True, (255, 0, 0))  # Render title
    screen.blit(title_surf, title_surf.get_rect(
        center=(w // 2, h // 2 - 150)))  # Blit title
    congrats_messages = [  # Score-based messages
        (100, "Legendary Try! You're a rugby superstar!"),
        (50, "Solid Scrum! Great effort out there!"),
        (20, "Nice Tackle! You gave it a good run!"),
        (1, "Good Hustle! You kept the ball in play!")
    ]
    congrats_text = "Well played!"  # Default message
    for threshold, message in congrats_messages:  # Find message
        if final_score >= threshold:
            congrats_text = message
            break
    if final_score == 0:  # Zero score poem
        poem_lines = [
            "The field was tough, the defenders cold,",
            "Your tries were thwarted, no points to hold.",
            "Yet rise again, with heart so bold,",
            "Next game, your glory will unfold!"
        ]
        for i, line in enumerate(poem_lines):  # Render poem
            poem_surf = small_font.render(
                line, True, (255, 255, 0))  # Render line
            screen.blit(poem_surf, poem_surf.get_rect(
                center=(w // 2, h // 2 - 100 + i * 30)))  # Blit line
    else:  # Non-zero score
        congrats_surf = small_font.render(
            congrats_text, True, (255, 255, 0))  # Render message
        screen.blit(congrats_surf, congrats_surf.get_rect(
            center=(w // 2, h // 2 - 100)))  # Blit
    score_surf = small_font.render(
        f"Final Score: {final_score}", True, (255, 255, 255))  # Render score
    screen.blit(score_surf, score_surf.get_rect(
        center=(w // 2, h // 2 - 50)))  # Blit score
    restart_same_btn.draw(screen)  # Draw restart same
    restart_diff_btn.draw(screen)  # Draw restart diff
    quit_btn.draw(screen)  # Draw quit

# Gameplay Helpers


# Spawn food avoiding player and defenders
def spawn_food(player_pos, bg_players, grid_w, grid_h, cell_size):
    spawn_attempts = 0  # Attempt counter
    max_attempts = 100  # Max attempts
    while True:  # Loop for position
        x = random.randint(0, grid_w - 1)  # Random x
        y = random.randint(0, grid_h - 1)  # Random y
        if (x, y) != (player_pos.x, player_pos.y):  # Not on player
            food_x = pitch_rect.left + x * cell_size + cell_size // 2  # Food x
            food_y = pitch_rect.top + y * cell_size + cell_size // 2  # Food y
            safe = True  # Assume safe
            for p in bg_players:  # Check defenders
                dist = math.sqrt((p.x - food_x)**2 +
                                 (p.y - food_y)**2)  # Distance
                if dist < p.radius + (cell_size // 2):  # If overlap
                    safe = False  # Not safe
                    break
            if safe:  # If safe
                return (x, y)  # Return position
        spawn_attempts += 1  # Increment
        if spawn_attempts > max_attempts:  # If exceeded
            print("Warning: Could not find safe food spawn. Using default.")  # Warn
            return (grid_w // 2 + 1, grid_h // 2 + 1)  # Fallback

# Main Game Loop


def main():  # Main function
    try:  # Try Pygame init
        pygame.init()
    except Exception as e:  # Catch errors
        print(f"Error initializing Pygame: {e}")
        sys.exit(1)
    try:  # Try create screen
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    except pygame.error as e:  # Catch display errors
        print(f"Error creating display: {e}")
        pygame.quit()
        sys.exit(1)
    pygame.display.set_caption("Rugby Snake")  # Set title
    clock = pygame.time.Clock()  # Create clock
    try:  # Try fonts
        title_font = pygame.font.SysFont(None, 48)  # Title font
        small_font = pygame.font.SysFont(None, 24)  # Small font
    except Exception as e:  # Catch font errors
        print(f"Error creating fonts: {e}")
        title_font = pygame.font.Font(None, 48)  # Fallback
        small_font = pygame.font.Font(None, 24)  # Fallback
    project_root = os.path.dirname(os.path.abspath(__file__))  # Get root dir
    logo_img = load_image(os.path.join(project_root, LOGO_RELATIVE_PATH),
                          WINDOW_WIDTH * 0.7, WINDOW_HEIGHT * 0.35)  # Load logo
    logo_side_img = load_image(os.path.join(
        project_root, LOGO_RELATIVE_PATH), 100, 100)  # Load side logo
    rugby_ball_img = load_image(os.path.join(
        project_root, RUGBY_BALL_PATH), 100, 100)  # Load ball
    try:  # Try audio
        pygame.mixer.init()
        music_path = os.path.join(project_root, BG_MUSIC_PATH)
        if os.path.isfile(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1, fade_ms=1000)
        else:
            print(f"Warning: Music file '{music_path}' not found.")
    except pygame.error as e:
        print(f"Error initializing audio: {e}")
    except Exception as e:
        print(f"Unexpected audio error: {e}")
    play_button = Button((WINDOW_WIDTH // 2 - 110, int(WINDOW_HEIGHT * 0.65),
                         # Play button
                          220, 60), "Play", pygame.font.SysFont(None, 28))
    easy_btn = Button((0, 0, 180, 60), "Easy",
                      pygame.font.SysFont(None, 28))  # Easy button
    easy_btn.alpha = 0  # Start invisible
    med_btn = Button((0, 0, 180, 60), "Medium",
                     pygame.font.SysFont(None, 28))  # Medium button
    med_btn.alpha = 0
    hard_btn = Button((0, 0, 220, 60), "For the Brave!",
                      pygame.font.SysFont(None, 28))  # Hard button
    hard_btn.alpha = 0
    menu_bg_players = [MenuBackgroundPlayer((0, 0, 255)) for _ in range(
        # Background players
        5)] + [MenuBackgroundPlayer((200, 0, 0)) for _ in range(5)]
    color_buttons = []  # Color buttons list
    colors = [("Red", (200, 0, 0)), ("Blue", (0, 0, 200)),
              ("Green", (0, 200, 0)), ("Black", (20, 20, 20))]  # Colors
    for name, color in colors:  # Create color buttons
        btn = Button((0, 0, 80, 50), name,
                     pygame.font.SysFont(None, 28), bg_color=color)
        btn.alpha = 0
        color_buttons.append(btn)
    time_buttons = []  # Time buttons
    for i in range(1, 6):  # Create time buttons
        btn = Button((0, 0, 60, 60), str(i), pygame.font.SysFont(
            None, 28), bg_color=(0, 150, 0))
        btn.alpha = 0
        time_buttons.append(btn)
    restart_same_btn = Button(
        (0, 0, 200, 60), "Restart", pygame.font.SysFont(None, 28))  # Restart same
    restart_diff_btn = Button((0, 0, 300, 60), "Restart with Different Color/Time",
                              pygame.font.SysFont(None, 28))  # Restart diff
    quit_btn_go = Button((0, 0, 200, 60), "Quit to Menu",
                         pygame.font.SysFont(None, 28))  # Quit button
    state = MENU  # Start state
    frame_count = 0  # Frame counter
    sound_on = True  # Sound on
    dark_mode = True  # Dark mode
    volume_level = 0.5  # Volume
    selected_color = None  # Color
    selected_time = None  # Time
    selected_difficulty = None  # Difficulty
    num_defenders = 0  # Defenders
    player = None  # Player
    food_pos = None  # Food pos
    score = 0  # Score
    final_score = 0  # Final score
    time_left_frames = 0  # Time frames
    countdown_timer = 0  # Countdown
    move_counter = 0  # Move counter
    move_delay = 0  # Move delay
    initial_move_delay = 0  # Initial delay
    paused = False  # Paused
    pause_btn = None  # Pause button
    quit_btn = None  # Quit button
    grid_w = 30  # Grid width
    grid_h = 20  # Grid height
    cell_size = 20  # Cell size
    if pitch_rect.width % cell_size != 0 or pitch_rect.height % cell_size != 0:  # Check grid alignment
        print("Warning: Pitch dimensions not divisible by cell_size.")
    bg_players = []  # Defenders list
    lives = 3  # Lives
    last_key_time = 0  # Last key time
    key_cooldown = 0.1  # Key cooldown

    while True:  # Main loop
        mouse_pos = pygame.mouse.get_pos()  # Get mouse pos
        for event in pygame.event.get():  # Process events
            if event.type == pygame.QUIT:  # Quit event
                pygame.mixer.quit()  # Quit mixer
                pygame.quit()  # Quit Pygame
                sys.exit()  # Exit
            if event.type == pygame.ACTIVEEVENT:  # Window focus
                if event.gain == 0 and state == PLAYING:  # Lost focus
                    paused = True
                    if pause_btn:
                        pause_btn.text = "Resume"
            if state == MENU:  # Menu state
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    state = WELCOME
                    frame_count = 0
                if play_button.is_clicked(event):
                    state = WELCOME
                    frame_count = 0
            elif state == WELCOME:  # Welcome state
                if easy_btn.is_clicked(event):
                    selected_difficulty = "Easy"
                    state = COLOR_SELECT
                    frame_count = 0
                elif med_btn.is_clicked(event):
                    selected_difficulty = "Medium"
                    state = COLOR_SELECT
                    frame_count = 0
                elif hard_btn.is_clicked(event):
                    selected_difficulty = "Hard"
                    state = COLOR_SELECT
                    frame_count = 0
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if 'rugby_ball_rect' in locals() and rugby_ball_rect.collidepoint(event.pos):
                        state = SETTINGS
            elif state == COLOR_SELECT:  # Color select
                for btn in color_buttons:
                    if btn.is_clicked(event):
                        selected_color = btn.bg_color
                        state = TIME_SELECT
                        frame_count = 0
            elif state == TIME_SELECT:  # Time select
                for btn in time_buttons:
                    if btn.is_clicked(event):
                        selected_time = int(btn.text)
                        if selected_color is None or selected_difficulty is None:
                            print("Error: Missing color or difficulty.")
                            state = WELCOME
                            continue
                        if selected_difficulty == "Easy":
                            move_delay = 10
                            initial_move_delay = 10
                            num_defenders = 2
                        elif selected_difficulty == "Medium":
                            move_delay = 7
                            initial_move_delay = 7
                            num_defenders = 4
                        else:
                            move_delay = 5
                            initial_move_delay = 5
                            num_defenders = 6
                        player = Player(selected_color, grid_w, grid_h)
                        food_pos = spawn_food(
                            player, bg_players, grid_w, grid_h, cell_size)
                        score = 0
                        lives = 3
                        time_left_frames = selected_time * 60 * FPS
                        countdown_timer = 3 * FPS
                        move_counter = 0
                        bg_players = [BackgroundPlayer(
                            selected_color, player, selected_difficulty, cell_size) for _ in range(num_defenders)]
                        paused = False
                        pause_btn = Button(
                            (600, 20, 100, 50), "Pause", small_font)
                        pause_btn.alpha = 255
                        quit_btn = Button((710, 20, 100, 50),
                                          "Quit", small_font)
                        quit_btn.alpha = 255
                        state = PLAYING
                        if pygame.mixer.get_init():
                            pygame.mixer.music.fadeout(1000)
            elif state == SETTINGS:  # Settings state
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        sound_on = not sound_on
                        if pygame.mixer.get_init():
                            pygame.mixer.music.set_volume(
                                volume_level if sound_on else 0)
                    elif event.key == pygame.K_t:
                        dark_mode = not dark_mode
                    elif event.key == pygame.K_UP:
                        volume_level = min(volume_level + 0.1, 1.0)
                        if pygame.mixer.get_init():
                            pygame.mixer.music.set_volume(
                                volume_level if sound_on else 0)
                    elif event.key == pygame.K_DOWN:
                        volume_level = max(volume_level - 0.1, 0.0)
                        if pygame.mixer.get_init():
                            pygame.mixer.music.set_volume(
                                volume_level if sound_on else 0)
                    elif event.key == pygame.K_ESCAPE:
                        state = WELCOME
            elif state == PLAYING:  # Playing state
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = not paused
                        if pause_btn:
                            pause_btn.text = "Resume" if paused else "Pause"
                    if not paused and countdown_timer == 0:
                        current_time = pygame.time.get_ticks() / 1000
                        if current_time - last_key_time > key_cooldown:
                            last_key_time = current_time
                            if event.key in (pygame.K_UP, pygame.K_w):
                                player.change_direction((0, -1))
                            elif event.key in (pygame.K_DOWN, pygame.K_s):
                                player.change_direction((0, 1))
                            elif event.key in (pygame.K_LEFT, pygame.K_a):
                                player.change_direction((-1, 0))
                            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                                player.change_direction((1, 0))
                if pause_btn and pause_btn.is_clicked(event):
                    paused = not paused
                    pause_btn.text = "Resume" if paused else "Pause"
                if quit_btn and quit_btn.is_clicked(event):
                    final_score = score
                    state = GAME_OVER
                    if pygame.mixer.get_init():
                        pygame.mixer.music.play(-1, fade_ms=1000)
            elif state == GAME_OVER:  # Game over state
                if restart_same_btn.is_clicked(event):
                    if selected_color is None or selected_time is None or selected_difficulty is None:
                        print("Error: Missing setup for restart.")
                        state = MENU
                        continue
                    player = Player(selected_color, grid_w, grid_h)
                    food_pos = spawn_food(
                        player, bg_players, grid_w, grid_h, cell_size)
                    score = 0
                    lives = 3
                    time_left_frames = selected_time * 60 * FPS
                    countdown_timer = 3 * FPS
                    move_counter = 0
                    move_delay = initial_move_delay
                    bg_players = [BackgroundPlayer(
                        selected_color, player, selected_difficulty, cell_size) for _ in range(num_defenders)]
                    paused = False
                    if pause_btn:
                        pause_btn.text = "Pause"
                    if pygame.mixer.get_init():
                        pygame.mixer.music.fadeout(1000)
                    state = PLAYING
                elif restart_diff_btn.is_clicked(event):
                    state = COLOR_SELECT
                    frame_count = 0
                elif quit_btn_go.is_clicked(event):
                    state = MENU
                    if pygame.mixer.get_init():
                        pygame.mixer.music.play(-1, fade_ms=1000)
        frame_count += 1  # Increment frame counter
        dt = clock.tick(FPS) / 1000.0  # Delta time
        if state == WELCOME:  # Fade in difficulty buttons
            if frame_count > 20:
                easy_btn.alpha = min(easy_btn.alpha + 5, 255)
            if frame_count > 60:
                med_btn.alpha = min(med_btn.alpha + 5, 255)
            if frame_count > 100:
                hard_btn.alpha = min(hard_btn.alpha + 5, 255)
        if state == COLOR_SELECT:  # Fade in color buttons
            for i, btn in enumerate(color_buttons):
                if frame_count > i * 15:
                    btn.alpha = min(btn.alpha + 5, 255)
            spacing = 100
            total_width = len(color_buttons) * spacing
            start_x = (WINDOW_WIDTH - total_width) // 2 + spacing // 2
            y = WINDOW_HEIGHT // 2
            for i, btn in enumerate(color_buttons):
                btn.rect.center = (start_x + i * spacing, y)
        if state == TIME_SELECT:  # Fade in time buttons
            for i, btn in enumerate(time_buttons):
                if frame_count > i * 15:
                    btn.alpha = min(btn.alpha + 5, 255)
            spacing = 90
            total_width = len(time_buttons) * spacing
            start_x = (WINDOW_WIDTH - total_width) // 2 + spacing // 2
            y = WINDOW_HEIGHT // 2
            for i, btn in enumerate(time_buttons):
                btn.rect.center = (start_x + i * spacing, y)
        if state == GAME_OVER:  # Position game over buttons
            spacing = 220
            restart_same_btn.rect.center = (
                WINDOW_WIDTH // 2 - spacing, WINDOW_HEIGHT // 2 + 100)
            restart_diff_btn.rect.center = (
                WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100)
            quit_btn_go.rect.center = (
                WINDOW_WIDTH // 2 + spacing, WINDOW_HEIGHT // 2 + 100)
        if state == PLAYING:  # Gameplay logic
            if not paused:
                if countdown_timer > 0:
                    countdown_timer -= 1
                else:
                    for p in bg_players:
                        p.move(cell_size, countdown_timer)
                    move_counter += 1
                    if move_counter >= move_delay:
                        move_counter = 0
                        success, ate, hit_wall = player.move(
                            food_pos, grid_w, grid_h)
                        if not success:
                            final_score = score
                            state = GAME_OVER
                            if pygame.mixer.get_init():
                                pygame.mixer.music.play(-1, fade_ms=1000)
                        if ate:
                            score += 10
                            move_delay = max(2, move_delay - 0.5)
                            food_pos = spawn_food(
                                player, bg_players, grid_w, grid_h, cell_size)
                        if hit_wall:
                            score = max(0, score - 5)
                    collision_occurred = False
                    for p in bg_players:
                        if p.collides_with_player(player, cell_size) and not collision_occurred:
                            collision_occurred = True
                            lives -= 1
                            if lives <= 0:
                                final_score = score
                                state = GAME_OVER
                                if pygame.mixer.get_init():
                                    pygame.mixer.music.play(-1, fade_ms=1000)
                            else:
                                player = Player(player.color, grid_w, grid_h)
                                food_pos = spawn_food(
                                    player, bg_players, grid_w, grid_h, cell_size)
                                bg_players = [BackgroundPlayer(
                                    player.color, player, selected_difficulty, cell_size) for _ in range(num_defenders)]
                                move_delay = initial_move_delay
                    time_left_frames -= int(dt * FPS)
                    if time_left_frames <= 0:
                        final_score = score
                        state = GAME_OVER
                        if pygame.mixer.get_init():
                            pygame.mixer.music.play(-1, fade_ms=1000)
        if state == MENU:  # Update buttons
            play_button.update(mouse_pos)
        elif state == WELCOME:
            [btn.update(mouse_pos) for btn in [easy_btn, med_btn, hard_btn]]
        elif state == COLOR_SELECT:
            [btn.update(mouse_pos) for btn in color_buttons]
        elif state == TIME_SELECT:
            [btn.update(mouse_pos) for btn in time_buttons]
        elif state == PLAYING:
            if pause_btn:
                pause_btn.update(mouse_pos)
            if quit_btn:
                quit_btn.update(mouse_pos)
        elif state == GAME_OVER:
            restart_same_btn.update(mouse_pos)
            restart_diff_btn.update(mouse_pos)
            quit_btn_go.update(mouse_pos)
        if state == MENU:  # Render
            render_menu(screen, logo_img, play_button,
                        title_font, small_font, menu_bg_players)
        elif state == WELCOME:
            rugby_ball_rect = render_welcome(
                screen, title_font, small_font, easy_btn, med_btn, hard_btn, logo_side_img, rugby_ball_img, menu_bg_players)
        elif state == COLOR_SELECT:
            render_color_selection(
                screen, title_font, small_font, color_buttons)
        elif state == TIME_SELECT:
            render_time_selection(screen, title_font, small_font, time_buttons)
        elif state == SETTINGS:
            render_settings(screen, title_font, small_font,
                            sound_on, dark_mode, volume_level)
        elif state == PLAYING:
            render_playing(screen, title_font, small_font, player, food_pos, score, time_left_frames, countdown_timer,
                           paused, rugby_ball_img, bg_players, pause_btn, quit_btn, cell_size, pitch_rect, lives)
        elif state == GAME_OVER:
            render_game_over(screen, title_font, small_font, final_score,
                             restart_same_btn, restart_diff_btn, quit_btn_go)
        pygame.display.flip()  # Update display


if __name__ == "__main__":  # Entry point
    main()
