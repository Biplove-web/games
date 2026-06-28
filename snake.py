import pygame
import random
import os
import sys

pygame.init()
pygame.font.init()

HS_FILE = "highscore.txt"

class Particle:
    def __init__(self, x, y, color, cell_size):
        self.x = x + cell_size // 2
        self.y = y + cell_size // 2
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.lifetime = random.randint(15, 25)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            radius = max(1, int(self.lifetime / 4))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)

class SnakeGamePygame:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("Snake Arcade Elite Edition")
        self.clock = pygame.time.Clock()
        
        self.panel_height = 80
        self.game_width = self.width
        self.game_height = self.height - self.panel_height
        
        self.cell_size = 40
        self.cols = self.game_width // self.cell_size
        self.rows = self.game_height // self.cell_size
        
        self.game_width = self.cols * self.cell_size
        self.game_height = self.rows * self.cell_size
        self.x_offset = (self.width - self.game_width) // 2
        
        self.fps = 12
        
        self.color_bg = (6, 8, 12)
        self.color_canvas = (11, 15, 23)
        self.color_grid = (20, 27, 41)
        self.color_snake_head = (0, 242, 254)
        self.color_snake_body = (0, 178, 238)
        self.color_food = (255, 0, 119)
        self.color_super_food = (0, 255, 170)
        self.color_text = (220, 225, 235)
        self.color_gold = (255, 215, 0)
        self.color_panel = (16, 22, 34)
        self.color_neon_pink = (255, 0, 85)
        
        self.font_title = pygame.font.SysFont("Impact", int(self.cell_size * 1.5))
        self.font_ui = pygame.font.SysFont("Impact", 32)
        self.font_sub = pygame.font.SysFont("Consolas", 20, bold=True)
        
        self.high_score = self.load_high_score()
        self.particles = []
        self.screen_shake = 0
        
        self.state = "WELCOME"
        self.main_loop()

    def load_high_score(self):
        if os.path.exists(HS_FILE):
            with open(HS_FILE, "r") as f:
                try: return int(f.read().strip())
                except ValueError: return 0
        return 0

    def save_high_score(self):
        with open(HS_FILE, "w") as f:
            f.write(str(self.high_score))

    def reset_game(self):
        self.score = 0
        mid_y = (self.rows // 2) * self.cell_size
        self.snake = [
            [0, mid_y],
            [self.cell_size, mid_y],
            [self.cell_size * 2, mid_y]
        ]
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        self.is_super_food = False
        self.create_food()
        self.particles = []
        self.screen_shake = 0
        self.state = "PLAYING"

    def create_food(self):
        self.is_super_food = random.random() < 0.20
        while True:
            x = random.randint(0, self.cols - 1) * self.cell_size
            y = random.randint(0, self.rows - 1) * self.cell_size
            if [x, y] not in self.snake:
                self.food = [x, y]
                break

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.state in ["WELCOME", "GAMEOVER"]:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                elif self.state == "PLAYING":
                    if event.key == pygame.K_UP and self.direction != "DOWN":
                        self.next_direction = "UP"
                    elif event.key == pygame.K_DOWN and self.direction != "UP":
                        self.next_direction = "DOWN"
                    elif event.key == pygame.K_LEFT and self.direction != "RIGHT":
                        self.next_direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and self.direction != "LEFT":
                        self.next_direction = "RIGHT"

    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)

        if self.state != "PLAYING":
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[-1]

        if self.direction == "UP": head_y -= self.cell_size
        elif self.direction == "DOWN": head_y += self.cell_size
        elif self.direction == "LEFT": head_x -= self.cell_size
        elif self.direction == "RIGHT": head_x += self.cell_size

        if head_x < 0 or head_x >= self.game_width or head_y < 0 or head_y >= self.game_height or [head_x, head_y] in self.snake:
            self.state = "GAMEOVER"
            self.screen_shake = 25
            return

        self.snake.append([head_x, head_y])

        if head_x == self.food[0] and head_y == self.food[1]:
            color = self.color_super_food if self.is_super_food else self.color_food
            for _ in range(30):
                self.particles.append(Particle(self.food[0], self.food[1], color, self.cell_size))
                
            self.score += 3 if self.is_super_food else 1
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.create_food()
        else:
            self.snake.pop(0)

    def draw_grid(self, surface):
        for x in range(0, self.game_width + 1, self.cell_size):
            pygame.draw.line(surface, self.color_grid, (x, 0), (x, self.game_height), 1)
        for y in range(0, self.game_height + 1, self.cell_size):
            pygame.draw.line(surface, self.color_grid, (0, y), (self.game_width, y), 1)

    def draw(self):
        render_surf = pygame.Surface((self.width, self.height))
        render_surf.fill(self.color_bg)
        
        panel_y = self.height - self.panel_height
        pygame.draw.rect(render_surf, self.color_panel, (0, panel_y, self.width, self.panel_height))
        pygame.draw.line(render_surf, self.color_snake_head, (0, panel_y), (self.width, panel_y), 2)
        
        score_txt = self.font_ui.render(f"SCORE: {self.score if self.state in ['PLAYING', 'GAMEOVER'] else 0}", True, self.color_text)
        hs_txt = self.font_ui.render(f"HIGH SCORE: {self.high_score}", True, self.color_gold)
        render_surf.blit(score_txt, (self.x_offset + 40, panel_y + (self.panel_height - score_txt.get_height()) // 2))
        render_surf.blit(hs_txt, (self.width - self.x_offset - hs_txt.get_width() - 40, panel_y + (self.panel_height - hs_txt.get_height()) // 2))

        game_surf = pygame.Surface((self.game_width, self.game_height))
        game_surf.fill(self.color_canvas)
        self.draw_grid(game_surf)

        if self.state in ["PLAYING", "GAMEOVER"]:
            food_color = self.color_super_food if self.is_super_food else self.color_food
            food_center = (self.food[0] + self.cell_size // 2, self.food[1] + self.cell_size // 2)
            
            glow_radius = int(self.cell_size * 0.75)
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*food_color, 45), (glow_radius, glow_radius), glow_radius)
            game_surf.blit(glow_surf, (food_center[0] - glow_radius, food_center[1] - glow_radius))
            
            pygame.draw.circle(game_surf, food_color, food_center, (self.cell_size // 2) - 4)
            pygame.draw.circle(game_surf, (255, 255, 255), food_center, (self.cell_size // 4) - 2)

            for i, (x, y) in enumerate(self.snake):
                is_head = (i == len(self.snake) - 1)
                color = self.color_snake_head if is_head else self.color_snake_body
                
                rect = pygame.Rect(x + 2, y + 2, self.cell_size - 4, self.cell_size - 4)
                pygame.draw.rect(game_surf, color, rect, border_radius=8)
                
                if not is_head:
                    inner_rect = pygame.Rect(x + 6, y + 6, self.cell_size - 12, self.cell_size - 12)
                    pygame.draw.rect(game_surf, (20, 30, 48), inner_rect, border_radius=4)
                else:
                    eye_radius = 4
                    if self.direction in ["RIGHT", "LEFT"]:
                        pygame.draw.circle(game_surf, (255, 255, 255), (x + self.cell_size//2, y + self.cell_size//4 + 2), eye_radius)
                        pygame.draw.circle(game_surf, (255, 255, 255), (x + self.cell_size//2, y + 3*self.cell_size//4 - 2), eye_radius)
                    else:
                        pygame.draw.circle(game_surf, (255, 255, 255), (x + self.cell_size//4 + 2, y + self.cell_size//2), eye_radius)
                        pygame.draw.circle(game_surf, (255, 255, 255), (x + 3*self.cell_size//4 - 2, y + self.cell_size//2), eye_radius)

            for p in self.particles:
                p.draw(game_surf)

        if self.state == "WELCOME":
            title = self.font_title.render("SNAKE ARCADE ELITE", True, self.color_snake_head)
            sub = self.font_sub.render("PRESS ENTER TO ENTER THE MATRIX", True, self.color_text)
            esc_txt = self.font_sub.render("PRESS ESC TO EXIT", True, (110, 120, 135))
            game_surf.blit(title, (self.game_width // 2 - title.get_width() // 2, self.game_height // 2 - 60))
            game_surf.blit(sub, (self.game_width // 2 - sub.get_width() // 2, self.game_height // 2 + 20))
            game_surf.blit(esc_txt, (self.game_width // 2 - esc_txt.get_width() // 2, self.game_height // 2 + 60))

        elif self.state == "GAMEOVER":
            for p in self.particles:
                p.draw(game_surf)
            go_title = self.font_title.render("GAME OVER", True, self.color_neon_pink)
            go_sub = self.font_sub.render("PRESS ENTER TO TRY AGAIN", True, self.color_text)
            esc_txt = self.font_sub.render("PRESS ESC TO EXIT", True, (110, 120, 135))
            game_surf.blit(go_title, (self.game_width // 2 - go_title.get_width() // 2, self.game_height // 2 - 60))
            game_surf.blit(go_sub, (self.game_width // 2 - go_sub.get_width() // 2, self.game_height // 2 + 20))
            game_surf.blit(esc_txt, (self.game_width // 2 - esc_txt.get_width() // 2, self.game_height // 2 + 60))

        pygame.draw.rect(game_surf, self.color_snake_head, (0, 0, self.game_width, self.game_height), 2)
        render_surf.blit(game_surf, (self.x_offset, 0))

        offset_x = 0
        offset_y = 0
        if self.screen_shake > 0:
            offset_x = random.randint(-self.screen_shake, self.screen_shake)
            offset_y = random.randint(-self.screen_shake, self.screen_shake)
            self.screen_shake -= 2

        self.screen.blit(render_surf, (offset_x, offset_y))
        pygame.display.flip()

    def main_loop(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)

if __name__ == "__main__":
    SnakeGamePygame()