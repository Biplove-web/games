import pygame
import random
import sys
import math

pygame.init()
pygame.font.init()

# Luxury Cyberpunk Color Profile
COLOR_BG = (3, 4, 7)
COLOR_GRID = (10, 12, 22)
COLOR_STRUCT_FLASH = (25, 15, 30)
COLOR_PANEL = (8, 12, 20, 180)    # Ultra-translucent glass backing
COLOR_TEXT = (230, 240, 255)
COLOR_SUBTEXT = (90, 120, 160)

COLOR_POD_MAIN = (255, 255, 255)    # Platinum Gloss
COLOR_POD_NEON = (0, 230, 255)      # Sapphire Cyan Core
COLOR_LASER = (255, 0, 90)          # Ruby Neon Security Grid
COLOR_PHASE = (140, 0, 255)         # Amethyst Violet Phase Shield

class LaserGrid:
    def __init__(self, y, screen_width):
        self.y = y
        self.width = screen_width
        self.gap_width = 240
        self.type = random.choice(["LEFT", "RIGHT", "CENTER"])
        
        if self.type == "LEFT":
            self.gap_start = random.randint(120, int(screen_width * 0.28))
        elif self.type == "RIGHT":
            self.gap_start = random.randint(int(screen_width * 0.62), screen_width - 120 - self.gap_width)
        else:
            self.gap_start = (screen_width // 2) - (self.gap_width // 2)
            
        self.gap_end = self.gap_start + self.gap_width
        self.has_passed_pod = False

    def update(self, speed):
        self.y -= speed

    def draw(self, surface):
        if self.gap_start > 0:
            pygame.draw.line(surface, (100, 0, 30), (0, self.y), (self.gap_start, self.y), 6)
            pygame.draw.line(surface, COLOR_LASER, (0, self.y), (self.gap_start, self.y), 2)
            pygame.draw.circle(surface, COLOR_LASER, (self.gap_start, int(self.y)), 6)
        if self.gap_end < self.width:
            pygame.draw.line(surface, (100, 0, 30), (self.gap_end, self.y), (self.width, self.y), 6)
            pygame.draw.line(surface, COLOR_LASER, (self.gap_end, self.y), (self.width, self.y), 2)
            pygame.draw.circle(surface, COLOR_LASER, (self.gap_end, int(self.y)), 6)

class VerticalDropGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("Apex Velocity: Vertical Drop")
        self.clock = pygame.time.Clock()
        
        self.font_title = pygame.font.SysFont("Impact", int(self.width * 0.05))
        self.font_ui = pygame.font.SysFont("Consolas", 16, bold=True)
        self.font_digits = pygame.font.SysFont("Impact", 28)
        self.font_telemetry = pygame.font.SysFont("Consolas", 13)
        
        self.fps = 60
        self.state = "WELCOME"
        
        self.pod_x = self.width // 2
        self.pod_y = self.height * 0.22
        self.pod_radius = 18
        
        self.base_speed = 7.0
        self.fall_speed = self.base_speed
        self.steer_speed = 9.5
        
        self.score_float = 0.0  # Precision decimal storage for seamless tracking
        self.score = 0
        self.energy = 100.0
        self.max_energy = 100.0
        self.is_phasing = False
        self.lasers = []
        
        self.bg_rings = [200, 400, 600, 800] 
        self.flash_intensity = 0
        
        self.main_loop()

    def reset_game(self):
        self.pod_x = self.width // 2
        self.score_float = 0.0
        self.score = 0
        self.energy = self.max_energy
        self.fall_speed = self.base_speed
        self.is_phasing = False
        self.lasers = []
        self.flash_intensity = 0
        
        for i in range(4):
            self.lasers.append(LaserGrid(self.height + 200 + (i * 360), self.width))
            
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

    def update_physics(self):
        if self.state != "PLAYING":
            return

        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_SPACE] and self.energy > 8:
            self.is_phasing = True
            self.energy = max(0.0, self.energy - 0.95)
        else:
            self.is_phasing = False
            self.energy = min(self.max_energy, self.energy + 0.22)

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.pod_x = max(self.pod_radius + 55, self.pod_x - self.steer_speed)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.pod_x = min(self.width - self.pod_radius - 55, self.pod_x + self.steer_speed)

        # Dynamic gradual velocity adjustment (maintaining identical progression curve)
        speed_multiplier = 1.0 + (self.score_float / 3500.0)
        self.fall_speed = min(26.0, self.base_speed * speed_multiplier)
        
        # CONTINUOUS METER DESCENT TRACKING
        # Fractional conversion of velocity delta to real-time depth meters per frame
        self.score_float += self.fall_speed * 0.06
        self.score = int(self.score_float)
        
        for i in range(len(self.bg_rings)):
            self.bg_rings[i] -= self.fall_speed * 0.4
            if self.bg_rings[i] < -100:
                self.bg_rings[i] = self.height + 100

        if self.flash_intensity > 0:
            self.flash_intensity = max(0, self.flash_intensity - 4)

        for laser in self.lasers:
            laser.update(self.fall_speed)
            if not laser.has_passed_pod and laser.y < self.pod_y:
                laser.has_passed_pod = True
                self.flash_intensity = 90
            
        if len(self.lasers) > 0 and self.lasers[0].y < -50:
            self.lasers.pop(0)
            
        while len(self.lasers) < 5:
            last_y = self.lasers[-1].y if self.lasers else self.height
            self.lasers.append(LaserGrid(last_y + random.randint(340, 440), self.width))

        self.check_collisions()

    def check_collisions(self):
        if self.is_phasing:
            return 

        for laser in self.lasers:
            if abs(self.pod_y - laser.y) < (self.pod_radius + 4):
                if self.pod_x < laser.gap_start or self.pod_x > laser.gap_end:
                    self.state = "GAMEOVER"

    def draw_luxury_hud(self):
        hud_w, hud_h = 420, 175
        hud_canvas = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
        
        pygame.draw.rect(hud_canvas, COLOR_PANEL, (0, 0, hud_w, hud_h), border_radius=12)
        pygame.draw.rect(hud_canvas, COLOR_POD_NEON, (0, 0, hud_w, hud_h), 1, border_radius=12)
        
        pygame.draw.line(hud_canvas, COLOR_POD_NEON, (0, 0), (0, 20), 3)
        pygame.draw.line(hud_canvas, COLOR_POD_NEON, (0, 0), (20, 0), 3)
        
        lbl_score = self.font_ui.render("DEPTH MATRIX DATASET", True, COLOR_SUBTEXT)
        val_score = self.font_digits.render(f"{self.score:06} M", True, COLOR_TEXT)
        lbl_energy = self.font_ui.render("PHASE SHIELD CORE CAPACITY", True, COLOR_SUBTEXT)
        
        kmh = int(self.fall_speed * 18)
        txt_velocity = self.font_telemetry.render(f"VELOCITY: {kmh} KM/H", True, COLOR_POD_NEON)
        txt_gforce = self.font_telemetry.render(f"G-FORCE : {1.0 + (self.fall_speed/10.0):.2f} G", True, COLOR_TEXT)
        
        hud_canvas.blit(lbl_score, (25, 18))
        hud_canvas.blit(val_score, (25, 38))
        hud_canvas.blit(txt_velocity, (255, 20))
        hud_canvas.blit(txt_gforce, (255, 42))
        hud_canvas.blit(lbl_energy, (25, 92))
        
        bar_x, bar_y, cell_w, cell_h, gap = 25, 122, 6, 14, 3
        max_cells = 41
        active_cells = int((self.energy / self.max_energy) * max_cells)
        
        for i in range(max_cells):
            cx = bar_x + i * (cell_w + gap)
            is_active = i < active_cells
            cell_color = COLOR_PHASE if is_active else (22, 26, 38)
            pygame.draw.rect(hud_canvas, cell_color, (cx, bar_y, cell_w, cell_h))
            if is_active and i == active_cells - 1:
                pygame.draw.rect(hud_canvas, (255, 255, 255), (cx, bar_y, cell_w, cell_h), 1)

        self.screen.blit(hud_canvas, (50, 50))

    def draw_pod(self):
        core_color = COLOR_PHASE if self.is_phasing else COLOR_POD_NEON
        
        for i in range(5):
            ty = int(self.pod_y - (i * self.fall_speed * 0.7))
            t_radius = max(2, self.pod_radius - (i * 3))
            alpha = max(0, 150 - (i * 35))
            pygame.draw.circle(self.screen, (*core_color, alpha), (int(self.pod_x), ty), t_radius)

        pygame.draw.circle(self.screen, COLOR_POD_MAIN, (int(self.pod_x), int(self.pod_y)), self.pod_radius)
        pygame.draw.circle(self.screen, core_color, (int(self.pod_x), int(self.pod_y)), self.pod_radius - 5, 3)
        pygame.draw.circle(self.screen, COLOR_BG, (int(self.pod_x), int(self.pod_y)), 4)

    def draw(self):
        if self.flash_intensity > 0:
            flash_color = (COLOR_BG[0] + self.flash_intensity//4, COLOR_BG[1], COLOR_BG[2] + self.flash_intensity//3)
            self.screen.fill(flash_color)
        else:
            self.screen.fill(COLOR_BG)
        
        for ring_y in self.bg_rings:
            rect_h = 35
            pygame.draw.rect(self.screen, (10, 14, 25), (40, int(ring_y), self.width - 80, rect_h))
            pygame.draw.line(self.screen, (22, 28, 48), (40, int(ring_y)), (self.width - 40, int(ring_y)), 1)
            pygame.draw.line(self.screen, (22, 28, 48), (40, int(ring_y) + rect_h), (self.width - 40, int(ring_y) + rect_h), 1)

        grid_space = 80
        for x in range(40, self.width - 40, grid_space):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, self.height), 1)

        pygame.draw.rect(self.screen, (14, 16, 24), (0, 0, 50, self.height))
        pygame.draw.rect(self.screen, (14, 16, 24), (self.width - 50, 0, 50, self.height))
        
        pygame.draw.line(self.screen, COLOR_POD_NEON, (50, 0), (50, self.height), 2)
        pygame.draw.line(self.screen, COLOR_POD_NEON, (self.width - 50, 0), (self.width - 50, self.height), 2)

        if self.state in ["PLAYING", "GAMEOVER"]:
            for laser in self.lasers:
                laser.draw(self.screen)
            self.draw_pod()
            self.draw_luxury_hud()

        if self.state == "WELCOME":
            title = self.font_title.render("APEX VELOCITY // VERTICAL DROP", True, COLOR_POD_NEON)
            sub = self.font_ui.render("A/D OR ARROWS STEER  //  HOLD SPACEBAR TO PHASE  //  ENTER TO START", True, COLOR_TEXT)
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 40))
            self.screen.blit(sub, (self.width // 2 - sub.get_width() // 2, self.height // 2 + 40))

        elif self.state == "GAMEOVER":
            go_title = self.font_title.render("CORE CRITICAL: INTEGRITY LOST", True, COLOR_LASER)
            go_sub = self.font_ui.render("ENTER TO REBOOT TELEMETRY RUN  //  ESC TO ABORT", True, COLOR_TEXT)
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
    VerticalDropGame()