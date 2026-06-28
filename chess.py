import pygame
import sys
import random
import math
import copy

pygame.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
BOARD_SIZE = min(WIDTH, HEIGHT)
SQUARE_SIZE = BOARD_SIZE // 8
SIDEBAR_WIDTH = WIDTH - BOARD_SIZE

COLOR_LUXE_DARK = (14, 20, 32)        
COLOR_LUXE_DARK_GRAD = (28, 38, 58)   
COLOR_LUXE_GOLD = (200, 150, 24)      
COLOR_LUXE_GOLD_GRAD = (245, 210, 95)  
COLOR_ACCENT = (255, 223, 128)        
COLOR_HIGHLIGHT = (46, 125, 96)       
COLOR_ALERT = (166, 25, 46)           
COLOR_SIDEBAR_START = (7, 10, 18)     
COLOR_SIDEBAR_END = (18, 25, 38)      
COLOR_TEXT_LIGHT = (248, 249, 250)    
COLOR_TEXT_MUTED = (165, 142, 92)     
COLOR_OVERLAY = (10, 14, 22, 230)     

COLOR_NOTATION_BG = (245, 245, 242)   
COLOR_NOTATION_GOLD = (150, 105, 5)   
COLOR_NOTATION_BLACK = (20, 26, 40)   
COLOR_NOTATION_INDEX = (120, 125, 135) 

GOLD_BODY_TOP = (255, 225, 120)
GOLD_BODY_BOT = (175, 120, 10)
BLACK_BODY_TOP = (58, 64, 78)
BLACK_BODY_BOT = (18, 20, 26)

PIECE_GOLD_SHADOW = (140, 95, 10)
PIECE_BLACK_SHADOW = (10, 12, 16)

PIECE_VALUES = {'p': 10, 'n': 30, 'b': 30, 'r': 50, 'q': 90, 'k': 9000}

FONT_MAIN = pygame.font.SysFont("georgia", int(BOARD_SIZE * 0.045), bold=True)
FONT_SUB = pygame.font.SysFont("georgia", int(BOARD_SIZE * 0.022), bold=True)
FONT_SMALL = pygame.font.SysFont("georgia", int(BOARD_SIZE * 0.017))
FONT_NOTATION = pygame.font.SysFont("cambria", int(BOARD_SIZE * 0.019), bold=True)

class UltraLuxeChess:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Imperial Chess: Sovereign Edition XI")
        self.game_mode = "MENU"
        
        self.board_surface = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
        
        self.current_angle = 0.0
        self.start_angle = 0.0
        self.target_angle = 0.0
        self.rot_progress = 1.0
        
        self.spectator_history = []  
        self.spectator_index = -1    
        
        self.reset_game_state()

    def reset_game_state(self):
        self.turn = "W"
        self.selected_square = None
        self.valid_moves = []
        self.game_over = False
        self.status_message = "Imperial Gold Match Initialized"
        self.current_angle = 0.0
        self.start_angle = 0.0
        self.target_angle = 0.0
        self.rot_progress = 1.0
        
        self.has_moved = {
            "K_white": False, "R_white_left": False, "R_white_right": False,
            "K_black": False, "R_black_left": False, "R_black_right": False
        }
        
        self.captured_by_white = []
        self.captured_by_black = []
        self.move_history = []  
        
        self.animating_piece = None
        self.anim_start = None
        self.anim_end = None
        self.anim_progress = 1.0
        
        self.promotion_active = False
        self.promotion_square = None  
        self.promotion_options = []   
        
        self.save_active = False
        self.load_active = False
        self.save_filename = "royal_match"
        self.load_filename = "royal_match"
        self.cursor_blink_time = 0
        
        self.board = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]

    def convert_to_notation(self, piece, start, end, captured):
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
        
        p_name = piece.upper()
        
        if p_name == "P":
            p_str = files[start[1]] if captured != "-" else ""
        else:
            p_str = p_name
        
        if p_name == "K" and abs(start[1] - end[1]) == 2:
            return "O-O" if end[1] == 6 else "O-O-O"
            
        action = "x" if captured != "-" else ""
        dest = f"{files[end[1]]}{ranks[end[0]]}"
        return f"{p_str}{action}{dest}"

    def execute_save_to_file(self):
        pgn_out = []
        for i in range(0, len(self.move_history), 2):
            move_num = (i // 2) + 1
            white_move = self.move_history[i]
            black_move = self.move_history[i+1] if i+1 < len(self.move_history) else ""
            pgn_out.append(f"{move_num}. {white_move} {black_move}".strip())
        
        full_pgn_string = " ".join(pgn_out)
        clean_filename = "".join([c for c in self.save_filename if c.isalnum() or c in ('_', '-')]).strip()
        if not clean_filename:
            clean_filename = "imperial_match"
            
        final_path = f"{clean_filename}.chess"
        try:
            with open(final_path, "w") as f:
                f.write("[Event \"Imperial Sovereign Match\"]\n")
                f.write(f"[Result \"{self.status_message}\"]\n\n")
                f.write(full_pgn_string)
            self.status_message = f"Archived as {final_path}!"
        except Exception as e:
            self.status_message = "File Write Permission Error."
        self.save_active = False

    def execute_load_from_file(self):
        clean_filename = "".join([c for c in self.load_filename if c.isalnum() or c in ('_', '-')]).strip()
        final_path = f"{clean_filename}.chess"
        
        try:
            with open(final_path, "r") as f:
                lines = f.readlines()
        except Exception:
            self.status_message = "File Not Found / Access Error."
            self.load_active = False
            return

        moves_text = ""
        for line in lines:
            if not line.startswith("[") and line.strip():
                moves_text += " " + line.strip()

        tokens = moves_text.split()
        move_tokens = []
        for token in tokens:
            if "." in token:
                parts = token.split(".")
                if parts[-1].strip(): 
                    move_tokens.append(parts[-1].strip())
            else:
                move_tokens.append(token.strip())

        sim_instance = UltraLuxeChess()
        sim_instance.game_mode = "HUMAN"
        
        self.spectator_history = []
        
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['8', '7', '6', '5', '4', '3', '2', '1']

        for move_str in move_tokens:
            if not move_str: continue
            start_sq = None
            end_sq = None
            promo_piece = None

            if move_str in ("O-O", "O-O-O"):
                rank = 7 if sim_instance.turn == "W" else 0
                start_sq = (rank, 4)
                end_sq = (rank, 6) if move_str == "O-O" else (rank, 2)
            else:
                clean_move = move_str.replace("x", "").replace("+", "").replace("#", "")
                if "=" in clean_move:
                    clean_move, promo_piece = clean_move.split("=")
                    if sim_instance.turn == "B": promo_piece = promo_piece.lower()
                    else: promo_piece = promo_piece.upper()

                if len(clean_move) < 2: continue
                dest_str = clean_move[-2:]
                try:
                    end_sq = (ranks.index(dest_str[1]), files.index(dest_str[0]))
                except ValueError:
                    continue
                    
                prefix = clean_move[:-2]
                
                if not prefix:
                    target_char = "P"
                elif len(prefix) == 1 and prefix[0].islower():
                    target_char = "P"
                else:
                    target_char = prefix[0].upper()

                for r in range(8):
                    for c in range(8):
                        piece = sim_instance.board[r][c]
                        if piece != "-" and ((sim_instance.turn == "W" and piece.isupper()) or (sim_instance.turn == "B" and piece.islower())):
                            if piece.upper() == target_char and end_sq in sim_instance.get_legal_moves(r, c, sim_instance.board):
                                if target_char == "P" and len(prefix) == 1:
                                    if c != files.index(prefix[0]):
                                        continue
                                start_sq = (r, c)
                                break
                    if start_sq: break

            if start_sq and end_sq:
                sr, sc = start_sq
                er, ec = end_sq
                p = sim_instance.board[sr][sc]
                captured = sim_instance.board[er][ec]

                if captured != "-":
                    if sim_instance.turn == "W": sim_instance.captured_by_white.append(captured)
                    else: sim_instance.captured_by_black.append(captured)

                if p.upper() == "K" and abs(sc - ec) == 2:
                    curr_rank = 7 if p.isupper() else 0
                    if ec == 6:
                        sim_instance.board[curr_rank][5] = sim_instance.board[curr_rank][7]
                        sim_instance.board[curr_rank][7] = "-"
                    elif ec == 2:
                        sim_instance.board[curr_rank][3] = sim_instance.board[curr_rank][0]
                        sim_instance.board[curr_rank][0] = "-"

                sim_instance.board[er][ec] = p
                sim_instance.board[sr][sc] = "-"

                if promo_piece:
                    sim_instance.board[er][ec] = promo_piece
                    sim_instance.move_history.append(move_str if "=" in move_str else f"{move_str}={promo_piece.upper()}")
                else:
                    sim_instance.move_history.append(move_str)

                if sr == 7 and sc == 4: sim_instance.has_moved["K_white"] = True
                if sr == 0 and sc == 4: sim_instance.has_moved["K_black"] = True
                if sr == 7 and sc == 0: sim_instance.has_moved["R_white_left"] = True
                if sr == 7 and sc == 7: sim_instance.has_moved["R_white_right"] = True
                if sr == 0 and sc == 0: sim_instance.has_moved["R_black_left"] = True
                if sr == 0 and sc == 7: sim_instance.has_moved["R_black_right"] = True

                sim_instance.turn = "B" if sim_instance.turn == "W" else "W"
                sim_instance.evaluate_endgame_state()
                
                self.spectator_history.append({
                    "board": copy.deepcopy(sim_instance.board),
                    "turn": sim_instance.turn,
                    "captured_w": list(sim_instance.captured_by_white),
                    "captured_b": list(sim_instance.captured_by_black),
                    "move_history": list(sim_instance.move_history),
                    "status": str(sim_instance.status_message)
                })
            else:
                self.status_message = "Malformed log tracking sequence."
                self.load_active = False
                return

        if self.game_mode == "WATCH":
            self.reset_game_state()
            self.spectator_index = -1
            self.status_message = "Loaded! Use [LEFT/RIGHT ARROWS] to spectate."
        else:
            if self.spectator_history:
                final_state = self.spectator_history[-1]
                self.board = final_state["board"]
                self.turn = final_state["turn"]
                self.captured_by_white = final_state["captured_w"]
                self.captured_by_black = final_state["captured_b"]
                self.move_history = final_state["move_history"]
                self.status_message = "Sovereign Match Log Restored!"
            self.target_angle = 180.0 if self.turn == "B" and self.game_mode == "HUMAN" else 0.0
            self.current_angle = self.target_angle

        self.load_active = False

    def navigate_spectator_timeline(self, direction):
        if not self.spectator_history: return
        
        new_index = self.spectator_index + direction
        if -1 <= new_index < len(self.spectator_history):
            self.spectator_index = new_index
            
            if self.spectator_index == -1:
                self.reset_game_state()
                self.status_message = "Match Start. Press [RIGHT ARROW] to play moves."
            else:
                state = self.spectator_history[self.spectator_index]
                self.board = copy.deepcopy(state["board"])
                self.turn = state["turn"]
                self.captured_by_white = list(state["captured_w"])
                self.captured_by_black = list(state["captured_b"])
                self.move_history = list(state["move_history"])
                self.status_message = f"Reviewing move {self.spectator_index + 1}/{len(self.spectator_history)}"
                if "Wins" in state["status"] or "Stalemate" in state["status"]:
                    self.status_message = state["status"]

    def draw_luxe_sidebar_background(self):
        for y in range(HEIGHT):
            factor = y / HEIGHT
            r = int(COLOR_SIDEBAR_START[0] * (1 - factor) + COLOR_SIDEBAR_END[0] * factor)
            g = int(COLOR_SIDEBAR_START[1] * (1 - factor) + COLOR_SIDEBAR_END[1] * factor)
            b = int(COLOR_SIDEBAR_START[2] * (1 - factor) + COLOR_SIDEBAR_END[2] * factor)
            pygame.draw.line(self.screen, (r, g, b), (BOARD_SIZE, y), (WIDTH, y))

    def draw_gradient_polygon(self, surface, points, top_color, bot_color):
        if not points: return
        ys = [p[1] for p in points]
        min_y, max_y = min(ys), max(ys)
        h = max(1.0, max_y - min_y)
        
        poly_surf = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
        pygame.draw.polygon(poly_surf, (255, 255, 255, 255), points)
        
        for y_pos in range(int(min_y), int(max_y) + 1):
            factor = (y_pos - min_y) / h
            r = max(0, min(255, int(top_color[0] * (1 - factor) + bot_color[0] * factor)))
            g = max(0, min(255, int(top_color[1] * (1 - factor) + bot_color[1] * factor)))
            b = max(0, min(255, int(top_color[2] * (1 - factor) + bot_color[2] * factor)))
            
            line_surf = pygame.Surface((BOARD_SIZE, 1), pygame.SRCALPHA)
            line_surf.fill((r, g, b, 255))
            poly_surf.blit(line_surf, (0, y_pos), special_flags=pygame.BLEND_RGBA_MIN)
            
        surface.blit(poly_surf, (0, 0))

    def draw_premium_piece(self, surface, p_type, is_gold, x, y, size_scale=1.0):
        top_c = GOLD_BODY_TOP if is_gold else BLACK_BODY_TOP
        bot_c = GOLD_BODY_BOT if is_gold else BLACK_BODY_BOT
        shadow_c = PIECE_GOLD_SHADOW if is_gold else PIECE_BLACK_SHADOW
        trim_c = COLOR_ACCENT if is_gold else (90, 102, 120)
        glare_c = (255, 255, 220) if is_gold else (150, 165, 190)
        
        local_size = int(SQUARE_SIZE * size_scale)
        f = local_size / 100.0
        
        p_surf = pygame.Surface((local_size, local_size), pygame.SRCALPHA)
        mid_x = local_size // 2
        base_y = local_size - int(local_size * 0.12)

        pygame.draw.ellipse(p_surf, (0, 0, 0, 110), (mid_x - int(40*f), local_size - int(20*f), int(80*f), int(15*f)))
        pygame.draw.ellipse(p_surf, shadow_c, (mid_x - 42*f, base_y - 1*f, 84*f, 16*f))
        pygame.draw.ellipse(p_surf, bot_c, (mid_x - 40*f, base_y - 5*f, 80*f, 16*f))
        pygame.draw.ellipse(p_surf, trim_c, (mid_x - 36*f, base_y - 4*f, 72*f, 10*f), max(1, int(2*f)))
        
        t = p_type.upper()
        
        if t == "P":  
            self.draw_gradient_polygon(p_surf, [(mid_x-16*f, base_y-10*f), (mid_x-8*f, 42*f), (mid_x+8*f, 42*f), (mid_x+16*f, base_y-10*f)], top_c, bot_c)
            pygame.draw.circle(p_surf, top_c, (int(mid_x), int(32*f)), int(18*f))
            pygame.draw.circle(p_surf, shadow_c, (int(mid_x), int(32*f)), int(18*f), max(1, int(2*f)))
            pygame.draw.circle(p_surf, glare_c, (int(mid_x - 6*f), int(26*f)), int(4*f))
        elif t == "R":  
            self.draw_gradient_polygon(p_surf, [(mid_x-24*f, base_y-12*f), (mid_x-20*f, 32*f), (mid_x+20*f, 32*f), (mid_x+24*f, base_y-12*f)], top_c, bot_c)
            pygame.draw.rect(p_surf, top_c, (mid_x-24*f, 16*f, 48*f, 16*f), border_radius=int(2*f))
            pygame.draw.rect(p_surf, shadow_c, (mid_x-24*f, 16*f, 48*f, 16*f), max(1, int(2*f)), border_radius=int(2*f))
            pygame.draw.rect(p_surf, (0,0,0,0), (mid_x-14*f, 16*f, 7*f, 7*f))
            pygame.draw.rect(p_surf, (0,0,0,0), (mid_x+7*f, 16*f, 7*f, 7*f))
        elif t == "B":  
            self.draw_gradient_polygon(p_surf, [(mid_x-20*f, base_y-12*f), (mid_x-18*f, 32*f), (mid_x+18*f, 32*f), (mid_x+20*f, base_y-12*f)], top_c, bot_c)
            pygame.draw.ellipse(p_surf, top_c, (mid_x-18*f, 16*f, 36*f, 32*f))
            pygame.draw.ellipse(p_surf, shadow_c, (mid_x-18*f, 16*f, 36*f, 32*f), max(1, int(2*f)))
            pygame.draw.circle(p_surf, COLOR_ACCENT, (int(mid_x), int(12*f)), int(5*f))
            pygame.draw.line(p_surf, shadow_c, (mid_x-10*f, 24*f), (mid_x+6*f, 36*f), max(1, int(3*f)))
        elif t == "N":  
            self.draw_gradient_polygon(p_surf, [(mid_x-22*f, base_y-12*f), (mid_x-28*f, 32*f), (mid_x-5*f, 18*f), (mid_x+18*f, base_y-12*f)], top_c, bot_c)
            pygame.draw.ellipse(p_surf, top_c, (mid_x-32*f, 14*f, 34*f, 24*f))
            pygame.draw.circle(p_surf, top_c, (int(mid_x-6*f), int(22*f)), int(15*f))
            pygame.draw.polygon(p_surf, trim_c, [(mid_x-4*f, 10*f), (mid_x+2*f, 2*f), (mid_x+6*f, 10*f)])
            pygame.draw.circle(p_surf, COLOR_ALERT if is_gold else COLOR_LUXE_GOLD, (int(mid_x-16*f), int(20*f)), int(3*f))
        elif t == "Q":  
            self.draw_gradient_polygon(p_surf, [(mid_x-25*f, base_y-12*f), (mid_x-16*f, 28*f), (mid_x+16*f, 28*f), (mid_x+25*f, base_y-12*f)], top_c, bot_c)
            self.draw_gradient_polygon(p_surf, [(mid_x-26*f, 28*f), (mid_x-34*f, 10*f), (mid_x-16*f, 22*f), (mid_x, 6*f), (mid_x+16*f, 22*f), (mid_x+34*f, 10*f), (mid_x+26*f, 28*f)], top_c, bot_c)
            pygame.draw.circle(p_surf, trim_c, (int(mid_x), int(6*f)), int(4*f))
            pygame.draw.circle(p_surf, trim_c, (int(mid_x-34*f), int(10*f)), int(4*f))
            pygame.draw.circle(p_surf, trim_c, (int(mid_x+34*f), int(10*f)), int(4*f))
        elif t == "K":  
            self.draw_gradient_polygon(p_surf, [(mid_x-26*f, base_y-12*f), (mid_x-16*f, 24*f), (mid_x+16*f, 24*f), (mid_x+26*f, base_y-12*f)], top_c, bot_c)
            pygame.draw.rect(p_surf, top_c, (mid_x-20*f, 16*f, 40*f, 14*f), border_radius=int(2*f))
            pygame.draw.rect(p_surf, shadow_c, (mid_x-20*f, 16*f, 40*f, 14*f), max(1, int(2*f)), border_radius=int(2*f))
            pygame.draw.line(p_surf, trim_c, (mid_x, 2*f), (mid_x, 16*f), max(1, int(3*f)))
            pygame.draw.line(p_surf, trim_c, (mid_x-8*f, 7*f), (mid_x+8*f, 7*f), max(1, int(3*f)))

        surface.blit(p_surf, (x, y))

    def draw_menu(self):
        self.screen.fill(COLOR_SIDEBAR_START)
        mouse_pos = pygame.mouse.get_pos()
        
        title_text = FONT_MAIN.render("IMPERIAL GOLD CHESS", True, COLOR_LUXE_GOLD)
        self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT * 0.20))
        sub_text = FONT_SUB.render("Sovereign Chromatic Edition v12.0", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT * 0.27))
        
        btn_w, btn_h = int(BOARD_SIZE * 0.45), int(BOARD_SIZE * 0.07)
        self.btn_human = pygame.Rect(WIDTH // 2 - btn_w // 2, int(HEIGHT * 0.42), btn_w, btn_h)
        self.btn_bot = pygame.Rect(WIDTH // 2 - btn_w // 2, int(HEIGHT * 0.52), btn_w, btn_h)
        self.btn_watch = pygame.Rect(WIDTH // 2 - btn_w // 2, int(HEIGHT * 0.62), btn_w, btn_h)
        
        menu_items = [
            (self.btn_human, "Sovereign PvP Match"), 
            (self.btn_bot, "Grandmaster AI Core"),
            (self.btn_watch, "Spectator Core (Review Log)")
        ]
        
        for btn, label in menu_items:
            if btn.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, COLOR_LUXE_GOLD, btn, border_radius=12)
                lbl_surface = FONT_SUB.render(label, True, COLOR_SIDEBAR_START)
            else:
                pygame.draw.rect(self.screen, COLOR_LUXE_DARK, btn, border_radius=12)
                pygame.draw.rect(self.screen, COLOR_LUXE_GOLD, btn, 2, border_radius=12)
                lbl_surface = FONT_SUB.render(label, True, COLOR_TEXT_LIGHT)
            self.screen.blit(lbl_surface, (btn.x + (btn_w - lbl_surface.get_width()) // 2, btn.y + (btn_h - lbl_surface.get_height()) // 2))

    def draw_luxury_square(self, surf, row, col, is_check, is_selected, rendered_angle):
        is_gold_sq = (row + col) % 2 == 0
        if rendered_angle > 90.0:
            bx, by = (7 - col) * SQUARE_SIZE, (7 - row) * SQUARE_SIZE
        else:
            bx, by = col * SQUARE_SIZE, row * SQUARE_SIZE
        
        c1 = COLOR_LUXE_GOLD if is_gold_sq else COLOR_LUXE_DARK
        c2 = COLOR_LUXE_GOLD_GRAD if is_gold_sq else COLOR_LUXE_DARK_GRAD
        
        for i in range(SQUARE_SIZE):
            fact = i / SQUARE_SIZE
            r = max(0, min(255, int(c1[0] * (1 - fact) + c2[0] * fact)))
            g = max(0, min(255, int(c1[1] * (1 - fact) + c2[1] * fact)))
            b = max(0, min(255, int(c1[2] * (1 - fact) + c2[2] * fact)))
            pygame.draw.line(surf, (r, g, b), (bx, by + i), (bx + SQUARE_SIZE - 1, by + i))

        pad = int(SQUARE_SIZE * 0.22)
        pat_color = (255, 240, 190, 32) if is_gold_sq else (46, 58, 82, 75)
        pat_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        pygame.draw.polygon(pat_surf, pat_color, [(SQUARE_SIZE//2, pad), (SQUARE_SIZE - pad, SQUARE_SIZE//2), (SQUARE_SIZE//2, SQUARE_SIZE - pad), (pad, SQUARE_SIZE//2)], 1)
        pygame.draw.polygon(pat_surf, pat_color, [(SQUARE_SIZE//2, pad + 6), (SQUARE_SIZE - pad - 6, SQUARE_SIZE//2), (SQUARE_SIZE//2, SQUARE_SIZE - pad - 6), (pad + 6, SQUARE_SIZE//2)], 1)
        surf.blit(pat_surf, (bx, by))

        bevel_color = (255, 235, 170, 50) if is_gold_sq else (44, 54, 76, 130)
        pygame.draw.rect(surf, bevel_color, (bx, by, SQUARE_SIZE, SQUARE_SIZE), 1)
        
        if is_check:
            pygame.draw.rect(surf, COLOR_ALERT, (bx, by, SQUARE_SIZE, SQUARE_SIZE), int(5 * (SQUARE_SIZE / 100)))
        elif is_selected:
            pygame.draw.rect(surf, COLOR_ACCENT, (bx, by, SQUARE_SIZE, SQUARE_SIZE), int(4 * (SQUARE_SIZE / 100)))

    def draw_board(self):
        if self.rot_progress < 1.0:
            self.rot_progress += 0.045
            if self.rot_progress >= 1.0:
                self.rot_progress = 1.0
                self.current_angle = self.target_angle
            else:
                factor = math.sin(self.rot_progress * math.pi / 2)
                self.current_angle = self.start_angle + (self.target_angle - self.start_angle) * factor

        self.board_surface.fill(COLOR_LUXE_DARK)
        king_in_check_pos = self.get_king_square(self.turn) if self.is_in_check(self.turn, self.board) else None

        for row in range(8):
            for col in range(8):
                is_check = (king_in_check_pos == (row, col))
                is_selected = (self.selected_square == (row, col))
                self.draw_luxury_square(self.board_surface, row, col, is_check, is_selected, self.current_angle)

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != "-" and not (self.anim_progress < 1.0 and (row, col) == self.anim_end):
                    if self.current_angle > 90.0:
                        bx, by = (7 - col) * SQUARE_SIZE, (7 - row) * SQUARE_SIZE
                    else:
                        bx, by = col * SQUARE_SIZE, row * SQUARE_SIZE
                    self.draw_premium_piece(self.board_surface, piece, piece.isupper(), bx, by)

        if self.anim_progress < 1.0:
            self.anim_progress += 0.12
            if self.anim_progress >= 1.0:
                self.anim_progress = 1.0
                self.check_post_move_conditions()
            else:
                st_row, st_col = self.anim_start
                ed_row, ed_col = self.anim_end
                if self.current_angle > 90.0:
                    st_x, st_y = (7 - st_col) * SQUARE_SIZE, (7 - st_row) * SQUARE_SIZE
                    ed_x, ed_y = (7 - ed_col) * SQUARE_SIZE, (7 - ed_row) * SQUARE_SIZE
                else:
                    st_x, st_y = st_col * SQUARE_SIZE, st_row * SQUARE_SIZE
                    ed_x, ed_y = ed_col * SQUARE_SIZE, ed_row * SQUARE_SIZE
                    
                curr_x = st_x + (ed_x - st_x) * math.sin(self.anim_progress * math.pi / 2)
                curr_y = st_y + (ed_y - st_y) * math.sin(self.anim_progress * math.pi / 2)
                self.draw_premium_piece(self.board_surface, self.animating_piece, self.animating_piece.isupper(), curr_x, curr_y)

        for row, col in self.valid_moves:
            if self.current_angle > 90.0:
                bx, by = (7 - col) * SQUARE_SIZE, (7 - row) * SQUARE_SIZE
            else:
                bx, by = col * SQUARE_SIZE, row * SQUARE_SIZE
            center = (bx + SQUARE_SIZE // 2, by + SQUARE_SIZE // 2)
            pygame.draw.circle(self.board_surface, COLOR_HIGHLIGHT, center, int(SQUARE_SIZE * 0.14), 2)
            pygame.draw.circle(self.board_surface, COLOR_TEXT_LIGHT, center, int(SQUARE_SIZE * 0.04))

        self.screen.blit(self.board_surface, (0, 0))
        if self.promotion_active: self.draw_promotion_overlay()

    def draw_promotion_overlay(self):
        overlay = pygame.Surface((BOARD_SIZE, HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))
        
        modal_w, modal_h = int(BOARD_SIZE * 0.7), int(HEIGHT * 0.3)
        modal_rect = pygame.Rect((BOARD_SIZE - modal_w) // 2, (HEIGHT - modal_h) // 2, modal_w, modal_h)
        pygame.draw.rect(self.screen, COLOR_LUXE_DARK, modal_rect, border_radius=16)
        pygame.draw.rect(self.screen, COLOR_LUXE_GOLD, modal_rect, 2, border_radius=16)
        
        title = FONT_SUB.render("SELECT ASCENSION CLASS", True, COLOR_LUXE_GOLD)
        self.screen.blit(title, (modal_rect.x + (modal_w - title.get_width()) // 2, modal_rect.y + 20))
        
        options = ["Q", "R", "B", "N"] if self.turn == "B" else ["q", "r", "b", "n"]  
        is_gold = not (self.turn == "B")
        box_size = int(SQUARE_SIZE * 1.1)
        spacing = (modal_w - (4 * box_size)) // 5
        self.promotion_options = []
        
        mouse_pos = pygame.mouse.get_pos()
        for idx, item in enumerate(options):
            bx = modal_rect.x + spacing + idx * (box_size + spacing)
            by = modal_rect.y + int(modal_h * 0.4)
            btn_rect = pygame.Rect(bx, by, box_size, box_size)
            self.promotion_options.append((btn_rect, item))
            
            if btn_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, COLOR_HIGHLIGHT, btn_rect, border_radius=12)
                pygame.draw.rect(self.screen, COLOR_ACCENT, btn_rect, 2, border_radius=12)
            else:
                pygame.draw.rect(self.screen, COLOR_SIDEBAR_START, btn_rect, border_radius=12)
                pygame.draw.rect(self.screen, COLOR_LUXE_GOLD, btn_rect, 1, border_radius=12)
            self.draw_premium_piece(self.screen, item, is_gold, bx, by, size_scale=1.1)

    def draw_luxury_save_vault(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))
        
        v_w, v_h = int(WIDTH * 0.5), int(HEIGHT * 0.35)
        v_rect = pygame.Rect((WIDTH - v_w) // 2, (HEIGHT - v_h) // 2, v_w, v_h)
        
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_START, v_rect, border_radius=16)
        pygame.draw.rect(self.screen, COLOR_LUXE_DARK, v_rect, int(BOARD_SIZE*0.01), border_radius=16)
        pygame.draw.rect(self.screen, COLOR_LUXE_GOLD, v_rect, 2, border_radius=16)
        
        title = FONT_MAIN.render("ARCHIVE SOVEREIGN LOG", True, COLOR_LUXE_GOLD)
        self.screen.blit(title, (v_rect.x + (v_w - title.get_width()) // 2, v_rect.y + int(v_h * 0.1)))
        
        sub = FONT_SMALL.render("Enter your custom designation path below:", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub, (v_rect.x + (v_w - sub.get_width()) // 2, v_rect.y + int(v_h * 0.28)))
        
        t_w, t_h = int(v_w * 0.8), int(BOARD_SIZE * 0.06)
        t_rect = pygame.Rect(v_rect.x + (v_w - t_w) // 2, v_rect.y + int(v_h * 0.45), t_w, t_h)
        pygame.draw.rect(self.screen, COLOR_LUXE_DARK, t_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_ACCENT, t_rect, 1, border_radius=8)
        
        display_str = f"{self.save_filename}.chess"
        text_surf = FONT_SUB.render(display_str, True, COLOR_TEXT_LIGHT)
        self.screen.blit(text_surf, (t_rect.x + 20, t_rect.y + (t_h - text_surf.get_height()) // 2))
        
        self.cursor_blink_time = (self.cursor_blink_time + 1) % 60
        if self.cursor_blink_time < 30:
            base_x = t_rect.x + 22 + FONT_SUB.size(self.save_filename)[0]
            pygame.draw.line(self.screen, COLOR_LUXE_GOLD, (base_x, t_rect.y + 12), (base_x, t_rect.y + t_h - 12), 3)
            
        footer = FONT_SMALL.render("[ENTER] Finalize & Archive   |   [ESC] Dismiss Vault", True, COLOR_TEXT_MUTED)
        self.screen.blit(footer, (v_rect.x + (v_w - footer.get_width()) // 2, v_rect.y + int(v_h * 0.82)))

    def draw_luxury_load_vault(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))
        
        v_w, v_h = int(WIDTH * 0.5), int(HEIGHT * 0.35)
        v_rect = pygame.Rect((WIDTH - v_w) // 2, (HEIGHT - v_h) // 2, v_w, v_h)
        
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_START, v_rect, border_radius=16)
        pygame.draw.rect(self.screen, COLOR_LUXE_DARK, v_rect, int(BOARD_SIZE*0.01), border_radius=16)
        pygame.draw.rect(self.screen, COLOR_LUXE_GOLD, v_rect, 2, border_radius=16)
        
        title_str = "OPEN ARCHIVE FOR INSPECTION" if self.game_mode == "WATCH" else "RESTORE SOVEREIGN LOG"
        title = FONT_MAIN.render(title_str, True, COLOR_LUXE_GOLD)
        self.screen.blit(title, (v_rect.x + (v_w - title.get_width()) // 2, v_rect.y + int(v_h * 0.1)))
        
        sub = FONT_SMALL.render("Enter target archive matching file prefix:", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub, (v_rect.x + (v_w - sub.get_width()) // 2, v_rect.y + int(v_h * 0.28)))
        
        t_w, t_h = int(v_w * 0.8), int(BOARD_SIZE * 0.06)
        t_rect = pygame.Rect(v_rect.x + (v_w - t_w) // 2, v_rect.y + int(v_h * 0.45), t_w, t_h)
        pygame.draw.rect(self.screen, COLOR_LUXE_DARK, t_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_HIGHLIGHT, t_rect, 1, border_radius=8)
        
        display_str = f"{self.load_filename}.chess"
        text_surf = FONT_SUB.render(display_str, True, COLOR_TEXT_LIGHT)
        self.screen.blit(text_surf, (t_rect.x + 20, t_rect.y + (t_h - text_surf.get_height()) // 2))
        
        self.cursor_blink_time = (self.cursor_blink_time + 1) % 60
        if self.cursor_blink_time < 30:
            base_x = t_rect.x + 22 + FONT_SUB.size(self.load_filename)[0]
            pygame.draw.line(self.screen, COLOR_LUXE_GOLD, (base_x, t_rect.y + 12), (base_x, t_rect.y + t_h - 12), 3)
            
        footer = FONT_SMALL.render("[ENTER] Read & Synchronize   |   [ESC] Dismiss Vault", True, COLOR_TEXT_MUTED)
        self.screen.blit(footer, (v_rect.x + (v_w - footer.get_width()) // 2, v_rect.y + int(v_h * 0.82)))

    def draw_sidebar(self):
        self.draw_luxe_sidebar_background()
        pygame.draw.line(self.screen, COLOR_LUXE_GOLD, (BOARD_SIZE, 0), (BOARD_SIZE, HEIGHT), 3)
        pad_x = BOARD_SIZE + int(SIDEBAR_WIDTH * 0.08)
        content_w = int(SIDEBAR_WIDTH * 0.84)
        
        if self.game_mode == "HUMAN": mode_str = "Sovereign PvP Core"
        elif self.game_mode == "BOT": mode_str = "System AI Matrix Engaged"
        else: mode_str = "Spectator Inspection Matrix"
            
        self.screen.blit(FONT_SMALL.render(mode_str, True, COLOR_TEXT_MUTED), (pad_x, HEIGHT * 0.02))
        turn_str = "Golden Alliance" if self.turn == "W" else "Obsidian Alliance"
        self.screen.blit(FONT_MAIN.render(turn_str, True, COLOR_LUXE_GOLD), (pad_x, HEIGHT * 0.04))
        self.screen.blit(FONT_SMALL.render(self.status_message, True, COLOR_TEXT_LIGHT), (pad_x, HEIGHT * 0.10))
        
        box_history = pygame.Rect(pad_x, int(HEIGHT * 0.14), content_w, int(HEIGHT * 0.30))
        pygame.draw.rect(self.screen, COLOR_NOTATION_BG, box_history, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_LUXE_GOLD, box_history, 2, border_radius=6)
        
        history_header = FONT_NOTATION.render("Live Move Notation Matrix:", True, COLOR_NOTATION_GOLD)
        self.screen.blit(history_header, (pad_x + 15, int(HEIGHT * 0.15)))
        
        log_y_start = int(HEIGHT * 0.18)
        max_rows = 6
        line_height = int(HEIGHT * 0.018)
        
        pairs_count = (len(self.move_history) + 1) // 2
        start_pair_idx = max(0, pairs_count - max_rows)
        
        for r_idx in range(min(pairs_count, max_rows)):
            actual_pair_idx = start_pair_idx + r_idx
            move_num = actual_pair_idx + 1
            w_idx = actual_pair_idx * 2
            b_idx = w_idx + 1
            w_str = self.move_history[w_idx] if w_idx < len(self.move_history) else ""
            b_str = self.move_history[b_idx] if b_idx < len(self.move_history) else ""
            
            render_y = log_y_start + (r_idx * line_height)
            num_surf = FONT_NOTATION.render(f"{move_num}.", True, COLOR_NOTATION_INDEX)
            w_surf = FONT_NOTATION.render(w_str, True, COLOR_NOTATION_GOLD)
            b_surf = FONT_NOTATION.render(b_str, True, COLOR_NOTATION_BLACK)
            
            self.screen.blit(num_surf, (box_history.x + 15, render_y))
            self.screen.blit(w_surf, (box_history.x + 65, render_y))
            self.screen.blit(b_surf, (box_history.x + 165, render_y))
            
        box_white_cap = pygame.Rect(pad_x, int(HEIGHT * 0.49), content_w, int(HEIGHT * 0.11))
        box_black_cap = pygame.Rect(pad_x, int(HEIGHT * 0.64), content_w, int(HEIGHT * 0.11))
        
        pygame.draw.rect(self.screen, COLOR_LUXE_DARK, box_white_cap, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_LUXE_GOLD, box_white_cap, 1, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_LUXE_DARK, box_black_cap, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_LUXE_GOLD, box_black_cap, 1, border_radius=6)
        
        self.screen.blit(FONT_SMALL.render("Gold Captured:", True, COLOR_LUXE_GOLD), (pad_x + 5, int(HEIGHT * 0.46)))
        self.screen.blit(FONT_SMALL.render("Obsidian Captured:", True, COLOR_LUXE_GOLD), (pad_x + 5, int(HEIGHT * 0.61)))
        
        p_scale = 0.45
        step_w = int(SQUARE_SIZE * p_scale) + 4
        for idx, p in enumerate(self.captured_by_white):
            self.draw_premium_piece(self.screen, p, p.isupper(), box_white_cap.x + 10 + (idx % 8) * step_w, box_white_cap.y + 8 + (idx // 8) * step_w, size_scale=p_scale)
        for idx, p in enumerate(self.captured_by_black):
            self.draw_premium_piece(self.screen, p, p.isupper(), box_black_cap.x + 10 + (idx % 8) * step_w, box_black_cap.y + 8 + (idx // 8) * step_w, size_scale=p_scale)

        pygame.draw.rect(self.screen, COLOR_LUXE_DARK, (pad_x, int(HEIGHT * 0.77), content_w, int(HEIGHT * 0.18)), border_radius=6)
        if self.game_mode == "WATCH":
            self.screen.blit(FONT_SMALL.render("[<-] -> Review Previous Move Status", True, COLOR_HIGHLIGHT), (pad_x + 15, int(HEIGHT * 0.79)))
            self.screen.blit(FONT_SMALL.render("[->] -> Advance Timeline Step", True, COLOR_HIGHLIGHT), (pad_x + 15, int(HEIGHT * 0.83)))
        else:
            self.screen.blit(FONT_SMALL.render("[S] -> Save Match to .chess File", True, COLOR_ACCENT), (pad_x + 15, int(HEIGHT * 0.79)))
            self.screen.blit(FONT_SMALL.render("[L] -> Load Match from .chess File", True, COLOR_HIGHLIGHT), (pad_x + 15, int(HEIGHT * 0.83)))
        self.screen.blit(FONT_SMALL.render("[ESC] -> Main Menu Core", True, COLOR_TEXT_MUTED), (pad_x + 15, int(HEIGHT * 0.87)))

    def get_king_square(self, color, current_board=None):
        target_board = current_board if current_board is not None else self.board
        target_king = "K" if color == "W" else "k"
        for r in range(8):
            for c in range(8):
                if target_board[r][c] == target_king: return (r, c)
        return None

    def is_in_check(self, color, current_board):
        king_pos = self.get_king_square(color, current_board)
        if not king_pos: return False
        enemy_color = "B" if color == "W" else "W"
        for r in range(8):
            for c in range(8):
                piece = current_board[r][c]
                if piece != "-" and (piece.isupper() if enemy_color == "W" else piece.islower()):
                    if king_pos in self.get_piece_structural_moves(r, c, current_board): return True
        return False

    def get_piece_structural_moves(self, row, col, target_board):
        moves = []
        piece = target_board[row][col]
        if piece == "-": return moves
        is_gold = piece.isupper()
        
        if piece.upper() == "P":
            direction = -1 if is_gold else 1
            if 0 <= row + direction < 8 and target_board[row + direction][col] == "-":
                moves.append((row + direction, col))
                start_rank = 6 if is_gold else 1
                if row == start_rank and target_board[row + (2 * direction)][col] == "-":
                    moves.append((row + (2 * direction), col))
            for dc in [-1, 1]:
                t_c, t_r = col + dc, row + direction
                if 0 <= t_r < 8 and 0 <= t_c < 8:
                    t_p = target_board[t_r][t_c]
                    if t_p != "-" and t_p.isupper() != is_gold: moves.append((t_r, t_c))
        else:
            dirs = []
            if piece.upper() in ["R", "Q"]: dirs.extend([(1,0), (-1,0), (0,1), (0,-1)])
            if piece.upper() in ["B", "Q"]: dirs.extend([(1,1), (1,-1), (-1,1), (-1,-1)])
            if piece.upper() == "N":
                for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                    r, c = row + dr, col + dc
                    if 0 <= r < 8 and 0 <= c < 8:
                        if target_board[r][c] == "-" or target_board[r][c].isupper() != is_gold: moves.append((r, c))
            elif piece.upper() == "K":
                for dr in [-1,0,1]:
                    for dc in [-1,0,1]:
                        r, c = row + dr, col + dc
                        if 0 <= r < 8 and 0 <= c < 8 and (dr != 0 or dc != 0):
                            if target_board[r][c] == "-" or target_board[r][c].isupper() != is_gold: moves.append((r, c))
            for dr, dc in dirs:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if target_board[r][c] == "-": moves.append((r, c))
                    elif target_board[r][c].isupper() != is_gold:
                        moves.append((r, c)); break
                    else: break
                    r += dr; c += dc
        return moves

    def get_legal_moves(self, row, col, custom_board=None):
        target_board = custom_board if custom_board is not None else self.board
        raw_moves = self.get_piece_structural_moves(row, col, target_board)
        legal_moves = []
        piece = target_board[row][col]
        is_gold = piece.isupper()
        
        for r, c in raw_moves:
            board_copy = copy.deepcopy(target_board)
            board_copy[r][c] = board_copy[row][col]
            board_copy[row][col] = "-"
            if not self.is_in_check("W" if is_gold else "B", board_copy):
                legal_moves.append((r, c))
                
        if custom_board is None and piece.upper() == "K" and not self.is_in_check("W" if is_gold else "B", target_board):
            rank = 7 if is_gold else 0
            k_key = "K_white" if is_gold else "K_black"
            if not self.has_moved[k_key]:
                r_right_key = "R_white_right" if is_gold else "R_black_right"
                if not self.has_moved[r_right_key] and target_board[rank][5] == "-" and target_board[rank][6] == "-":
                    if self.test_square_safety(rank, 5, is_gold): legal_moves.append((rank, 6))
                r_left_key = "R_white_left" if is_gold else "R_black_left"
                if not self.has_moved[r_left_key] and target_board[rank][1] == "-" and target_board[rank][2] == "-" and target_board[rank][3] == "-":
                    if self.test_square_safety(rank, 3, is_gold): legal_moves.append((rank, 2))
        return legal_moves

    def test_square_safety(self, r, c, is_gold):
        board_copy = copy.deepcopy(self.board)
        king_char = "K" if is_gold else "k"
        king_sq = self.get_king_square("W" if is_gold else "B")
        if king_sq:
            orig_r, orig_c = king_sq
            board_copy[orig_r][orig_c] = "-"
        board_copy[r][c] = king_char
        return not self.is_in_check("W" if is_gold else "B", board_copy)

    def verify_checkmate_status(self, color, custom_board=None):
        target_board = custom_board if custom_board is not None else self.board
        for r in range(8):
            for c in range(8):
                p = target_board[r][c]
                if p != "-" and (p.isupper() if color == "W" else p.islower()):
                    if len(self.get_legal_moves(r, c, target_board)) > 0: return False
        return True

    def trigger_move_animation(self, start, end, piece):
        self.animating_piece = piece
        self.anim_start = start
        self.anim_end = end
        self.anim_progress = 0.0

    def evaluate_static_board(self, board_matrix):
        score = 0
        for r in range(8):
            for c in range(8):
                p = board_matrix[r][c]
                if p != "-":
                    val = PIECE_VALUES[p.lower()]
                    if p.isupper(): score += val
                    else: score -= val
        return score

    def make_bot_move(self):
        if self.game_over or self.promotion_active or self.save_active or self.load_active: return
        scored_moves = []
        for r in range(8):
            for c in range(8):
                if self.board[r][c].islower():
                    moves = self.get_legal_moves(r, c)
                    for m in moves:
                        sim_board = copy.deepcopy(self.board)
                        sim_board[m[0]][m[1]] = sim_board[r][c]
                        sim_board[r][c] = "-"
                        if self.is_in_check("W", sim_board) and self.verify_checkmate_status("W", sim_board):
                            self.execute_board_move((r, c), m)
                            return
                        base_score = self.evaluate_static_board(sim_board)
                        if self.is_in_check("B", sim_board): base_score += 15
                        if self.is_in_check("W", sim_board): base_score -= 8
                        scored_moves.append((base_score, (r, c), m))
                        
        if scored_moves:
            scored_moves.sort(key=lambda x: x[0])
            best_score = scored_moves[0][0]
            top_candidates = [move for move in scored_moves if move[0] == best_score]
            _, start, end = random.choice(top_candidates)
            self.execute_board_move(start, end)
        else:
            self.evaluate_endgame_state()

    def execute_board_move(self, start, end):
        sr, sc = start
        row, col = end
        p = self.board[sr][sc]
        target_captured = self.board[row][col]
        
        notated_string = self.convert_to_notation(p, start, end, target_captured)
        self.move_history.append(notated_string)
        
        if target_captured != "-":
            if self.turn == "W": self.captured_by_white.append(target_captured)
            else: self.captured_by_black.append(target_captured)
            self.status_message = f"Captured enemy {target_captured.upper()}"
        else:
            self.status_message = "Move Executed Gracefully"

        if p.upper() == "K" and abs(sc - col) == 2:
            rank = 7 if p.isupper() else 0
            if col == 6:
                self.board[rank][5] = self.board[rank][7]; self.board[rank][7] = "-"
            elif col == 2:
                self.board[rank][3] = self.board[rank][0]; self.board[rank][0] = "-"

        self.board[row][col] = p
        self.board[sr][sc] = "-"
        
        if sr == 7 and sc == 4: self.has_moved["K_white"] = True
        if sr == 0 and sc == 4: self.has_moved["K_black"] = True
        if sr == 7 and sc == 0: self.has_moved["R_white_left"] = True
        if sr == 7 and sc == 7: self.has_moved["R_white_right"] = True
        if sr == 0 and sc == 0: self.has_moved["R_black_left"] = True
        if sr == 0 and sc == 7: self.has_moved["R_black_right"] = True

        self.trigger_move_animation(start, end, self.board[row][col])
        self.turn = "B" if self.turn == "W" else "W"
        
        if self.game_mode == "HUMAN":
            self.start_angle = self.current_angle
            self.target_angle = 180.0 if self.turn == "B" else 0.0
            self.rot_progress = 0.0

    def check_post_move_conditions(self):
        look_color = "W" if self.turn == "B" else "B"
        promo_rank = 0 if look_color == "W" else 7
        p_char = "P" if look_color == "W" else "p"
        
        for col in range(8):
            if self.board[promo_rank][col] == p_char:
                if self.game_mode == "BOT" and look_color == "B":
                    self.board[promo_rank][col] = "q"
                    if self.move_history: self.move_history[-1] += "=Q"
                    self.status_message = "System Queen Ascended"
                else:
                    self.promotion_active = True
                    self.promotion_square = (promo_rank, col)
                    self.status_message = "Awaiting Ascension Selection"
                    return 

        self.evaluate_endgame_state()
        if self.game_mode == "BOT" and self.turn == "B" and not self.game_over:
            self.make_bot_move()

    def evaluate_endgame_state(self):
        if self.is_in_check(self.turn, self.board):
            if self.verify_checkmate_status(self.turn):
                self.game_over = True
                self.status_message = f"CHECKMATE. {'Obsidian' if self.turn=='W' else 'Gold'} Wins."
            else:
                self.status_message = "King Vulnerable (In Check)"
        elif self.verify_checkmate_status(self.turn):
            self.game_over = True
            self.status_message = "Stalemate Concluded"

    def handle_click(self, pos):
        if self.game_mode == "MENU":
            if self.btn_human.collidepoint(pos): 
                self.game_mode = "HUMAN"
                self.reset_game_state()
            elif self.btn_bot.collidepoint(pos): 
                self.game_mode = "BOT"
                self.reset_game_state()
            elif self.btn_watch.collidepoint(pos): 
                self.game_mode = "WATCH"
                self.reset_game_state()
                self.load_active = True  
                self.cursor_blink_time = 0
            return

        if self.save_active or self.load_active or self.game_mode == "WATCH": return

        if self.promotion_active:
            for rect, item in self.promotion_options:
                if rect.collidepoint(pos):
                    pr, pc = self.promotion_square
                    self.board[pr][pc] = item
                    if self.move_history: self.move_history[-1] += f"={item.upper()}"
                    self.promotion_active = False
                    self.status_message = "Ascension Order Dispatched"
                    self.evaluate_endgame_state()
                    if self.game_mode == "BOT" and self.turn == "B" and not self.game_over:
                        self.make_bot_move()
            return

        x, y = pos
        if x >= BOARD_SIZE or self.anim_progress < 1.0 or self.game_over: return
        if self.rot_progress < 1.0: return 
        
        if self.current_angle > 90.0:
            col = 7 - (x // SQUARE_SIZE)
            row = 7 - (y // SQUARE_SIZE)
        else:
            col = x // SQUARE_SIZE
            row = y // SQUARE_SIZE
        
        if self.selected_square:
            if (row, col) in self.valid_moves:
                self.execute_board_move(self.selected_square, (row, col))
                self.selected_square = None
                self.valid_moves = []
            else:
                piece = self.board[row][col]
                if piece != "-" and ((self.turn == "W" and piece.isupper()) or (self.turn == "B" and piece.islower())):
                    self.selected_square = (row, col)
                    self.valid_moves = self.get_legal_moves(row, col)
                else:
                    self.selected_square = None; self.valid_moves = []
        else:
            piece = self.board[row][col]
            if piece != "-" and ((self.turn == "W" and piece.isupper()) or (self.turn == "B" and piece.islower())):
                self.selected_square = (row, col)
                self.valid_moves = self.get_legal_moves(row, col)

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                    
                elif event.type == pygame.KEYDOWN:
                    if self.save_active:
                        if event.key == pygame.K_ESCAPE: self.save_active = False
                        elif event.key == pygame.K_RETURN: self.execute_save_to_file()
                        elif event.key == pygame.K_BACKSPACE: self.save_filename = self.save_filename[:-1]
                        else:
                            if len(self.save_filename) < 22:
                                if event.unicode.isalnum() or event.unicode in ('_', '-'):
                                    self.save_filename += event.unicode
                        continue

                    if self.load_active:
                        if event.key == pygame.K_ESCAPE: 
                            self.load_active = False
                            if self.game_mode == "WATCH": self.game_mode = "MENU"
                        elif event.key == pygame.K_RETURN: self.execute_load_from_file()
                        elif event.key == pygame.K_BACKSPACE: self.load_filename = self.load_filename[:-1]
                        else:
                            if len(self.load_filename) < 22:
                                if event.unicode.isalnum() or event.unicode in ('_', '-'):
                                    self.load_filename += event.unicode
                        continue

                    if event.key == pygame.K_ESCAPE: 
                        if self.game_mode == "MENU": pygame.quit(); sys.exit()
                        else: self.game_mode = "MENU"
                        
                    elif self.game_mode == "WATCH":
                        if event.key == pygame.K_RIGHT:
                            self.navigate_spectator_timeline(1)
                        elif event.key == pygame.K_LEFT:
                            self.navigate_spectator_timeline(-1)
                            
                    else:
                        if event.key == pygame.K_s:
                            if self.game_mode != "MENU":
                                self.save_active = True
                                self.cursor_blink_time = 0
                        elif event.key == pygame.K_l:
                            if self.game_mode != "MENU":
                                self.load_active = True
                                self.cursor_blink_time = 0
                        
            if self.game_mode == "MENU": 
                self.draw_menu()
            else:
                self.draw_board()
                self.draw_sidebar()
                if self.save_active: self.draw_luxury_save_vault()
                elif self.load_active: self.draw_luxury_load_vault()
                
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    game = UltraLuxeChess()
    game.run()