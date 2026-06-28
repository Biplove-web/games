import pygame
import random
import sys

pygame.init()
pygame.font.init()

SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Teen Patti")
clock = pygame.time.Clock()

COLOR_TABLE = (18, 90, 45)
COLOR_BORDER = (12, 60, 30)
COLOR_WOOD = (55, 33, 18)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (20, 20, 20)
COLOR_GOLD = (230, 180, 40)
COLOR_RED = (210, 40, 40)
COLOR_BLUE = (40, 110, 220)
COLOR_GRAY = (180, 180, 180)

FONT_LARGE = pygame.font.SysFont("sans-serif", 42, bold=True)
FONT_MED = pygame.font.SysFont("sans-serif", 24, bold=True)
FONT_SMALL = pygame.font.SysFont("sans-serif", 18, bold=True)

SUITS = ['♠', '♥', '♦', '♣']
RANKS = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
RANK_NAMES = list(RANKS.keys())

def create_deck():
    deck = [(rank, suit) for rank in RANK_NAMES for suit in SUITS]
    random.shuffle(deck)
    return deck

def evaluate_hand(hand):
    sorted_hand = sorted(hand, key=lambda card: RANKS[card[0]], reverse=True)
    v1, v2, v3 = RANKS[sorted_hand[0][0]], RANKS[sorted_hand[1][0]], RANKS[sorted_hand[2][0]]
    s1, s2, s3 = sorted_hand[0][1], sorted_hand[1][1], sorted_hand[2][1]

    if v1 == v2 == v3: return (6, v1)
    
    is_seq = False
    if v1 - v2 == 1 and v2 - v3 == 1:
        is_seq = True
        seq_high = v1
    elif v1 == 14 and v2 == 3 and v3 == 2:
        is_seq = True
        seq_high = 14

    is_flush = (s1 == s2 == s3)

    if is_seq and is_flush: return (5, seq_high)
    if is_seq: return (4, seq_high)
    if is_flush: return (3, v1, v2, v3)
    if v1 == v2: return (2, v1, v3)
    if v2 == v3: return (2, v2, v1)
    if v1 == v3: return (2, v1, v2)

    return (1, v1, v2, v3)

def get_hand_name(score_tuple):
    hand_types = {6: "Trail (Trio)", 5: "Pure Sequence", 4: "Sequence (Run)", 3: "Color (Flush)", 2: "Pair", 1: "High Card"}
    return hand_types[score_tuple[0]]

def draw_suit_shape(surface, cx, cy, suit, color):
    if suit == '♦':
        points = [(cx, cy - 15), (cx + 12, cy), (cx, cy + 15), (cx - 12, cy)]
        pygame.draw.polygon(surface, color, points)
        
    elif suit == '♥':
        pygame.draw.circle(surface, color, (cx - 6, cy - 4), 7)
        pygame.draw.circle(surface, color, (cx + 6, cy - 4), 7)
        points = [(cx - 13, cy - 2), (cx + 13, cy - 2), (cx, cy + 14)]
        pygame.draw.polygon(surface, color, points)
        
    elif suit == '♠':
        pygame.draw.circle(surface, color, (cx - 6, cy + 2), 7)
        pygame.draw.circle(surface, color, (cx + 6, cy + 2), 7)
        points = [(cx - 13, cy + 1), (cx + 13, cy + 1), (cx, cy - 14)]
        pygame.draw.polygon(surface, color, points)
        stem_points = [(cx, cy), (cx - 5, cy + 13), (cx + 5, cy + 13)]
        pygame.draw.polygon(surface, color, stem_points)
        
    elif suit == '♣':
        pygame.draw.circle(surface, color, (cx, cy - 7), 7)      
        pygame.draw.circle(surface, color, (cx - 7, cy + 2), 7)  
        pygame.draw.circle(surface, color, (cx + 7, cy + 2), 7)  
        stem_points = [(cx, cy), (cx - 4, cy + 13), (cx + 4, cy + 13)]
        pygame.draw.polygon(surface, color, stem_points)

def draw_card(surface, x, y, card, face_up=True):
    width, height = 70, 100
    pygame.draw.rect(surface, (0, 0, 0, 40), (x + 2, y + 2, width, height), border_radius=6)
    pygame.draw.rect(surface, COLOR_WHITE, (x, y, width, height), border_radius=6)
    pygame.draw.rect(surface, COLOR_GRAY, (x, y, width, height), width=1, border_radius=6)

    if not face_up:
        pygame.draw.rect(surface, COLOR_RED, (x + 4, y + 4, width - 8, height - 8), border_radius=4)
        pygame.draw.rect(surface, COLOR_GOLD, (x + 8, y + 8, width - 16, height - 16), width=1, border_radius=2)
        return

    rank, suit = card
    color = COLOR_RED if suit in ['♥', '♦'] else COLOR_BLACK
    
    rank_txt = FONT_MED.render(rank, True, color)
    surface.blit(rank_txt, (x + 6, y + 4))
    
    center_x = x + width // 2
    center_y = y + height // 2 + 3
    draw_suit_shape(surface, center_x, center_y, suit, color)

DECK_POS = (SCREEN_WIDTH // 2 - 35, SCREEN_HEIGHT // 2 - 50)

PLAYER_POSITIONS = {
    "User": [(SCREEN_WIDTH // 2 - 110 + (i * 75), SCREEN_HEIGHT - 160) for i in range(3)],
    "CPU 1": [(60 + (i * 75), SCREEN_HEIGHT // 2 - 50) for i in range(3)],
    "CPU 2": [(SCREEN_WIDTH // 2 - 110 + (i * 75), 80) for i in range(3)],
    "CPU 3": [(SCREEN_WIDTH - 270 + (i * 75), SCREEN_HEIGHT // 2 - 50) for i in range(3)]
}

class AnimatedCard:
    def __init__(self, card, target_pos, delay):
        self.card = card
        self.current_x, self.current_y = DECK_POS[0], DECK_POS[1]
        self.target_x, self.target_y = target_pos
        self.delay = delay
        self.progress = 0.0
        self.speed = 0.07  
        self.done = False

    def update(self, current_tick):
        if current_tick < self.delay:
            return
        if self.progress < 1.0:
            self.progress += self.speed
            if self.progress >= 1.0:
                self.progress = 1.0
                self.done = True
            self.current_x = DECK_POS[0] + (self.target_x - DECK_POS[0]) * self.progress
            self.current_y = DECK_POS[1] + (self.target_y - DECK_POS[1]) * self.progress

    def draw(self, surface, face_up):
        if pygame.time.get_ticks() >= self.delay:
            draw_card(surface, int(self.current_x), int(self.current_y), self.card, face_up)

def setup_round():
    global deck, player_hands, animated_cards, game_state, winner_text
    deck = create_deck()
    
    player_hands = {
        "User": [deck.pop(), deck.pop(), deck.pop()],
        "CPU 1": [deck.pop(), deck.pop(), deck.pop()],
        "CPU 2": [deck.pop(), deck.pop(), deck.pop()],
        "CPU 3": [deck.pop(), deck.pop(), deck.pop()]
    }
    
    animated_cards = []
    delay_accumulator = pygame.time.get_ticks() + 200
    
    for card_idx in range(3):
        for p_name in ["User", "CPU 1", "CPU 2", "CPU 3"]:
            target = PLAYER_POSITIONS[p_name][card_idx]
            card_data = player_hands[p_name][card_idx]
            animated_cards.append(AnimatedCard(card_data, target, delay_accumulator))
            delay_accumulator += 120  
            
    game_state = "DEALING"
    winner_text = ""

setup_round()

running = True
while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                if game_state == "PLAYING":
                    game_state = "SHOWDOWN"
                    scores = {p: evaluate_hand(hand) for p, hand in player_hands.items()}
                    winner = max(scores, key=scores.get)
                    winner_text = f"{winner} Wins with a {get_hand_name(scores[winner])}!"
                elif game_state == "SHOWDOWN":
                    setup_round()

    screen.fill(COLOR_WOOD)
    pygame.draw.ellipse(screen, COLOR_BORDER, (40, 40, SCREEN_WIDTH-80, SCREEN_HEIGHT-80))
    pygame.draw.ellipse(screen, COLOR_TABLE, (55, 55, SCREEN_WIDTH-110, SCREEN_HEIGHT-110))
    
    if game_state == "DEALING":
        draw_card(screen, DECK_POS[0], DECK_POS[1], (None, None), face_up=False)

    all_done = True
    for ac in animated_cards:
        ac.update(current_time)
        if not ac.done:
            all_done = False
        
        is_user_card = ac.target_y > SCREEN_HEIGHT - 200
        reveal = is_user_card or (game_state == "SHOWDOWN")
        ac.draw(screen, face_up=reveal)

    if game_state == "DEALING" and all_done:
        game_state = "PLAYING"

    if game_state == "PLAYING":
        inst_txt = FONT_MED.render("Press SPACE for Showdown!", True, COLOR_GOLD)
        screen.blit(inst_txt, (SCREEN_WIDTH//2 - inst_txt.get_width()//2, SCREEN_HEIGHT//2 - 20))
        
        strength_str = get_hand_name(evaluate_hand(player_hands["User"]))
        str_txt = FONT_SMALL.render(f"Your Hand: {strength_str}", True, COLOR_WHITE)
        screen.blit(str_txt, (SCREEN_WIDTH//2 - str_txt.get_width()//2, SCREEN_HEIGHT - 50))
        
    elif game_state == "SHOWDOWN":
        win_txt = FONT_LARGE.render(winner_text, True, COLOR_GOLD)
        screen.blit(win_txt, (SCREEN_WIDTH//2 - win_txt.get_width()//2, SCREEN_HEIGHT//2 - 100))
        
        restart_txt = FONT_SMALL.render("Press SPACE to play again", True, COLOR_WHITE)
        screen.blit(restart_txt, (SCREEN_WIDTH//2 - restart_txt.get_width()//2, SCREEN_HEIGHT//2 - 40))

    screen.blit(FONT_MED.render("User (You)", True, COLOR_WHITE), (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT - 200))
    screen.blit(FONT_SMALL.render("CPU 1", True, COLOR_WHITE), (140, SCREEN_HEIGHT//2 - 80))
    screen.blit(FONT_SMALL.render("CPU 2", True, COLOR_WHITE), (SCREEN_WIDTH//2 - 25, 50))
    screen.blit(FONT_SMALL.render("CPU 3", True, COLOR_WHITE), (SCREEN_WIDTH - 200, SCREEN_HEIGHT//2 - 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()