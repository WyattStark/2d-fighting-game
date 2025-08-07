import pygame
import asyncio
import platform
import math
import textwrap

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Fighting Game")
FPS = 60
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)

# Easing function for animations
def ease_in_out_cubic(t):
    t *= 2
    if t < 1:
        return 0.5 * t ** 3
    t -= 2
    return 0.5 * (t ** 3 + 2)

# Menu class
class Menu:
    def __init__(self):
        self.active = True
        self.animation_frame = 0
        self.scale = 0
        self.button_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 150, 100, 50)

    def update(self):
        self.animation_frame += 0.5
        if self.animation_frame <= 20:
            self.scale = ease_in_out_cubic(self.animation_frame / 20)
        else:
            self.scale = 1

    def draw(self, screen):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Draw pop-up menu
        menu_width, menu_height = 400, 300
        scaled_width = int(menu_width * self.scale)
        scaled_height = int(menu_height * self.scale)
        menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        menu_surface.fill((200, 200, 200))
        pygame.draw.rect(menu_surface, BLACK, (0, 0, menu_width, menu_height), 2)

        # Render text
        font = pygame.font.Font(None, 40)  # Reduced title font size
        title = font.render("Stickman V2 Update", True, BLACK)
        font_small = pygame.font.Font(None, 28)  # Smaller font for notes
        note_text = "Made punching and kicking animations better"
        # Wrap text to fit within menu width (leaving 20px padding on each side)
        wrapped_lines = textwrap.wrap(note_text, width=35)  # Adjust width for ~360px
        note_surfaces = [font_small.render(line, True, BLACK) for line in wrapped_lines]

        # Draw title and notes
        menu_surface.blit(title, (menu_width // 2 - title.get_width() // 2, 30))
        for i, note_surface in enumerate(note_surfaces):
            menu_surface.blit(note_surface, 
                            (menu_width // 2 - note_surface.get_width() // 2, 80 + i * 30))

        # Draw button
        pygame.draw.rect(menu_surface, GRAY, (menu_width // 2 - 50, menu_height - 100, 100, 50))
        button_text = font_small.render("OK", True, WHITE)
        menu_surface.blit(button_text, (menu_width // 2 - button_text.get_width() // 2, menu_height - 85))

        # Scale and draw menu
        scaled_menu = pygame.transform.scale(menu_surface, (scaled_width, scaled_height))
        screen.blit(scaled_menu, (WIDTH // 2 - scaled_width // 2, HEIGHT // 2 - scaled_height // 2))

    def check_button_click(self, pos):
        if not self.active or self.animation_frame < 20:
            return False
        scaled_button = pygame.Rect(
            WIDTH // 2 - 50 * self.scale,
            HEIGHT // 2 + 50 * self.scale,
            100 * self.scale,
            50 * self.scale
        )
        return scaled_button.collidepoint(pos)

# Player class
class Player:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.color = color
        self.controls = controls
        self.width = 20
        self.height = 40
        self.head_radius = 10
        self.state = "idle"
        self.animation_frame = 0
        self.health = 100
        self.facing = 1 if x < WIDTH // 2 else -1
        self.hit_cooldown = 0
        self.target_x = x

    def draw(self, screen):
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.x, self.y + self.height), 2)
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.head_radius)
        pygame.draw.line(screen, self.color, (self.x, self.y + self.height), 
                        (self.x - 10 * self.facing, self.y + self.height + 20), 2)
        if self.state != "kicking":
            pygame.draw.line(screen, self.color, (self.x, self.y + self.height), 
                            (self.x + 10 * self.facing, self.y + self.height + 20), 2)
        
        if self.state == "punching":
            t = self.animation_frame / 20
            if t < 0.3:
                t = ease_in_out_cubic(t / 0.3)
                arm_end_x = self.x - 10 * self.facing * t
                arm_end_y = self.y + 10 + 10 * t
            else:
                t = ease_in_out_cubic((t - 0.3) / 0.7)
                arm_end_x = self.x + 25 * self.facing * (1 + 0.2 * t)
                arm_end_y = self.y + 10
            pygame.draw.line(screen, self.color, (self.x, self.y + 10), 
                           (arm_end_x, arm_end_y), 2)
            pygame.draw.line(screen, self.color, (self.x, self.y + 10), 
                           (self.x - 10 * self.facing, self.y + 20), 2)
        elif self.state == "kicking":
            t = self.animation_frame / 20
            if t < 0.3:
                t = ease_in_out_cubic(t / 0.3)
                leg_end_x = self.x - 10 * self.facing * t
                leg_end_y = self.y + self.height + 10 * t
            else:
                t = ease_in_out_cubic((t - 0.3) / 0.7)
                leg_end_x = self.x + 25 * self.facing * (1 + 0.2 * t)
                leg_end_y = self.y + self.height + 15
            pygame.draw.line(screen, self.color, (self.x, self.y + 10), 
                           (self.x - 10 * self.facing, self.y + 20), 2)
            pygame.draw.line(screen, self.color, (self.x, self.y + self.height), 
                           (leg_end_x, leg_end_y), 2)
        else:
            pygame.draw.line(screen, self.color, (self.x, self.y + 10), 
                           (self.x - 10 * self.facing, self.y + 20), 2)
            pygame.draw.line(screen, self.color, (self.x, self.y + 10), 
                           (self.x + 10 * self.facing, self.y + 20), 2)
            pygame.draw.line(screen, self.color, (self.x, self.y + self.height), 
                           (self.x + 10 * self.facing, self.y + self.height + 20), 2)

    def move(self, keys):
        if self.state in ["punching", "kicking", "hit"]:
            return
        if keys[self.controls["left"]]:
            self.x -= 5
            self.target_x = self.x
            self.facing = -1
        if keys[self.controls["right"]]:
            self.x += 5
            self.target_x = self.x
            self.facing = 1
        self.x = max(self.head_radius, min(WIDTH - self.head_radius, self.x))
        self.target_x = self.x

    def punch(self):
        if self.state == "idle":
            self.state = "punching"
            self.animation_frame = 0

    def kick(self):
        if self.state == "idle":
            self.state = "kicking"
            self.animation_frame = 0

    def update(self):
        if self.state in ["punching", "kicking"]:
            self.animation_frame += 0.5
            if self.animation_frame > 20:
                self.state = "idle"
                self.animation_frame = 0
        elif self.state == "hit":
            self.animation_frame += 0.5
            t = ease_in_out_cubic(self.animation_frame / 20)
            self.x = self.x + (self.target_x - self.x) * t
            if self.animation_frame > 20:
                self.state = "idle"
                self.animation_frame = 0
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

    def get_hitbox(self):
        t = self.animation_frame / 20
        if self.state == "punching" and t >= 0.3:
            t = ease_in_out_cubic((t - 0.3) / 0.7)
            return pygame.Rect(self.x + 20 * self.facing * (1 + 0.2 * t), self.y, 20, 20)
        elif self.state == "kicking" and t >= 0.3:
            t = ease_in_out_cubic((t - 0.3) / 0.7)
            return pygame.Rect(self.x + 20 * self.facing * (1 + 0.2 * t), self.y + self.height, 20, 20)
        return None

    def get_body_hitbox(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.head_radius, 
                         self.width, self.height + self.head_radius)

# Game setup
menu = Menu()
player1 = Player(200, HEIGHT - 60, RED, {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "punch": pygame.K_w,
    "kick": pygame.K_s
})
player2 = Player(600, HEIGHT - 60, BLUE, {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "punch": pygame.K_UP,
    "kick": pygame.K_DOWN
})

def setup():
    pass

async def update_loop():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and menu.active:
                if menu.check_button_click(event.pos):
                    menu.active = False

        if menu.active:
            menu.update()
            screen.fill(WHITE)
            menu.draw(screen)
        else:
            keys = pygame.key.get_pressed()
            player1.move(keys)
            player2.move(keys)

            if keys[player1.controls["punch"]]:
                player1.punch()
            if keys[player1.controls["kick"]]:
                player1.kick()
            if keys[player2.controls["punch"]]:
                player2.punch()
            if keys[player2.controls["kick"]]:
                player2.kick()

            # Check for hits
            if player1.get_hitbox() and player2.get_body_hitbox().colliderect(player1.get_hitbox()):
                if player2.hit_cooldown == 0 and player2.state != "hit":
                    player2.state = "hit"
                    player2.animation_frame = 0
                    player2.health -= 10 if player1.state == "punching" else 15
                    player2.hit_cooldown = 20
                    player2.target_x = player2.x - 20 * player2.facing
            if player2.get_hitbox() and player1.get_body_hitbox().colliderect(player2.get_hitbox()):
                if player1.hit_cooldown == 0 and player1.state != "hit":
                    player1.state = "hit"
                    player1.animation_frame = 0
                    player1.health -= 10 if player2.state == "punching" else 15
                    player1.hit_cooldown = 20
                    player1.target_x = player1.x - 20 * player1.facing

            player1.update()
            player2.update()

            # Draw game
            screen.fill(WHITE)
            player1.draw(screen)
            player2.draw(screen)
            pygame.draw.rect(screen, RED, (50, 50, player1.health, 20))
            pygame.draw.rect(screen, BLUE, (WIDTH - 150, 50, player2.health, 20))

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(update_loop())
else:
    if __name__ == "__main__":
        asyncio.run(update_loop())
