import pygame
import sys
import random
import math

pygame.init()

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
FPS = 60

BG_COLOR = (6, 4, 15)
P1_COLOR = (0, 255, 180)
P2_COLOR = (0, 190, 255)
TETHER_COLOR = (255, 0, 130)
CORE_COLOR = (255, 200, 0)
PORTAL_COLOR = (0, 255, 255)
ASTEROID_COLOR = (130, 120, 150)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("🌌 CYBER TETHER: ORBITAL FREIGHTERS 🌌")
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

def get_font(size, bold=False):
    try:
        return pygame.font.SysFont("Impact" if bold else "Arial", size)
    except:
        return pygame.font.Font(None, size)

font_ui = get_font(24, bold=True)
font_title = get_font(56, bold=True)

particles = []
screen_shake = 0

def spawn_particles(x, y, color, count=12, speed=5):
    for _ in range(count):
        particles.append({
            "x": x, "y": y,
            "vx": random.uniform(-speed, speed), "vy": random.uniform(-speed, speed),
            "radius": random.uniform(2, 5),
            "life": 1.0,
            "decay": random.uniform(0.02, 0.04),
            "color": color
        })

class Player:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 22
        self.angle = 0
        self.speed = 0.65
        self.friction = 0.94
        self.color = color
        self.controls = controls
        self.stun_timer = 0
        self.trail = []

    def update(self, keys, fx, fy):
        self.vx += fx
        self.vy += fy

        if self.stun_timer > 0:
            self.stun_timer -= 1
            self.vx *= 0.8
            self.vy *= 0.8
            self.x += self.vx
            self.y += self.vy
            return

        ax, ay = 0, 0
        if keys[self.controls['up']]:    ay -= self.speed
        if keys[self.controls['down']]:  ay += self.speed
        if keys[self.controls['left']]:  ax -= self.speed
        if keys[self.controls['right']]: ax += self.speed

        if ax != 0 or ay != 0:
            self.angle = math.degrees(math.atan2(-ay, ax)) - 90

        self.vx += ax
        self.vy += ay
        self.vx *= self.friction
        self.vy *= self.friction
        self.x += self.vx
        self.y += self.vy

        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))

        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

        if (ax != 0 or ay != 0) and random.random() > 0.5:
            rad = math.radians(self.angle + 90)
            spawn_particles(self.x + math.cos(rad)*self.radius, self.y - math.sin(rad)*self.radius, (255, 100, 0), count=1, speed=2)

    def draw(self, surface):
        for idx, pos in enumerate(self.trail):
            alpha = int((idx / len(self.trail)) * 90)
            t_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(t_surf, (*self.color, alpha), (self.radius, self.radius), int(self.radius * (idx / len(self.trail))))
            surface.blit(t_surf, (pos[0] - self.radius, pos[1] - self.radius))

        rad = math.radians(self.angle)
        p1 = (self.x + self.radius * math.sin(rad), self.y + self.radius * math.cos(rad))
        p2 = (self.x + self.radius * math.sin(rad + 2.4), self.y + self.radius * math.cos(rad + 2.4))
        p3 = (self.x + self.radius * math.sin(rad - 2.4), self.y + self.radius * math.cos(rad - 2.4))
        
        draw_color = (130, 130, 130) if self.stun_timer > 0 and (self.stun_timer // 4) % 2 == 0 else self.color
        pygame.draw.polygon(surface, draw_color, p123:=[p1, p2, p3])
        pygame.draw.polygon(surface, WHITE, p123, 2)

class Asteroid:
    def __init__(self):
        self.reset()

    def reset(self):
        self.radius = random.randint(25, 55)
        self.x = random.randint(self.radius, SCREEN_WIDTH - self.radius)
        self.y = random.randint(-200, -60)
        self.speed_y = random.uniform(2.0, 5.0)
        self.speed_x = random.uniform(-1.0, 1.0)
        self.rot_angle = 0
        self.rot_speed = random.uniform(-1.5, 1.5)
        self.num_vertices = random.randint(8, 11)
        self.offsets = [random.uniform(0.8, 1.2) for _ in range(self.num_vertices)]

    def update(self):
        self.y += self.speed_y
        self.x += self.speed_x
        self.rot_angle += self.rot_speed
        if self.x - self.radius < 0 or self.x + self.radius > SCREEN_WIDTH:
            self.speed_x *= -1
        if self.y - self.radius > SCREEN_HEIGHT:
            self.reset()

    def draw(self, surface):
        points = []
        for i in range(self.num_vertices):
            angle = math.radians(i * (360 / self.num_vertices) + self.rot_angle)
            r = self.radius * self.offsets[i]
            points.append((self.x + r * math.cos(angle), self.y + r * math.sin(angle)))
        pygame.draw.polygon(surface, (20, 16, 32), points)
        pygame.draw.polygon(surface, ASTEROID_COLOR, points, 2)

class PlasmaCore:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.pulse = 0

    def update(self, target_x, target_y, snapped):
        self.pulse += 0.15
        if not snapped:
            self.x += (target_x - self.x) * 0.25
            self.y += (target_y - self.y) * 0.25
        else:
            self.y += 7

    def draw(self, surface):
        pulse_r = self.radius + math.sin(self.pulse) * 4
        s = pygame.Surface((pulse_r*4, pulse_r*4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*CORE_COLOR, 60), (int(pulse_r*2), int(pulse_r*2)), int(pulse_r*1.8))
        pygame.draw.circle(s, (255, 255, 255, 200), (int(pulse_r*2), int(pulse_r*2)), self.radius)
        surface.blit(s, (int(self.x - pulse_r*2), int(self.y - pulse_r*2)))

def check_tether_collision(p1, p2, ast):
    dx, dy = p2.x - p1.x, p2.y - p1.y
    if dx == 0 and dy == 0: return False
    t = max(0.0, min(1.0, ((ast.x - p1.x) * dx + (ast.y - p1.y) * dy) / (dx*dx + dy*dy)))
    return math.hypot(ast.x - (p1.x + t * dx), ast.y - (p1.y + t * dy)) < ast.radius

p1_controls = {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d}
p2_controls = {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}

player1 = Player(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2, P1_COLOR, p1_controls)
player2 = Player((SCREEN_WIDTH // 3) * 2, SCREEN_HEIGHT // 2, P2_COLOR, p2_controls)

asteroids = [Asteroid() for _ in range(6)]
cargo_cores = []

score = 0
time_left = 60 * FPS
game_active = True
tether_snapped = False
tether_cooldown = 0

TETHER_REST_LEN = SCREEN_WIDTH * 0.2
TETHER_STIFFNESS = 0.0038
MAX_TETHER_DIST = SCREEN_WIDTH * 0.45

portal_rect = pygame.Rect(200, SCREEN_HEIGHT - 45, SCREEN_WIDTH - 400, 45)
portal_pulse = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
                
            if event.key == pygame.K_SPACE and not game_active:
                score = 0; time_left = 60 * FPS
                player1.x, player1.y = SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2
                player2.x, player2.y = (SCREEN_WIDTH // 3) * 2, SCREEN_HEIGHT // 2
                player1.vx = player1.vy = player2.vx = player2.vy = 0
                player1.stun_timer = player2.stun_timer = 0
                for a in asteroids: a.reset()
                cargo_cores.clear(); particles.clear()
                tether_snapped = False; tether_cooldown = 0
                game_active = True

    if game_active:
        keys = pygame.key.get_pressed()
        dist_ships = math.hypot(player1.x - player2.x, player1.y - player2.y)
        f1x, f1y, f2x, f2y = 0, 0, 0, 0
        
        if not tether_snapped:
            if dist_ships > TETHER_REST_LEN:
                displacement = dist_ships - TETHER_REST_LEN
                force_mag = displacement * TETHER_STIFFNESS
                ux = (player2.x - player1.x) / dist_ships
                uy = (player2.y - player1.y) / dist_ships
                f1x, f1y = ux * force_mag, uy * force_mag
                f2x, f2y = -ux * force_mag, -uy * force_mag
                
            if dist_ships > MAX_TETHER_DIST:
                tether_snapped = True
                tether_cooldown = 140
                screen_shake = 22
                spawn_particles((player1.x+player2.x)/2, (player1.y+player2.y)/2, TETHER_COLOR, count=25, speed=7)
        else:
            tether_cooldown -= 1
            if tether_cooldown <= 0:
                tether_snapped = False

        player1.update(keys, f1x, f1y)
        player2.update(keys, f2x, f2y)

        mid_x = (player1.x + player2.x) / 2
        mid_y = (player1.y + player2.y) / 2

        for ast in asteroids:
            ast.update()
            for p in [player1, player2]:
                if p.stun_timer == 0 and math.hypot(p.x - ast.x, p.y - ast.y) < (p.radius + ast.radius):
                    p.stun_timer = 50
                    screen_shake = 16
                    spawn_particles(p.x, p.y, (255, 60, 60), count=15, speed=6)
                    ast.reset()
            if not tether_snapped and check_tether_collision(player1, player2, ast):
                screen_shake = 6
                spawn_particles(ast.x, ast.y, TETHER_COLOR, count=12, speed=5)
                cargo_cores.append(PlasmaCore(ast.x, ast.y))
                ast.reset()

        portal_pulse += 0.08
        for core in cargo_cores[:]:
            core.update(mid_x, mid_y, tether_snapped)
            if portal_rect.collidepoint(core.x, core.y):
                score += 150
                screen_shake = 10
                spawn_particles(core.x, core.y, PORTAL_COLOR, count=20, speed=6)
                cargo_cores.remove(core)
            elif core.y > SCREEN_HEIGHT + 20:
                cargo_cores.remove(core)

        for p in particles[:]:
            p["x"] += p["vx"]; p["y"] += p["vy"]; p["life"] -= p["decay"]
            if p["life"] <= 0: particles.remove(p)

        time_left -= 1
        if time_left <= 0: game_active = False

    rx, ry = 0, 0
    if screen_shake > 0:
        rx = random.randint(-screen_shake, screen_shake)
        ry = random.randint(-screen_shake, screen_shake)
        screen_shake = int(screen_shake * 0.88)

    display_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    display_surface.fill(BG_COLOR)
    random.seed(450)
    for _ in range(65):
        sx, sy = random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)
        pygame.draw.circle(display_surface, (100, 95, 145), (sx, sy), random.choice([1, 2, 3]))
    random.seed()

    p_alpha = 50 + int(math.sin(portal_pulse) * 30)
    portal_surf = pygame.Surface((portal_rect.width, portal_rect.height), pygame.SRCALPHA)
    portal_surf.fill((*PORTAL_COLOR, p_alpha))
    pygame.draw.line(portal_surf, PORTAL_COLOR, (0, 0), (portal_rect.width, 0), 4)
    display_surface.blit(portal_surf, (portal_rect.x, portal_rect.y))
    
    port_lbl = font_ui.render("EXTRACTION SLOTS - DROP CARGO HERE", True, PORTAL_COLOR)
    display_surface.blit(port_lbl, (SCREEN_WIDTH // 2 - port_lbl.get_width() // 2, SCREEN_HEIGHT - 34))
    if game_active:
        if not tether_snapped:
            steps = 32
            current_color = TETHER_COLOR
            if dist_ships > MAX_TETHER_DIST * 0.78:
                current_color = (255, 30, 30) if (time_left // 4) % 2 == 0 else TETHER_COLOR
            
            for i in range(steps):
                r = i / steps
                lx = player1.x + (player2.x - player1.x) * r + random.uniform(-2, 2)
                ly = player1.y + (player2.y - player1.y) * r + random.uniform(-2, 2)
                pygame.draw.circle(display_surface, current_color, (int(lx), int(ly)), 5)
            pygame.draw.line(display_surface, WHITE, (player1.x, player1.y), (player2.x, player2.y), 1)
        elif tether_cooldown > 0 and (tether_cooldown // 6) % 2 == 0:
            warn = font_ui.render("TETHER LINE SEVERED: DIST CHARGE SNAPBACK...", True, (255, 40, 60))
            display_surface.blit(warn, (SCREEN_WIDTH // 2 - warn.get_width() // 2, SCREEN_HEIGHT // 2 + 120))

        for ast in asteroids: ast.draw(display_surface)
        for core in cargo_cores: core.draw(display_surface)
        player1.draw(display_surface)
        player2.draw(display_surface)

        for p in particles:
            col = (int(p["color"][0] * p["life"]), int(p["color"][1] * p["life"]), int(p["color"][2] * p["life"]))
            pygame.draw.circle(display_surface, col, (int(p["x"]), int(p["y"])), max(1, int(p["radius"] * p["life"])))

    score_txt = font_ui.render(f"SECURED NET ASSETS: {score} CR", True, P1_COLOR)
    time_txt = font_ui.render(f"CONTRACT TIME: {max(0, time_left // FPS)}s", True, P2_COLOR)
    esc_txt = font_ui.render("PRESS [ESC] TO ABANDON MISSION", True, (120, 120, 140))
    
    display_surface.blit(score_txt, (40, 35))
    display_surface.blit(time_txt, (SCREEN_WIDTH - time_txt.get_width() - 40, 35))
    display_surface.blit(esc_txt, (40, SCREEN_HEIGHT - 35))

    if not game_active:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 4, 12, 235))
        display_surface.blit(overlay, (0, 0))

        over_title = font_title.render("CONSOLIDATION ENDED", True, WHITE)
        final_score = font_ui.render(f"TOTAL NET DIVIDENDS VALUE: {score} CREDITS", True, TETHER_COLOR)
        restart_lbl = font_ui.render("PRESS [ SPACE ] TO SIGN NEXT MINING HARVEST LEASE", True, P1_COLOR)

        display_surface.blit(over_title, (SCREEN_WIDTH // 2 - over_title.get_width() // 2, SCREEN_HEIGHT // 2 - 70))
        display_surface.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, SCREEN_HEIGHT // 2))
        display_surface.blit(restart_lbl, (SCREEN_WIDTH // 2 - restart_lbl.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

    screen.blit(display_surface, (rx, ry))
    pygame.display.flip()
    clock.tick(FPS)