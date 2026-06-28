import pygame
import random
import sys
import math

pygame.init()
pygame.font.init()

# Luxury Classic Color Palette
COLOR_BG = (5, 12, 10)             
COLOR_GRID = (10, 22, 16)          
COLOR_BEAM = (230, 205, 150)       
COLOR_BEAM_DARK = (125, 100, 55)   
COLOR_HERO = (255, 255, 252)       
COLOR_HAZARD = (165, 25, 35)       
COLOR_HAZARD_GOLD = (250, 215, 125)
COLOR_PANEL_BG = (8, 18, 14, 245)  
COLOR_TEXT_GOLD = (245, 195, 90)   
COLOR_TEXT_DIM = (120, 90, 40)     

class FilamentParticle:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-1.0, 2.0)
        self.life = 1.0  
        self.decay = random.uniform(0.02, 0.05)
        self.color = color
        self.size = random.choice([1, 2])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay

    def draw(self, surface, camera_y):
        if self.life <= 0: return
        r = max(0, min(255, int(self.color[0] * self.life)))
        g = max(0, min(255, int(self.color[1] * self.life)))
        b = max(0, min(255, int(self.color[2] * self.life)))
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y - camera_y)), self.size)

class Counterweight:
    def __init__(self, x, y, boundary_left, boundary_right, start_dir):
        self.x = float(x)
        self.y = float(y)
        self.boundary_left = boundary_left
        self.boundary_right = boundary_right
        self.speed = 2.0 if start_dir == "RIGHT" else -2.0
        self.radius = 11
        # Track the true center for pixel-perfect circular collision checks
        self.center_x = self.x + self.radius
        self.center_y = self.y + self.radius
        self.pulse_anim = random.uniform(0, 6.28)

    def update(self):
        self.x += self.speed
        self.center_x = self.x + self.radius
        self.pulse_anim += 0.05
        if self.x <= self.boundary_left:
            self.x = float(self.boundary_left)
            self.speed *= -1
        elif self.x + (self.radius * 2) >= self.boundary_right:
            self.x = float(self.boundary_right - (self.radius * 2))
            self.speed *= -1

    def draw(self, surface, camera_y):
        render_y = int(self.y - camera_y)
        cx = int(self.center_x)
        cy = int(self.center_y - camera_y)
        
        # Purely cosmetic suspension line
        pygame.draw.line(surface, COLOR_GRID, (cx, render_y - 20), (cx, cy), 1)
        pygame.draw.circle(surface, COLOR_BEAM_DARK, (cx, render_y - 20), 2)

        pulse_val = math.sin(self.pulse_anim) * 2
        pygame.draw.circle(surface, COLOR_BEAM, (cx, cy), int(self.radius + 3 + pulse_val), 1)
        pygame.draw.circle(surface, COLOR_BEAM_DARK, (cx, cy), self.radius + 1, 1)

        pygame.draw.circle(surface, COLOR_HAZARD, (cx, cy), self.radius - 1)
        
        pygame.draw.line(surface, COLOR_HAZARD_GOLD, (cx - self.radius + 3, cy), (cx + self.radius - 3, cy), 1)
        pygame.draw.line(surface, COLOR_HAZARD_GOLD, (cx, cy - self.radius + 3), (cx, cy + self.radius - 3), 1)
        pygame.draw.circle(surface, COLOR_HERO, (cx, cy), 2)

class StructuralBeam:
    def __init__(self, y, shaft_left, shaft_right, force_solid=False):
        self.y = float(y)
        self.shaft_left = shaft_left
        self.shaft_right = shaft_right
        self.has_gap = False if force_solid else (random.random() < 0.35)
        self.gap_w = 130
        self.gap_start = random.randint(shaft_left + 90, shaft_right - 90 - self.gap_w)
        self.gap_end = self.gap_start + self.gap_w

    def draw(self, surface, camera_y):
        render_y = int(self.y - camera_y)
        
        def draw_luxury_segment(x1, x2):
            if x1 >= x2: return
            pygame.draw.line(surface, COLOR_BEAM_DARK, (x1, render_y + 2), (x2, render_y + 2), 6)
            pygame.draw.line(surface, COLOR_BEAM, (x1, render_y), (x2, render_y), 3)
            
            for step in range(int(x1) + 6, int(x2), 14):
                pygame.draw.line(surface, COLOR_BEAM_DARK, (step, render_y + 4), (step + 6, render_y - 5), 1)
                pygame.draw.line(surface, COLOR_BEAM_DARK, (step + 6, render_y + 4), (step, render_y - 5), 1)
                
            pygame.draw.circle(surface, COLOR_TEXT_GOLD, (int(x1), render_y + 1), 3)
            pygame.draw.circle(surface, COLOR_TEXT_GOLD, (int(x2), render_y + 1), 3)

        if self.has_gap:
            draw_luxury_segment(self.shaft_left + 24, self.gap_start)
            draw_luxury_segment(self.gap_end, self.shaft_right - 24)
            pygame.draw.circle(surface, COLOR_HAZARD, (self.gap_start, render_y + 1), 4, 1)
            pygame.draw.circle(surface, COLOR_HAZARD, (self.gap_end, render_y + 1), 4, 1)
        else:
            draw_luxury_segment(self.shaft_left + 24, self.shaft_right - 24)

class CyberClimbGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("High-Line: Ultimate Premium Ascent")
        self.clock = pygame.time.Clock()
        
        self.font_title = pygame.font.SysFont("Georgia", int(self.width * 0.038), bold=False, italic=True)
        self.font_ui = pygame.font.SysFont("Courier New", 14, bold=True)
        self.font_digits = pygame.font.SysFont("Courier New", 26, bold=True)
        
        self.fps = 60
        self.state = "WELCOME"
        
        self.shaft_left = self.width // 2 - 280
        self.shaft_right = self.width // 2 + 280
        
        self.player_x = float(self.width // 2)
        self.player_y = float(self.height - 100)
        self.player_w = 24
        self.player_h = 24  
        self.vel_y = 0.0
        self.is_grounded = True
        self.is_magnetized = False
        
        self.battery = 100.0
        self.max_battery = 100.0
        self.score = 0
        self.highest_y = self.player_y
        self.camera_y = 0.0
        
        self.beams = []        
        self.hazards = []
        self.particles = []
        
        self.main_loop()

    def generate_level_floor(self, y_pos, force_solid=False):
        beam = StructuralBeam(y_pos, self.shaft_left, self.shaft_right, force_solid)
        self.beams.append(beam)
        
        if y_pos < self.height - 150:
            self.hazards.append(Counterweight(self.shaft_left + 30, y_pos - 24, self.shaft_left + 24, self.shaft_right - 50, "RIGHT"))
            self.hazards.append(Counterweight(self.shaft_right - 80, y_pos - 24, self.shaft_left + 24, self.shaft_right - 50, "LEFT"))

    def reset_game(self):
        self.player_x = float(self.width // 2)
        self.player_y = float(self.height - 100)
        self.vel_y = 0.0
        self.is_grounded = True
        self.is_magnetized = False
        self.battery = self.max_battery
        self.score = 0
        self.highest_y = self.player_y
        self.camera_y = float(self.player_y - (self.height * 0.7))
        
        self.beams = []
        self.hazards = []
        self.particles = []
        
        for i in range(10):
            y_pos = self.height - 60 - (i * 145)
            is_first_floor = (i == 0)
            self.generate_level_floor(y_pos, force_solid=is_first_floor)
            
        self.state = "PLAYING"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.state in ["WELCOME", "GAMEOVER"] and event.key == pygame.K_RETURN:
                    self.reset_game()
                if self.state == "PLAYING" and self.is_grounded and not self.is_magnetized:
                    if event.key in [pygame.K_w, pygame.K_UP, pygame.K_SPACE]:
                        self.vel_y = -15.2  
                        self.is_grounded = False
                        for _ in range(15):
                            self.particles.append(FilamentParticle(self.player_x + self.player_w//2, self.player_y + self.player_h, COLOR_BEAM))

    def update_physics(self):
        if self.state != "PLAYING":
            return

        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if self.battery > 3:
                self.is_magnetized = True
                self.battery = max(0.0, self.battery - 0.85)
                self.vel_y = 0.0  
                if random.random() < 0.4:
                    self.particles.append(FilamentParticle(random.uniform(self.player_x, self.player_x + self.player_w), self.player_y + self.player_h//2, COLOR_TEXT_GOLD))
            else:
                self.is_magnetized = False
        else:
            self.is_magnetized = False
            self.battery = min(self.max_battery, self.battery + 0.15)

        speed = float(6.0)
        moving = False
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player_x = max(float(self.shaft_left + 26), self.player_x - speed)
            moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player_x = min(float(self.shaft_right - 26 - self.player_w), self.player_x + speed)
            moving = True

        if moving and self.is_grounded and random.random() < 0.3:
            self.particles.append(FilamentParticle(self.player_x + self.player_w//2, self.player_y + self.player_h, COLOR_BEAM_DARK))

        if not self.is_magnetized:
            self.vel_y += 0.72  
            self.player_y += self.vel_y
        
        if self.vel_y >= 0:
            self.is_grounded = False
            for beam in self.beams:
                if abs((self.player_y + self.player_h) - beam.y) < 10:
                    if self.player_x + self.player_w > self.shaft_left and self.player_x < self.shaft_right:
                        if beam.has_gap and (beam.gap_start < self.player_x + (self.player_w//2) < beam.gap_end):
                            continue 
                        
                        self.player_y = float(beam.y - self.player_h)
                        self.vel_y = 0.0
                        self.is_grounded = True
                        break

        if self.player_y < self.highest_y:
            self.highest_y = self.player_y
            self.score = int((self.height - 100 - self.highest_y) // 10)

        target_cam_y = self.player_y - (self.height * 0.65)
        self.camera_y += (target_cam_y - self.camera_y) * 0.09

        highest_generated_beam = self.beams[-1].y
        if self.camera_y < highest_generated_beam + 300:
            self.generate_level_floor(highest_generated_beam - 145, force_solid=False)

        if len(self.beams) > 18:
            self.beams.pop(0)
            if len(self.hazards) > 1:
                self.hazards.pop(0)
                self.hazards.pop(0)

        # Player midpoints for accurate circle math
        player_mid_x = self.player_x + (self.player_w / 2)
        player_mid_y = self.player_y + (self.player_h / 2)

        for hazard in self.hazards:
            hazard.update() 
            
            # Find closest point on square player to the circle hazard core
            closest_x = max(self.player_x, min(hazard.center_x, self.player_x + self.player_w))
            closest_y = max(self.player_y, min(hazard.center_y, self.player_y + self.player_h))
            
            # Calculate actual distance to circle edge
            dist_x = hazard.center_x - closest_x
            dist_y = hazard.center_y - closest_y
            distance_squared = (dist_x ** 2) + (dist_y ** 2)
            
            if distance_squared < (hazard.radius ** 2):
                self.state = "GAMEOVER"

        if self.player_y - self.camera_y > self.height:
            self.state = "GAMEOVER"

        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

    def draw_classic_hud(self):
        hud_w, hud_h = 540, 155
        hud_canvas = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
        
        pygame.draw.rect(hud_canvas, COLOR_PANEL_BG, (0, 0, hud_w, hud_h), border_radius=6)
        pygame.draw.rect(hud_canvas, COLOR_TEXT_DIM, (0, 0, hud_w, hud_h), 2, border_radius=6)
        pygame.draw.rect(hud_canvas, COLOR_TEXT_GOLD, (3, 3, hud_w - 6, hud_h - 6), 1, border_radius=4)
        
        corner_sz = 14
        corners = [(3, 3), (hud_w - corner_sz - 3, 3), (3, hud_h - corner_sz - 3), (hud_w - corner_sz - 3, hud_h - corner_sz - 3)]
        for cx, cy in corners:
            pygame.draw.rect(hud_canvas, COLOR_TEXT_GOLD, (cx, cy, corner_sz, corner_sz))
            pygame.draw.rect(hud_canvas, COLOR_BG, (cx + 3, cy + 3, corner_sz - 6, corner_sz - 6))

        lbl_score = self.font_ui.render("CHRONO ASCENT TELEMETRY METRIC", True, COLOR_TEXT_DIM)
        val_score = self.font_digits.render(f"{self.score:05} INDEX UNITS", True, COLOR_TEXT_GOLD)
        lbl_battery = self.font_ui.render("MAGNETIC CORE AMPLIFIER STORAGE BUFFER", True, COLOR_TEXT_DIM)
        
        col1_x = 24
        col2_x = hud_w - 180
        txt_strain = self.font_ui.render("CALIBRATED FLOW", True, COLOR_TEXT_GOLD)
        
        hud_canvas.blit(lbl_score, (col1_x, 16))
        hud_canvas.blit(val_score, (col1_x, 34))
        hud_canvas.blit(txt_strain, (col2_x, 22))
        hud_canvas.blit(lbl_battery, (col1_x, 82))
        
        bar_x, bar_y, bar_w, bar_h = 24, 106, hud_w - 48, 18
        pygame.draw.rect(hud_canvas, COLOR_TEXT_DIM, (bar_x, bar_y, bar_w, bar_h), 1)
        
        total_segments = 24
        fill_segments = int((self.battery / self.max_battery) * total_segments)
        seg_w = (bar_w - 6) // total_segments
        
        for i in range(fill_segments):
            pygame.draw.rect(hud_canvas, COLOR_TEXT_GOLD, (bar_x + 4 + (i * seg_w), bar_y + 4, seg_w - 2, bar_h - 8))

        self.screen.blit(hud_canvas, (50, 50))

    def draw_structure(self):
        for y in range(0, self.height, 40):
            scrolled_y = (y - int(self.camera_y * 0.30)) % self.height
            pygame.draw.line(self.screen, COLOR_GRID, (self.shaft_left, scrolled_y), (self.shaft_right, scrolled_y), 1)

        col_w = 26
        pygame.draw.rect(self.screen, (6, 18, 14), (self.shaft_left, 0, col_w, self.height))
        pygame.draw.rect(self.screen, (6, 18, 14), (self.shaft_right - col_w, 0, col_w, self.height))
        
        pygame.draw.line(self.screen, COLOR_BEAM_DARK, (self.shaft_left + col_w - 5, 0), (self.shaft_left + col_w - 5, self.height), 1)
        pygame.draw.line(self.screen, COLOR_BEAM, (self.shaft_left + col_w, 0), (self.shaft_left + col_w, self.height), 2)
        pygame.draw.line(self.screen, COLOR_BEAM_DARK, (self.shaft_right - col_w + 5, 0), (self.shaft_right - col_w + 5, self.height), 1)
        pygame.draw.line(self.screen, COLOR_BEAM, (self.shaft_right - col_w, 0), (self.shaft_right - col_w, self.height), 2)

        pygame.draw.line(self.screen, (12, 32, 24), (self.shaft_left + 4, 0), (self.shaft_left + 4, self.height), 2)
        pygame.draw.line(self.screen, (12, 32, 24), (self.shaft_right - 4, 0), (self.shaft_right - 4, self.height), 2)

        for beam in self.beams:
            beam.draw(self.screen, self.camera_y)

        for p in self.particles:
            p.draw(self.screen, self.camera_y)

        for hazard in self.hazards:
            hazard.draw(self.screen, self.camera_y)

        px = int(self.player_x)
        py = int(self.player_y - self.camera_y)
        half_w = self.player_w // 2
        half_h = self.player_h // 2
        mid_x = px + half_w
        mid_y = py + half_h
        
        hero_color = COLOR_TEXT_GOLD if self.is_magnetized else COLOR_HERO
        
        pygame.draw.circle(self.screen, hero_color, (mid_x, mid_y), half_w, 2)
        pygame.draw.circle(self.screen, COLOR_BEAM_DARK, (mid_x, mid_y), half_w - 4, 1)
        
        pygame.draw.rect(self.screen, hero_color, (px, py, 4, 4))
        pygame.draw.rect(self.screen, hero_color, (px + self.player_w - 4, py, 4, 4))
        pygame.draw.rect(self.screen, hero_color, (px, py + self.player_h - 4, 4, 4))
        pygame.draw.rect(self.screen, hero_color, (px + self.player_w - 4, py + self.player_h - 4, 4, 4))
        
        pygame.draw.polygon(self.screen, COLOR_TEXT_GOLD if not self.is_magnetized else COLOR_HERO, [
            (mid_x, py + 4),
            (px + self.player_w - 4, mid_y),
            (mid_x, py + self.player_h - 4),
            (px + 4, mid_y)
        ], 1)
        
        pygame.draw.circle(self.screen, hero_color, (mid_x, mid_y), 2)

    def draw(self):
        self.screen.fill(COLOR_BG)

        if self.state in ["PLAYING", "GAMEOVER"]:
            self.draw_structure()
            self.draw_classic_hud()

        if self.state == "WELCOME":
            title = self.font_title.render("HIGH-LINE // LUXURY ASCENT", True, COLOR_TEXT_GOLD)
            sub = self.font_ui.render("STEER A/D  //  JUMP W/SPACE  //  ENGAGE MAGNETIC CLING [HOLD SHIFT]  //  [ENTER RUN]", True, COLOR_BEAM)
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 40))
            self.screen.blit(sub, (self.width // 2 - sub.get_width() // 2, self.height // 2 + 40))

        elif self.state == "GAMEOVER":
            go_title = self.font_title.render("TELEMETRY INTERRUPTED: CORE CRITICAL", True, COLOR_HAZARD)
            go_sub = self.font_ui.render("ENTER SYSTEM INITIALIZE REBOOT  //  ESC TERMINATE SEQUENCER RUN", True, COLOR_BEAM)
            self.screen.blit(go_title, (self.width // 2 - go_title.get_width() // 2, self.height // 2 - 40))
            self.screen.blit(go_sub, (self.width // 2 - go_sub.get_width() // 2, self.height // 2 + 40))

        pygame.display.flip()

    def main_loop(self):
        while True:
            self.handle_events()
            self.update_physics()
            self.draw()
            self.clock.tick(self.fps)

if __name__ == "__main__":
    CyberClimbGame()