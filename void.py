import pygame
import random
import sys
import math

pygame.init()
pygame.font.init()

COLOR_BG = (12, 10, 15)           
COLOR_GRID = (30, 24, 35)         
COLOR_SUN = (255, 110, 0)         
COLOR_SUN_CORE = (255, 200, 50)    
COLOR_SHIP = (240, 238, 230)       
COLOR_PANEL_BG = (20, 16, 24, 200) 
COLOR_TEXT_AMBER = (255, 160, 0)   
COLOR_TEXT_DIM = (160, 100, 0)     
COLOR_BOOST = (0, 200, 255)        

class SolarFlare:
    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y
        self.angle = random.uniform(0, math.pi * 2)
        self.length = random.uniform(80, 140)
        self.speed = random.uniform(0.02, 0.05)
        self.width = random.randint(2, 5)
        
    def update(self):
        self.angle += self.speed

    def draw(self, surface):
        start_x = self.center_x + 60 * math.cos(self.angle)
        start_y = self.center_y + 60 * math.sin(self.angle)
        end_x = self.center_x + self.length * math.cos(self.angle)
        end_y = self.center_y + self.length * math.sin(self.angle)
        pygame.draw.line(surface, COLOR_SUN, (start_x, start_y), (end_x, end_y), self.width)

class VoidRunnerClassic:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("Void Runner: Event Horizon")
        self.clock = pygame.time.Clock()
        
        self.font_title = pygame.font.SysFont("Courier", int(self.width * 0.04), bold=True)
        self.font_ui = pygame.font.SysFont("Courier", 15, bold=True)
        self.font_digits = pygame.font.SysFont("Courier", 24, bold=True)
        
        self.fps = 60
        self.state = "WELCOME"
        
        self.sun_x = self.width // 2
        self.sun_y = self.height // 2
        
        self.ship_angle = 0.0
        self.orbit_radius = 300.0
        self.base_speed = 0.03
        self.fuel = 100.0
        self.max_fuel = 100.0
        self.is_boosting = False
        
        self.score_float = 0.0
        self.score = 0
        
        self.flares = [SolarFlare(self.sun_x, self.sun_y) for _ in range(12)]
        
        self.main_loop()

    def reset_game(self):
        self.ship_angle = 0.0
        self.orbit_radius = 320.0
        self.fuel = self.max_fuel
        self.score_float = 0.0
        self.score = 0
        self.is_boosting = False
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
        gravity_pull = 1.2
        
        if keys[pygame.K_SPACE] and self.fuel > 5:
            self.is_boosting = True
            self.orbit_radius += 3.5  
            self.fuel = max(0.0, self.fuel - 0.8)
        else:
            self.is_boosting = False
            self.orbit_radius -= gravity_pull  
            self.fuel = min(self.max_fuel, self.fuel + 0.15)

        current_speed = self.base_speed * (1.0 + (self.score_float / 5000.0))
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.ship_angle -= current_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.ship_angle += current_speed

        self.ship_angle += current_speed * 0.5

        for flare in self.flares:
            flare.update()

        if self.orbit_radius > 70 and self.orbit_radius < 550:
            self.score_float += 0.25
            self.score = int(self.score_float)

        self.check_boundaries()

    def check_boundaries(self):
        if self.orbit_radius < 65 or self.orbit_radius > 560:
            self.state = "GAMEOVER"

        for flare in self.flares:
            angle_diff = abs(self.ship_angle % (math.pi * 2) - flare.angle % (math.pi * 2))
            if angle_diff < 0.08:
                if self.orbit_radius < flare.length:
                    self.state = "GAMEOVER"

    def draw_classic_hud(self):
        hud_w, hud_h = 480, 160
        hud_canvas = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
        
        pygame.draw.rect(hud_canvas, COLOR_PANEL_BG, (0, 0, hud_w, hud_h))
        pygame.draw.rect(hud_canvas, COLOR_TEXT_AMBER, (0, 0, hud_w, hud_h), 2)
        
        lbl_score = self.font_ui.render("HARVEST MATRIX", True, COLOR_TEXT_DIM)
        val_score = self.font_digits.render(f"{self.score:06} UNT", True, COLOR_TEXT_AMBER)
        lbl_fuel = self.font_ui.render("ION PRESSURE FLUID CORE", True, COLOR_TEXT_DIM)
        
        txt_radius = self.font_ui.render(f"PROX: {int(self.orbit_radius)}M", True, COLOR_TEXT_AMBER)
        status_txt = "SAFE HORIZON" if self.orbit_radius > 140 else "GRAV CRIT"
        txt_status = self.font_ui.render(status_txt, True, COLOR_TEXT_AMBER if status_txt == "SAFE HORIZON" else COLOR_SUN)
        
        col1_x = 24
        col2_x = hud_w - 180  
        
        hud_canvas.blit(lbl_score, (col1_x, 18))
        hud_canvas.blit(val_score, (col1_x, 38))
        
        hud_canvas.blit(txt_radius, (col2_x, 18))
        hud_canvas.blit(txt_status, (col2_x, 38))
        
        hud_canvas.blit(lbl_fuel, (col1_x, 88))
        
        bar_x, bar_y, bar_w, bar_h = 24, 115, hud_w - 48, 16
        pygame.draw.rect(hud_canvas, COLOR_TEXT_DIM, (bar_x, bar_y, bar_w, bar_h), 1)
        
        fill_w = int((self.fuel / self.max_fuel) * (bar_w - 6))
        if fill_w > 0:
            pygame.draw.rect(hud_canvas, COLOR_TEXT_AMBER, (bar_x + 3, bar_y + 3, fill_w, bar_h - 6))

        self.screen.blit(hud_canvas, (50, 50))

    def draw_universe(self):
        pygame.draw.circle(self.screen, (22, 18, 28), (self.sun_x, self.sun_y), 560, 2) 
        pygame.draw.circle(self.screen, (35, 20, 15), (self.sun_x, self.sun_y), 140, 1) 
        pygame.draw.circle(self.screen, COLOR_SUN, (self.sun_x, self.sun_y), 65, 2)    
        
        for flare in self.flares:
            flare.draw(self.screen)
            
        pygame.draw.circle(self.screen, COLOR_SUN, (self.sun_x, self.sun_y), 55)
        pygame.draw.circle(self.screen, COLOR_SUN_CORE, (self.sun_x, self.sun_y), 40)

        ship_x = self.sun_x + self.orbit_radius * math.cos(self.ship_angle)
        ship_y = self.sun_y + self.orbit_radius * math.sin(self.ship_angle)
        
        front_pt = (ship_x + 16 * math.cos(self.ship_angle), ship_y + 16 * math.sin(self.ship_angle))
        left_pt = (ship_x + 10 * math.cos(self.ship_angle + 2.4), ship_y + 10 * math.sin(self.ship_angle + 2.4))
        right_pt = (ship_x + 10 * math.cos(self.ship_angle - 2.4), ship_y + 10 * math.sin(self.ship_angle - 2.4))
        
        if self.is_boosting:
            exhaust_pt = (ship_x - 18 * math.cos(self.ship_angle), ship_y - 18 * math.sin(self.ship_angle))
            pygame.draw.polygon(self.screen, COLOR_BOOST, [left_pt, exhaust_pt, right_pt])

        pygame.draw.polygon(self.screen, COLOR_SHIP, [front_pt, left_pt, right_pt])
        pygame.draw.polygon(self.screen, COLOR_TEXT_AMBER, [front_pt, left_pt, right_pt], 1)

    def draw(self):
        self.screen.fill(COLOR_BG)
        
        spacing = 100
        for x in range(0, self.width, spacing):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, spacing):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (self.width, y), 1)

        if self.state in ["PLAYING", "GAMEOVER"]:
            self.draw_universe()
            self.draw_classic_hud()

        if self.state == "WELCOME":
            title = self.font_title.render("VOID RUNNER // EVENT HORIZON", True, COLOR_TEXT_AMBER)
            sub = self.font_ui.render("A/D OR ARROWS ORBIT  //  HOLD SPACE TO ION BOOST  //  ENTER TO RUN", True, COLOR_SHIP)
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 40))
            self.screen.blit(sub, (self.width // 2 - sub.get_width() // 2, self.height // 2 + 40))

        elif self.state == "GAMEOVER":
            go_title = self.font_title.render("HULL COLLAPSE: GRAVITY BREACHED", True, COLOR_SUN)
            go_sub = self.font_ui.render("ENTER TO REBOOT MAIN ENGINE SYSTEMS  //  ESC TO ABORT", True, COLOR_SHIP)
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
    VoidRunnerClassic()
