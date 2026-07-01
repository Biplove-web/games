import pygame
import random
import sys
import math

pygame.init()
pygame.font.init()

COLOR_BG = (4, 5, 8)
COLOR_GRID = (10, 12, 20)
COLOR_TRACK = (15, 18, 25)
COLOR_BORDER = (0, 180, 255)

COLOR_CAR_MAIN = (10, 12, 16)
COLOR_CAR_ACCENT = (0, 210, 255)
COLOR_CAR_SHADOW = (2, 3, 5)
COLOR_HEADLIGHT = (230, 245, 255)
COLOR_TAILLIGHT = (255, 0, 85)
COLOR_GLASS = (0, 80, 150)

COLOR_TRAIL = (0, 150, 255)
COLOR_TEXT = (210, 220, 240)
COLOR_TIME_BAR = (0, 255, 130)
COLOR_HUD_BG = (12, 16, 26, 120)

class Particle:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-2.5, 2.5)
        self.vy = random.uniform(-2.5, 2.5)
        self.lifetime = random.randint(15, 25)
        self.color = color

    def update(self, scroll):
        self.x += self.vx
        self.y += self.vy + scroll
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            alpha = min(255, max(0, self.lifetime * 12))
            p_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*self.color, alpha), (2, 2), 2)
            surface.blit(p_surf, (int(self.x) - 2, int(self.y) - 2))

class CyberDriftLuxury:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("Cyber Drift Luxury")
        self.clock = pygame.time.Clock()
        
        self.font_title = pygame.font.SysFont("Impact", int(self.width * 0.05))
        self.font_ui = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_digits = pygame.font.SysFont("Impact", 32)
        self.font_sub = pygame.font.SysFont("Consolas", 20, bold=True)
        
        self.fps = 60
        self.state = "WELCOME"
        
        self.car_x = self.width // 2
        self.car_y = self.height * 0.75
        self.car_angle = 270.0
        self.speed = 0.0
        self.max_speed = 15.0
        self.accel = 0.22
        self.decel = 0.35            
        self.friction = 0.05
        
        self.track_points = []
        self.track_width = 240
        self.score = 0
        self.trails = []
        self.particles = []
        self.is_braking = False
        
        self.max_time = 90.0         
        self.time_left = self.max_time
        self.gameover_reason = "CRITICAL CRASH"
        
        self.main_loop()

    def reset_game(self):
        self.car_x = self.width // 2
        self.car_y = self.height * 0.75
        self.car_angle = 270.0
        self.speed = 0.0
        self.generate_initial_track()
        self.score = 0
        self.trails = []
        self.particles = []
        self.time_left = self.max_time
        self.state = "PLAYING"

    def generate_initial_track(self):
        self.track_points = []
        current_x = self.width // 2
        current_y = self.height + 300
        while current_y > -200:
            current_y -= 80
            self.track_points.append([current_x, current_y])

    def update_track(self, scroll_speed):
        for p in self.track_points:
            p[1] += scroll_speed
            
        while len(self.track_points) > 0 and self.track_points[0][1] > self.height + 200:
            self.track_points.pop(0)
            self.score += 25
            
        while len(self.track_points) < 30:
            last_x, last_y = self.track_points[-1] if self.track_points else (self.width // 2, -80)
            next_y = last_y - 80
            max_turn = 75
            next_x = last_x + random.randint(-max_turn, max_turn)
            next_x = max(int(self.width * 0.2), min(int(self.width * 0.8), next_x))
            self.track_points.append([next_x, next_y])

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
            for p in self.particles[:]:
                p.update(0)
                if p.lifetime <= 0: self.particles.remove(p)
            return

        self.time_left -= 1.0 / self.fps
        if self.time_left <= 0:
            self.time_left = 0
            self.gameover_reason = "CHRONO DEPLETED"
            self.state = "GAMEOVER"
            return

        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]:
            self.speed = min(self.max_speed, self.speed + self.accel)
            self.is_braking = False
        elif keys[pygame.K_DOWN]:
            self.speed = max(0.0, self.speed - self.decel)
            self.is_braking = True if self.speed > 0 else False
        else:
            self.speed = max(0.0, self.speed - self.friction)
            self.is_braking = False

        rad = math.radians(self.car_angle)
        
        is_steering = False
        if self.speed > 1:
            turn_factor = 4.6 * (1.0 - (self.speed / (self.max_speed * 1.6)))
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: 
                self.car_angle -= turn_factor
                is_steering = True
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: 
                self.car_angle += turn_factor
                is_steering = True

        move_x = self.speed * math.cos(rad)
        scroll_speed = self.speed * abs(math.sin(rad)) if math.sin(rad) < 0 else self.speed * 0.18
        
        self.car_x += move_x
        self.update_track(scroll_speed)

        for t in self.trails:
            t[1] += scroll_speed

        if self.speed > 4 and is_steering:
            sin_a, cos_a = math.sin(rad), math.cos(rad)
            tl_x, tl_y = self.car_x - 14 * sin_a, self.car_y + 14 * cos_a
            tr_x, tr_y = self.car_x + 14 * sin_a, self.car_y - 14 * cos_a
            self.trails.append([tl_x, tl_y, 35])
            self.trails.append([tr_x, tr_y, 35])
            
            self.time_left = min(self.max_time, self.time_left + 0.04) 

            if random.random() < 0.5:
                self.particles.append(Particle(self.car_x, self.car_y, COLOR_CAR_ACCENT))

        for t in self.trails[:]:
            t[2] -= 1
            if t[2] <= 0: self.trails.remove(t)

        for p in self.particles[:]:
            p.update(scroll_speed)
            if p.lifetime <= 0: self.particles.remove(p)

        self.check_collisions()

    def check_collisions(self):
        on_track = False
        for x, y in self.track_points:
            if abs(self.car_y - y) < 60:
                if x - self.track_width//2 < self.car_x < x + self.track_width//2:
                    on_track = True
                    break
        if not on_track:
            self.gameover_reason = "CRITICAL CRASH"
            self.state = "GAMEOVER"
            for _ in range(60):
                self.particles.append(Particle(self.car_x, self.car_y, COLOR_CAR_ACCENT))

    def draw_background(self, surface):
        surface.fill(COLOR_BG)
        grid = 60
        for x in range(0, self.width, grid):
            pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, grid):
            pygame.draw.line(surface, COLOR_GRID, (0, y), (self.width, y), 1)

    def draw_track(self, surface):
        if len(self.track_points) < 2: return
        left_poly, right_poly = [], []
        for x, y in self.track_points:
            left_poly.append((x - self.track_width // 2, y))
            right_poly.insert(0, (x + self.track_width // 2, y))

        pygame.draw.polygon(surface, COLOR_TRACK, left_poly + right_poly)

        for i in range(len(self.track_points) - 1):
            x1, y1 = self.track_points[i]
            x2, y2 = self.track_points[i+1]
            pygame.draw.aaline(surface, COLOR_BORDER, (x1 - self.track_width//2, y1), (x2 - self.track_width//2, y2))
            pygame.draw.aaline(surface, COLOR_BORDER, (x1 + self.track_width//2, y1), (x2 + self.track_width//2, y2))

    def draw_car(self, surface):
        rad = math.radians(self.car_angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        length, width = 44, 20

        glow_amt = int(25 + (self.speed * 2.5))
        glow_surf = pygame.Surface((160, 160), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COLOR_CAR_ACCENT, glow_amt), (80, 80), 60)
        surface.blit(glow_surf, (int(self.car_x) - 80, int(self.car_y) - 80))

        hl_len = 160
        hl_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        l_rad, r_rad = math.radians(self.car_angle - 12), math.radians(self.car_angle + 12)
        f_x, f_y = self.car_x + length * cos_a, self.car_y + length * sin_a
        p1 = (f_x - width*0.5*sin_a, f_y + width*0.5*cos_a)
        p4 = (f_x + width*0.5*sin_a, f_y - width*0.5*cos_a)
        p2 = (p1[0] + hl_len * math.cos(l_rad), p1[1] + hl_len * math.sin(l_rad))
        p3 = (p4[0] + hl_len * math.cos(r_rad), p4[1] + hl_len * math.sin(r_rad))
        pygame.draw.polygon(hl_surf, (200, 245, 255, 30), [p1, p2, p3, p4])
        surface.blit(hl_surf, (0, 0))

        def get_pt(f_factor, w_factor):
            px = self.car_x + length * f_factor * cos_a - width * w_factor * sin_a
            py = self.car_y + length * f_factor * sin_a + width * w_factor * cos_a
            return (px, py)

        wheels = [get_pt(0.6, 0.9), get_pt(0.6, -0.9), get_pt(-0.4, 0.9), get_pt(-0.4, -0.9)]
        for wx, wy in wheels:
            pygame.draw.circle(surface, (5, 5, 5), (int(wx), int(wy)), 8)
            pygame.draw.circle(surface, COLOR_CAR_ACCENT, (int(wx), int(wy)), 6, 2)

        chassis_poly = [get_pt(1.0, 0.0), get_pt(0.8, 0.7), get_pt(0.1, 0.8), get_pt(-0.6, 0.9), 
                        get_pt(-0.7, 0.0), get_pt(-0.6, -0.9), get_pt(0.1, -0.8), get_pt(0.8, -0.7)]
        pygame.draw.polygon(surface, COLOR_CAR_MAIN, chassis_poly)

        core_poly = [get_pt(0.8, 0.0), get_pt(0.6, 0.5), get_pt(0.1, 0.6), get_pt(-0.4, 0.7),
                     get_pt(-0.5, 0.0), get_pt(-0.4, -0.7), get_pt(0.1, -0.6), get_pt(0.6, -0.5)]
        pygame.draw.polygon(surface, COLOR_CAR_SHADOW, core_poly)
        pygame.draw.polygon(surface, COLOR_CAR_ACCENT, chassis_poly, 2)

        canopy = [get_pt(0.3, 0.0), get_pt(0.1, 0.45), get_pt(-0.25, 0.5), get_pt(-0.35, 0.0), get_pt(-0.25, -0.5), get_pt(0.1, -0.45)]
        pygame.draw.polygon(surface, COLOR_GLASS, canopy)
        pygame.draw.polygon(surface, (255, 255, 255), canopy, 1)

        pygame.draw.line(surface, COLOR_CAR_ACCENT, get_pt(0.7, 0.0), get_pt(0.3, 0.0), 3)
        pygame.draw.circle(surface, COLOR_HEADLIGHT, (int(p1[0]), int(p1[1])), 4)
        pygame.draw.circle(surface, COLOR_HEADLIGHT, (int(p4[0]), int(p4[1])), 4)

        b_color = COLOR_TAILLIGHT if self.is_braking else (100, 0, 25)
        pygame.draw.line(surface, b_color, get_pt(-0.65, 0.6), get_pt(-0.65, -0.6), 4)

    def draw_luxury_hud(self):
        hud_w, hud_h = 360, 150
        hud_x, hud_y = 40, 40
        hud_canvas = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
        pygame.draw.rect(hud_canvas, COLOR_HUD_BG, (0, 0, hud_w, hud_h), border_radius=8)
        
        pygame.draw.rect(hud_canvas, COLOR_CAR_ACCENT, (0, 0, hud_w, hud_h), 1, border_radius=8)
        pygame.draw.line(hud_canvas, COLOR_CAR_ACCENT, (0, 0), (0, 30), 4)
        pygame.draw.line(hud_canvas, COLOR_CAR_ACCENT, (0, 0), (30, 0), 4)
        pygame.draw.line(hud_canvas, COLOR_CAR_ACCENT, (hud_w-1, hud_h-30), (hud_w-1, hud_h), 4)
        pygame.draw.line(hud_canvas, COLOR_CAR_ACCENT, (hud_w-30, hud_h-1), (hud_w, hud_h-1), 4)
        
        lbl_score = self.font_ui.render("NET METRIC // SCORE", True, (100, 130, 160))
        val_score = self.font_digits.render(f"{self.score:06}", True, COLOR_TEXT)
        lbl_time = self.font_ui.render("CHRONO TRACKER", True, (100, 130, 160))
        
        t_color = COLOR_TIME_BAR if self.time_left > 20 else COLOR_TAILLIGHT
        val_time = self.font_digits.render(f"{self.time_left:04.1f} SEC", True, t_color)
        
        hud_canvas.blit(lbl_score, (20, 15))
        hud_canvas.blit(val_score, (20, 38))
        hud_canvas.blit(lbl_time, (20, 82))
        hud_canvas.blit(val_time, (20, 105))
        
        pygame.draw.line(hud_canvas, (30, 45, 70), (200, 25), (200, 125), 1)
        
        bar_x, bar_y, max_bar_w, bar_h = 220, 42, 115, 75
        pct = max(0.0, min(1.0, self.time_left / self.max_time))
        
        segments = 10
        seg_gap = 3
        seg_h = (bar_h - (segments - 1) * seg_gap) // segments
        active_segments = int(pct * segments)
        
        for i in range(segments):
            sy = bar_y + (segments - 1 - i) * (seg_h + seg_gap)
            is_active = i < active_segments
            seg_color = t_color if is_active else (20, 30, 45)
            pygame.draw.rect(hud_canvas, seg_color, (bar_x, sy, max_bar_w, seg_h))
            if is_active:
                pygame.draw.rect(hud_canvas, (255, 255, 255, 80), (bar_x, sy, max_bar_w, 1))

        self.screen.blit(hud_canvas, (hud_x, hud_y))

    def draw(self):
        self.draw_background(self.screen)

        if self.state in ["PLAYING", "GAMEOVER"]:
            self.draw_track(self.screen)
            for t in self.trails:
                alpha = max(0, min(255, int((t[2] / 35) * 180)))
                t_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                t_surf.fill((*COLOR_TRAIL, alpha))
                self.screen.blit(t_surf, (int(t[0])-3, int(t[1])-3))

            for p in self.particles: p.draw(self.screen)
            if self.state == "PLAYING": self.draw_car(self.screen)
            self.draw_luxury_hud()

        if self.state == "WELCOME":
            title = self.font_title.render("CYBER DRIFT ELITE", True, COLOR_BORDER)
            sub = self.font_sub.render("WASD OR ARROWS TO CONTROL // ENTER TO DRIVE", True, COLOR_TEXT)
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 60))
            self.screen.blit(sub, (self.width // 2 - sub.get_width() // 2, self.height // 2 + 40))

        elif self.state == "GAMEOVER":
            for p in self.particles: p.draw(self.screen)
            go_title = self.font_title.render(self.gameover_reason, True, COLOR_TAILLIGHT)
            go_sub = self.font_sub.render("PRESS ENTER TO REBOOT METRIC  //  ESC TO QUIT", True, COLOR_TEXT)
            self.screen.blit(go_title, (self.width // 2 - go_title.get_width() // 2, self.height // 2 - 60))
            self.screen.blit(go_sub, (self.width // 2 - go_sub.get_width() // 2, self.height // 2 + 40))

        pygame.display.flip()

    def main_loop(self):
        while True:
            self.handle_events()
            self.update_physics()
            self.draw()
            self.clock.tick(self.fps)

if __name__ == "__main__":
    CyberDriftLuxury()
