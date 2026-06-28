import pygame
import sys
import random
import math

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BG_COLOR = (10, 10, 18)
PADDLE_COLOR = (0, 255, 204)
BALL_COLOR = (255, 0, 128)
SCORE_COLOR = (100, 110, 140)
WHITE = (255, 255, 255)

BRICK_COLORS = [
    {"base": (255, 0, 55),   "glow": (255, 50, 100)},
    {"base": (255, 110, 0),  "glow": (255, 160, 50)},
    {"base": (212, 255, 0),  "glow": (230, 255, 100)},
    {"base": (0, 180, 255),  "glow": (100, 220, 255)}
]

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("⚡ PREMIUM BREAKOUT EVOLUTION ⚡")
clock = pygame.time.Clock()

font_hud = pygame.font.SysFont("Impact", 20)
font_title = pygame.font.SysFont("Impact", 40)

particles = []

def spawn_particles(x, y, color):
    for _ in range(15):
        particles.append({
            "x": x,
            "y": y,
            "vx": random.uniform(-4, 4),
            "vy": random.uniform(-4, 4),
            "radius": random.uniform(2, 5),
            "color": color,
            "life": 1.0
        })

paddle_width = 130
paddle_height = 16
paddle_x = (SCREEN_WIDTH - paddle_width) // 2
paddle_y = SCREEN_HEIGHT - 50
paddle_speed = 9
paddle = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)

ball_size = 14
ball = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, ball_size, ball_size)
ball_speed_x = 5 * random.choice([-1, 1])
ball_speed_y = -6

ball_trail = []

BRICK_ROWS = 4
BRICK_COLS = 17
brick_width = 72
brick_height = 24
brick_padding = 6
offset_top = 80
offset_left = (SCREEN_WIDTH - ((brick_width + brick_padding) * BRICK_COLS)) // 2

bricks = []
for row in range(BRICK_ROWS):
    for col in range(BRICK_COLS):
        bx = offset_left + col * (brick_width + brick_padding)
        by = offset_top + row * (brick_height + brick_padding)
        bricks.append({
            "rect": pygame.Rect(bx, by, brick_width, brick_height), 
            "color_data": BRICK_COLORS[row]
        })

score = 0
lives = 3
game_over = False
victory = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if (game_over or victory) and event.key == pygame.K_SPACE:
                score = 0
                lives = 3
                game_over = False
                victory = False
                paddle.x = (SCREEN_WIDTH - paddle_width) // 2
                ball.x = SCREEN_WIDTH // 2
                ball.y = SCREEN_HEIGHT // 2
                ball_speed_x = 5 * random.choice([-1, 1])
                ball_speed_y = -6
                ball_trail.clear()
                particles.clear()
                
                bricks = []
                for r in range(BRICK_ROWS):
                    for c in range(BRICK_COLS):
                        bx = offset_left + c * (brick_width + brick_padding)
                        by = offset_top + r * (brick_height + brick_padding)
                        bricks.append({
                            "rect": pygame.Rect(bx, by, brick_width, brick_height), 
                            "color_data": BRICK_COLORS[r]
                        })

    if not game_over and not victory:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 10:
            paddle.x -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle.right < SCREEN_WIDTH - 10:
            paddle.x += paddle_speed

        ball.x += ball_speed_x
        ball.y += ball_speed_y
        
        ball_trail.append((ball.centerx, ball.centery))
        if len(ball_trail) > 8:
            ball_trail.pop(0)

        if ball.left <= 0:
            ball.left = 0
            ball_speed_x *= -1
        elif ball.right >= SCREEN_WIDTH:
            ball.right = SCREEN_WIDTH
            ball_speed_x *= -1
            
        if ball.top <= 0:
            ball.top = 0
            ball_speed_y *= -1

        if ball.bottom >= SCREEN_HEIGHT:
            lives -= 1
            if lives <= 0:
                game_over = True
            else:
                ball.x = SCREEN_WIDTH // 2
                ball.y = SCREEN_HEIGHT // 2 + 50
                ball_speed_x = 5 * random.choice([-1, 1])
                ball_speed_y = -6
                paddle.x = (SCREEN_WIDTH - paddle_width) // 2
                ball_trail.clear()

        if ball.colliderect(paddle) and ball_speed_y > 0:
            relative_intersect = (paddle.centerx - ball.centerx) / (paddle_width / 2)
            relative_intersect = max(-0.85, min(0.85, relative_intersect))
            ball_speed_y = -abs(ball_speed_y)
            ball_speed_x = -relative_intersect * 8

        for brick in bricks[:]:
            if ball.colliderect(brick["rect"]):
                score += 15
                spawn_particles(brick["rect"].centerx, brick["rect"].centery, brick["color_data"]["glow"])
                
                overlap_x = min(ball.right, brick["rect"].right) - max(ball.left, brick["rect"].left)
                overlap_y = min(ball.bottom, brick["rect"].bottom) - max(ball.top, brick["rect"].top)
                
                if overlap_x < overlap_y:
                    ball_speed_x *= -1
                else:
                    ball_speed_y *= -1
                
                bricks.remove(brick)
                break

        if len(bricks) == 0:
            victory = True

        for p in particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 0.04
            if p["life"] <= 0:
                particles.remove(p)

    screen.fill(BG_COLOR)

    for x in range(0, SCREEN_WIDTH, 40):
        pygame.draw.line(screen, (20, 22, 35), (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, 40):
        pygame.draw.line(screen, (20, 22, 35), (0, y), (SCREEN_WIDTH, y), 1)

    for idx, pos in enumerate(ball_trail):
        alpha_ratio = (idx + 1) / len(ball_trail)
        trail_color = (int(BALL_COLOR[0] * alpha_ratio), int(BALL_COLOR[1] * alpha_ratio), int(BALL_COLOR[2] * alpha_ratio))
        trail_radius = int((ball_size // 2) * (alpha_ratio * 0.8))
        if trail_radius > 0:
            pygame.draw.circle(screen, trail_color, pos, trail_radius)

    for brick in bricks:
        r = brick["rect"]
        c = brick["color_data"]
        pygame.draw.rect(screen, c["glow"], r, border_radius=4)
        inner_r = r.inflate(-4, -4)
        pygame.draw.rect(screen, c["base"], inner_r, border_radius=2)

    pygame.draw.rect(screen, PADDLE_COLOR, paddle, border_radius=6)
    pygame.draw.rect(screen, WHITE, paddle.inflate(-6, -10), border_radius=3)

    pygame.draw.circle(screen, BALL_COLOR, (ball.centerx, ball.centery), ball_size // 2)
    pygame.draw.circle(screen, WHITE, (ball.centerx - 2, ball.centery - 2), 2)

    for p in particles:
        alpha_color = tuple(max(0, min(255, int(c_val * p["life"]))) for c_val in p["color"])
        pygame.draw.circle(screen, alpha_color, (int(p["x"]), int(p["y"])), int(p["radius"]))

    score_lbl = font_hud.render(f"SCORE // {score:04d}", True, SCORE_COLOR)
    lives_lbl = font_hud.render(f"MATRIX LIVES // {lives}", True, BALL_COLOR if lives == 1 else PADDLE_COLOR)
    screen.blit(score_lbl, (30, 25))
    screen.blit(lives_lbl, (SCREEN_WIDTH - 200, 25))

    if game_over or victory:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 10, 200))
        screen.blit(overlay, (0, 0))
        
        msg_str = "VICTORY ACHIEVED" if victory else "SYSTEM CRASH: GAME OVER"
        col = PADDLE_COLOR if victory else BALL_COLOR
        
        title_txt = font_title.render(msg_str, True, col)
        sub_txt = font_hud.render("PRESS [ SPACE ] TO RE-INITIALIZE", True, WHITE)
        
        screen.blit(title_txt, (SCREEN_WIDTH // 2 - title_txt.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    pygame.display.flip()
    clock.tick(FPS)
