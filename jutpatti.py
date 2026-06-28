import pygame
import random
import sys

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Jutpatti")
clock = pygame.time.Clock()

COLOR_TABLE = (24, 76, 120)    
COLOR_BORDER = (14, 50, 80)
COLOR_WOOD = (43, 29, 20)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (20, 20, 20)
COLOR_GOLD = (235, 190, 50)
COLOR_RED = (220, 45, 45)
COLOR_BLUE = (45, 130, 240)
COLOR_GRAY = (190, 190, 190)

FONT_LARGE = pygame.font.SysFont("sans-serif", 42, bold=True)
FONT_MED = pygame.font.SysFont("sans-serif", 24, bold=True)
FONT_SMALL = pygame.font.SysFont("sans-serif", 18, bold=True)

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {rank: index for index, rank in enumerate(RANKS)}

def draw_suit_shape(surface, cx, cy, suit, color):
    if suit == '♦': 
        points = [(cx, cy - 13), (cx + 10, cy), (cx, cy + 13), (cx - 10, cy)]
        pygame.draw.polygon(surface, color, points)
    elif suit == '♥': 
        pygame.draw.circle(surface, color, (cx - 5, cy - 3), 6)
        pygame.draw.circle(surface, color, (cx + 5, cy - 3), 6)
        points = [(cx - 11, cy - 1), (cx + 11, cy - 1), (cx, cy + 12)]
        pygame.draw.polygon(surface, color, points)
    elif suit == '♠': 
        pygame.draw.circle(surface, color, (cx - 5, cy + 2), 6)
        pygame.draw.circle(surface, color, (cx + 5, cy + 2), 6)
        points = [(cx - 11, cy + 1), (cx + 11, cy + 1), (cx, cy - 12)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, color, [(cx, cy), (cx - 4, cy + 11), (cx + 4, cy + 11)])
    elif suit == '♣': 
        pygame.draw.circle(surface, color, (cx, cy - 6), 6)      
        pygame.draw.circle(surface, color, (cx - 6, cy + 2), 6)  
        pygame.draw.circle(surface, color, (cx + 7, cy + 2), 6)  
        pygame.draw.polygon(surface, color, [(cx, cy), (cx - 3, cy + 11), (cx + 3, cy + 11)])

def draw_card(surface, x, y, card, face_up=True, selected=False, is_joker=False):
    width, height = 70, 100
    y_offset = -15 if selected else 0
    actual_y = y + y_offset
    
    pygame.draw.rect(surface, (0, 0, 0, 40), (x + 2, actual_y + 2, width, height), border_radius=6)
    pygame.draw.rect(surface, COLOR_WHITE, (x, actual_y, width, height), border_radius=6)
    
    if is_joker and face_up:
        pygame.draw.rect(surface, COLOR_GOLD, (x, actual_y, width, height), width=3, border_radius=6)
    elif selected:
        pygame.draw.rect(surface, COLOR_BLUE, (x, actual_y, width, height), width=3, border_radius=6)
    else:
        pygame.draw.rect(surface, COLOR_GRAY, (x, actual_y, width, height), width=1, border_radius=6)

    if not face_up:
        pygame.draw.rect(surface, COLOR_BLUE, (x + 4, actual_y + 4, width - 8, height - 8), border_radius=4)
        return

    rank, suit = card
    color = COLOR_RED if suit in ['♥', '♦'] else COLOR_BLACK
    
    rank_txt = FONT_MED.render(rank, True, color)
    surface.blit(rank_txt, (x + 6, actual_y + 4))
    draw_suit_shape(surface, x + width // 2, actual_y + height // 2 + 5, suit, color)
    
    if is_joker:
        j_txt = FONT_SMALL.render("JOKER", True, COLOR_GOLD)
        surface.blit(j_txt, (x + width//2 - j_txt.get_width()//2, actual_y + height - 20))

def evaluate_jutpatti_win(hand, joker_card):
    joker_rank = joker_card[0]
    jokers = [c for c in hand if c[0] == joker_rank]
    normals = [c for c in hand if c[0] != joker_rank]
    
    rank_counts = {}
    for c in normals:
        rank_counts[c[0]] = rank_counts.get(c[0], 0) + 1
        
    num_jokers = len(jokers)
    pairs = 0
    singletons = 0
    
    for rank, count in rank_counts.items():
        pairs += count // 2
        if count % 2 != 0:
            singletons += 1
            
    while num_jokers > 0 and singletons > 0:
        num_jokers -= 1
        singletons -= 1
        pairs += 1
        
    pairs += num_jokers // 2
    if num_jokers % 2 != 0:
        singletons += 1

    return pairs == 4 and singletons == 0

def sort_hand(hand):
    hand.sort(key=lambda card: RANK_VALUES[card[0]])

DECK_POS = (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 50)
JOKER_POS = (SCREEN_WIDTH // 2 - 35, SCREEN_HEIGHT // 2 - 50)
DISCARD_POS = (SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2 - 50)

USER_Y = SCREEN_HEIGHT - 160
CPU_Y = SCREEN_HEIGHT // 2 - 50

def get_target_positions(player_name, count):
    if player_name == "User":
        user_x_start = SCREEN_WIDTH // 2 - (count * 40)
        return [(user_x_start + (i * 80), USER_Y) for i in range(count)]
    elif player_name == "CPU 1":
        return [(30 + (i * 24), CPU_Y) for i in range(count)]
    elif player_name == "CPU 2":
        return [(SCREEN_WIDTH - 240 + (i * 24), CPU_Y) for i in range(count)]

class AnimationEffect:
    def __init__(self, card, start_pos, target_pos, duration=15, face_up=True, is_joker=False, callback=None):
        self.card = card
        self.x, self.y = start_pos
        self.start_x, self.start_y = start_pos
        self.target_x, self.target_y = target_pos
        self.frame = 0
        self.duration = duration
        self.face_up = face_up
        self.is_joker = is_joker
        self.callback = callback
        self.done = False

    def update(self):
        if self.frame < self.duration:
            self.frame += 1
            if self.frame > 0:
                t = self.frame / self.duration
                t = 1 - (1 - t) * (1 - t)
                self.x = self.start_x + (self.target_x - self.start_x) * t
                self.y = self.start_y + (self.target_y - self.start_y) * t
        else:
            if not self.done:
                self.done = True
                if self.callback:
                    self.callback()

    def draw(self, surface):
        if self.frame > 0:
            draw_card(surface, int(self.x), int(self.y), self.card, face_up=self.face_up, is_joker=self.is_joker)

deck = []
hands = {"User": [], "CPU 1": [], "CPU 2": []}
discard_pile = []
active_animations = []
joker_card = None
turn = "User"
game_state = "DEALING"
game_phase = "DRAW" 
selected_card_idx = 0
winner_text = ""

temp_sorting_hand = []
animated_discard_card = None 

def setup_game():
    global deck, hands, discard_pile, joker_card, turn, game_phase, game_state, selected_card_idx, winner_text, active_animations, temp_sorting_hand, animated_discard_card
    deck = [(rank, suit) for rank in RANKS for suit in SUITS]
    random.shuffle(deck)
    
    secret_hands = {
        "User": [deck.pop() for _ in range(7)],
        "CPU 1": [deck.pop() for _ in range(7)],
        "CPU 2": [deck.pop() for _ in range(7)]
    }
    sort_hand(secret_hands["User"])
    
    hands = {"User": [], "CPU 1": [], "CPU 2": []}
    temp_sorting_hand = []
    joker_card = deck.pop()
    discard_pile = [deck.pop()]
    animated_discard_card = None
    
    active_animations = []
    frames_offset = 0
    for card_idx in range(7):
        for p_name in ["User", "CPU 1", "CPU 2"]:
            targets = get_target_positions(p_name, 7)
            card_data = secret_hands[p_name][card_idx]
            
            def deal_callback(player=p_name, card=card_data):
                hands[player].append(card)
                
            anim = AnimationEffect(card_data, DECK_POS, targets[card_idx], duration=15, face_up=(p_name == "User"), callback=deal_callback)
            anim.frame = -frames_offset 
            active_animations.append(anim)
            frames_offset += 3
            
    game_state = "DEALING"
    game_phase = "DRAW"
    selected_card_idx = 0
    winner_text = ""

setup_game()

running = True
while running:
    screen.fill(COLOR_WOOD)
    pygame.draw.ellipse(screen, COLOR_BORDER, (40, 40, SCREEN_WIDTH-80, SCREEN_HEIGHT-80))
    pygame.draw.ellipse(screen, COLOR_TABLE, (55, 55, SCREEN_WIDTH-110, SCREEN_HEIGHT-110))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                
            elif game_state == "PLAYING" and winner_text == "":
                if turn == "User":
                    if event.key == pygame.K_s:
                        old_positions = get_target_positions("User", len(hands["User"]))
                        sort_hand(hands["User"])
                        new_positions = get_target_positions("User", len(hands["User"]))
                        
                        game_state = "ANIMATING"
                        active_animations = []
                        
                        temp_sorting_hand = list(hands["User"])
                        hands["User"] = [] 
                        
                        for i, card in enumerate(temp_sorting_hand):
                            anim = AnimationEffect(card, old_positions[i], new_positions[i], duration=12, face_up=True)
                            active_animations.append(anim)
                            
                        def end_sort_anim(final_set=temp_sorting_hand):
                            global game_state, hands, temp_sorting_hand
                            hands["User"] = final_set
                            temp_sorting_hand = []
                            game_state = "PLAYING"
                            
                        active_animations[-1].callback = end_sort_anim
                        selected_card_idx = 0

                    elif game_phase == "DRAW":
                        if event.key == pygame.K_d: 
                            drawn_card = deck.pop()
                            targets = get_target_positions("User", 8)
                            game_state = "ANIMATING"
                            
                            def complete_deck_draw(c=drawn_card):
                                global game_state, game_phase; hands["User"].append(c); game_state = "PLAYING"; game_phase = "DISCARD"
                            active_animations = [AnimationEffect(drawn_card, DECK_POS, targets[7], duration=12, face_up=True, callback=complete_deck_draw)]
                            
                        elif event.key == pygame.K_p: 
                            drawn_card = discard_pile.pop()
                            targets = get_target_positions("User", 8)
                            game_state = "ANIMATING"
                            
                            def complete_discard_draw(c=drawn_card):
                                global game_state, game_phase; hands["User"].append(c); game_state = "PLAYING"; game_phase = "DISCARD"
                            active_animations = [AnimationEffect(drawn_card, DISCARD_POS, targets[7], duration=12, face_up=True, callback=complete_discard_draw)]
                            
                    elif game_phase == "DISCARD":
                        if event.key == pygame.K_LEFT:
                            selected_card_idx = (selected_card_idx - 1) % len(hands["User"])
                        elif event.key == pygame.K_RIGHT:
                            selected_card_idx = (selected_card_idx + 1) % len(hands["User"])
                        elif event.key == pygame.K_SPACE:  
                            if evaluate_jutpatti_win(hands["User"], joker_card):
                                winner_text = "You Win Jutpatti!"
                                game_state = "SHOWDOWN"
                            else:
                                discarded = hands["User"].pop(selected_card_idx)
                                start_pos = get_target_positions("User", len(hands["User"])+1)[selected_card_idx]
                                game_state = "ANIMATING"
                                animated_discard_card = discarded
                                
                                def complete_discard(c=discarded):
                                    global game_state, game_phase, turn, animated_discard_card; 
                                    discard_pile.append(c); animated_discard_card = None; turn = "CPU 1"; game_phase = "DRAW"; game_state = "PLAYING"
                                active_animations = [AnimationEffect(discarded, start_pos, DISCARD_POS, duration=12, face_up=True, callback=complete_discard)]
                            selected_card_idx = 0
                            
            elif game_state == "SHOWDOWN":
                if event.key == pygame.K_SPACE:
                    setup_game()

    if game_state == "PLAYING" and winner_text == "" and turn != "User":
        current_cpu = turn
        top_discard = discard_pile[-1]
        cpu_ranks = [c[0] for c in hands[current_cpu]]
        
        from_discard = top_discard[0] in cpu_ranks or top_discard[0] == joker_card[0]
        drawn_card = discard_pile.pop() if from_discard else deck.pop()
        start_pt = DISCARD_POS if from_discard else DECK_POS
        
        targets = get_target_positions(current_cpu, 8)
        game_state = "ANIMATING"
        
        def cpu_finish_draw(cpu=current_cpu, card=drawn_card):
            global game_state
            hands[cpu].append(card)
            
            if evaluate_jutpatti_win(hands[cpu], joker_card):
                global winner_text; winner_text = f"{cpu} Wins Jutpatti!"
                game_state = "SHOWDOWN"
            else:
                cpu_hand = hands[cpu]
                choice = 0
                for idx, card_item in enumerate(cpu_hand):
                    if card_item[0] != joker_card[0] and [c[0] for c in cpu_hand].count(card_item[0]) == 1:
                        choice = idx
                        break
                discarded_card = hands[cpu].pop(choice)
                cpu_slots = get_target_positions(cpu, len(hands[cpu])+1)
                
                def cpu_finish_discard(dc=discarded_card, p=cpu):
                    global game_state, turn, game_phase, animated_discard_card
                    discard_pile.append(dc)
                    animated_discard_card = None
                    turn = "CPU 2" if p == "CPU 1" else "User"
                    game_phase = "DRAW"
                    game_state = "PLAYING"
                    
                game_state = "ANIMATING"
                global active_animations, animated_discard_card
                animated_discard_card = discarded_card
                active_animations = [AnimationEffect(discarded_card, cpu_slots[choice], DISCARD_POS, duration=12, face_up=False, callback=cpu_finish_discard)]
                
        active_animations = [AnimationEffect(drawn_card, start_pt, targets[7], duration=12, face_up=False, callback=cpu_finish_draw)]

    if game_state in ["DEALING", "ANIMATING"]:
        all_done = True
        for anim in active_animations:
            anim.update()
            if not anim.done:
                all_done = False
        
        for anim in active_animations:
            anim.draw(screen)
            
        if all_done:
            if game_state == "DEALING":
                game_state = "PLAYING"

    if game_state != "DEALING":
        if len(deck) > 0:
            draw_card(screen, DECK_POS[0], DECK_POS[1], (None, None), face_up=False)
        draw_card(screen, JOKER_POS[0], JOKER_POS[1], joker_card, face_up=True, is_joker=True)
        
        if len(discard_pile) > 0 and animated_discard_card is not discard_pile[-1]:
            draw_card(screen, DISCARD_POS[0], DISCARD_POS[1], discard_pile[-1], face_up=True)

    user_positions = get_target_positions("User", len(hands["User"]))
    for i, card in enumerate(hands["User"]):
        is_sel = (game_phase == "DISCARD" and i == selected_card_idx and turn == "User" and game_state == "PLAYING")
        is_j = (card[0] == joker_card[0])
        draw_card(screen, user_positions[i][0], user_positions[i][1], card, face_up=True, selected=is_sel, is_joker=is_j)
        
    cpu1_positions = get_target_positions("CPU 1", len(hands["CPU 1"]))
    for i, card in enumerate(hands["CPU 1"]):
        draw_card(screen, cpu1_positions[i][0], cpu1_positions[i][1], card, face_up=(game_state == "SHOWDOWN"), is_joker=(card[0] == joker_card[0]))
        
    cpu2_positions = get_target_positions("CPU 2", len(hands["CPU 2"]))
    for i, card in enumerate(hands["CPU 2"]):
        draw_card(screen, cpu2_positions[i][0], cpu2_positions[i][1], card, face_up=(game_state == "SHOWDOWN"), is_joker=(card[0] == joker_card[0]))

    screen.blit(FONT_MED.render("User (You)", True, COLOR_WHITE), (SCREEN_WIDTH // 2 - 45, SCREEN_HEIGHT - 210))
    screen.blit(FONT_SMALL.render("CPU 1", True, COLOR_WHITE), (30, SCREEN_HEIGHT // 2 - 80))
    screen.blit(FONT_SMALL.render("CPU 2", True, COLOR_WHITE), (SCREEN_WIDTH - 240, SCREEN_HEIGHT // 2 - 80))
    screen.blit(FONT_SMALL.render("Press [ESC] to Exit", True, COLOR_GRAY), (20, 20))

    if game_state == "DEALING":
        txt = FONT_MED.render("Dealing cards...", True, COLOR_GOLD)
        screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 60))
    elif winner_text == "":
        if turn == "User" and game_state == "PLAYING":
            msg = "Your Turn! [D] Deck Pile  |  [P] Pick Discard  |  [S] Sort Hand" if game_phase == "DRAW" else "Arrows to navigate  |  [SPACE] Discard selected card  |  [S] Sort Hand"
            txt = FONT_MED.render(msg, True, COLOR_GOLD)
            screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 60))
    else:
        win_txt = FONT_LARGE.render(winner_text, True, COLOR_GOLD)
        screen.blit(win_txt, (SCREEN_WIDTH // 2 - win_txt.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
        res_txt = FONT_SMALL.render("Press [SPACE] to start a new round", True, COLOR_WHITE)
        screen.blit(res_txt, (SCREEN_WIDTH // 2 - res_txt.get_width() // 2, SCREEN_HEIGHT // 2 + 140))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()