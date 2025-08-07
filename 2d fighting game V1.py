import pygame
import asyncio
import platform
import math

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

# Easing function for smoother animations
def ease_out_quad(t):
    return 1 - (1 - t) ** 2

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
        self.target_x = x  # For smooth movement when hit

    def draw(self, screen):
        # Draw body
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.x, self.y + self.height), 2)
        # Draw head
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.head_radius)
        # Draw legs
        pygame.draw.line(screen, self.color, (self.x, self.y + self.height), 
                        (self.x - 10 * self.facing, self.y + self.height + 20), 2)
        pygame.draw.line(screen, self.color, (self.x, self.y + self.height), 
                        (self.x + 10 * self.facing, self.y + self.height + 20), 2)
        
        # Draw arms based on state
        if self.state == "punching":
            t = ease_out_quad(self.animation_frame / 20)  # 20 frames for animation
            arm_end_x = self.x + 25 * self.facing * t
            pygame.draw.line(screen, self.color, (self.x, self.y + 10), 
                           (arm_end_x, self.y + 10), 2)
            pygame.draw.line(screen, self.color, (self.x, self.y + 10), 
                           (self.x - 10 * self.facing, self.y + 20), 2)
        elif self.state == "kicking":
            t = ease_out_quad(self.animation_frame / 20)
            leg_end_x = self.x + 25 * self.facing * t
            leg_end_y = self.y + self.height + 15 * t
            pygame.draw.line(screen, self.color, (self.x, self.y + 10), 
                           (self.x - 10 * self.facing, self.y + 20), 2)
            pygame.draw.line(screen, self.color, (self.x, self.y + self.height), 
                           (leg_end_x, leg_end_y), 2)
        else:
            pygame.draw.line(screen, self.color, (self.x, self.y + 10), 
                           (self.x - 10 * self.facing, self.y + 20), 2)
            pygame.draw.line(screen, self.color, (self.x, self.y + 10), 
                           (self.x + 10 * self.facing, self.y + 20), 2)

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
            self.animation_frame += 0.5  # Slower increment for smoother animation
            if self.animation_frame > 20:
                self.state = "idle"
                self.animation_frame = 0
        elif self.state == "hit":
            self.animation_frame += 0.5
            t = ease_out_quad(self.animation_frame / 20)
            self.x = self.x + (self.target_x - self.x) * t  # Smooth interpolation
            if self.animation_frame > 20:
                self.state = "idle"
                self.animation_frame = 0
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

    def get_hitbox(self):
        if self.state == "punching":
            t = ease_out_quad(self.animation_frame / 20)
            return pygame.Rect(self.x + 20 * self.facing * t, self.y, 20, 20)
        elif self.state == "kicking":
            t = ease_out_quad(self.animation_frame / 20)
            return pygame.Rect(self.x + 20 * self.facing * t, self.y + self.height, 20, 20)
        return None

    def get_body_hitbox(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.head_radius, 
                         self.width, self.height + self.head_radius)

# Game setup
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
                player2.target_x = player2.x - 20 * player2.facing  # Set target for smooth knockback
        if player2.get_hitbox() and player1.get_body_hitbox().colliderect(player2.get_hitbox()):
            if player1.hit_cooldown == 0 and player1.state != "hit":
                player1.state = "hit"
                player1.animation_frame = 0
                player1.health -= 10 if player2.state == "punching" else 15
                player1.hit_cooldown = 20
                player1.target_x = player1.x - 20 * player1.facing

        player1.update()
        player2.update()

        # Draw everything
        screen.fill(WHITE)
        player1.draw(screen)
        player2.draw(screen)
        
        # Draw health bars
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
