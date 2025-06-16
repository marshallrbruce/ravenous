import pygame

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Ravenous") # Set the title of the window

CARD_WIDTH = 150
CARD_HEIGHT = 210
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50

# To create a surface the same size as your screen that supports transparency:
overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

# Create card zones (empty lists for now)
player_battlefield = []
enemy_battlefield = []
player_graveyard = []
enemy_graveyard = []

# Define battlefield slot coordinates (dictionaries)
player_battlefield_slots = {}
enemy_battlefield_slots = {}

targeting_mode = False
selected_attacker = None
turn_font = pygame.font.SysFont('Arial', 20)
current_turn = 'Player'

def end_player_turn():
    # Use 'global' to tell Python these are the global variables we want to modify
    global targeting_mode, selected_attacker, current_turn
    targeting_mode = False
    selected_attacker = None
    current_turn = 'Enemy'
    print("Player turn ended!") # Add a print statement for testing

# Constants for layout
HORIZONTAL_MARGIN = 50 # Space from left/right screen edges
VERTICAL_MARGIN_TOP = 75 # Space from top screen edge for enemy cards
VERTICAL_MARGIN_BOTTOM = 75 # Space from bottom screen edge for player cards
CARD_GAP_HORIZONTAL = 20 # Space between cards in a row
CARD_GAP_VERTICAL = 20 # Space between rows (if we add them)
BUTTON_ROW_GAP = 20

NUM_CARDS_PER_ROW = 5

# --- Player Melee Row (Bottom Half) ---
player_melee_row_y = SCREEN_HEIGHT - CARD_HEIGHT - VERTICAL_MARGIN_BOTTOM

# Calculate total width occupied by 5 cards and 4 gaps
total_row_width = (NUM_CARDS_PER_ROW * CARD_WIDTH) + \
                  ((NUM_CARDS_PER_ROW - 1) * CARD_GAP_HORIZONTAL)

# Calculate starting X to center the row
start_x_player_melee = (SCREEN_WIDTH - total_row_width) / 2

# Populate player_battlefield_slots for melee row
for i in range(NUM_CARDS_PER_ROW):
    slot_key = f"player_melee_{i:02d}" # Use f-string for "01", "02", etc.
    slot_x = start_x_player_melee + i * (CARD_WIDTH + CARD_GAP_HORIZONTAL)
    player_battlefield_slots[slot_key] = (slot_x, player_melee_row_y)

# --- Enemy Melee Row (Top Half) ---
enemy_melee_row_y = VERTICAL_MARGIN_TOP

# Calculate starting X for enemy row (can reuse total_row_width)
start_x_enemy_melee = (SCREEN_WIDTH - total_row_width) / 2

# Populate enemy_battlefield_slots for melee row
for i in range(NUM_CARDS_PER_ROW):
    slot_key = f"enemy_melee_{i:02d}" # Use f-string for "01", "02", etc.
    slot_x = start_x_enemy_melee + i * (CARD_WIDTH + CARD_GAP_HORIZONTAL)
    enemy_battlefield_slots[slot_key] = (slot_x, enemy_melee_row_y)

class Card:
    def __init__(self, name:str, attack:int, health:int, skill:str, image_path:str, x:int, y:int):
        self.name = name
        self.attack = attack
        self.health = health
        self.skill = skill
        self.image_path = image_path
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))
        self.x = x
        self.y = y
        self.exhausted = False

    def take_damage(self, damage_amount:int):
        self.health -= damage_amount
        print(f"{self.name} took {damage_amount} damage. Current HP: {self.health}")
        
    def deal_damage(self, target_card:'Card'):
        print(f"{self.name} attacks {target_card.name} for {self.attack} damage.")
        target_card.take_damage(self.attack)
        self.exhausted = True

    def draw(self, surface):
        # Render the card's image
        surface.blit(self.image, (self.x,self.y))
        font_obj = pygame.font.SysFont('Arial', 18)
        # Render the card's name
        font_card_name = font_obj.render(self.name, True, (255,0,0))
        x_pos = self.x + (CARD_WIDTH / 2) - (font_card_name.get_width() / 2)
        surface.blit(font_card_name, (x_pos, self.y +5))
        # Render the card's stats
        font_card_attack = font_obj.render(str(self.attack), True, (255,0,0))
        surface.blit(font_card_attack, (self.x +5, self.y +190))
        font_card_hp = font_obj.render(str(self.health), True, (255,0,0))
        surface.blit(font_card_hp, (self.x +125, self.y +190))
        # Skill text-wrapping and rendering lines of skill text
        skill_font = pygame.font.SysFont('Arial', 13)
        max_skill_width = CARD_WIDTH - 10
        start_y_for_skill = self.y + 135
        wrapped_lines = []
        words = self.skill.split(' ')
        current_line = ""
        for word in words:
            # Check if adding the next word exceeds max_skill_width
            if skill_font.size(current_line + " " + word)[0] <= max_skill_width:
                # If it fits, add it to the current line (handle first word no space)
                if current_line == "":
                    current_line = word
                else:
                    current_line += " " + word
            else:
                # If it doesn't fit, add the current line to wrapped_lines
                wrapped_lines.append(current_line)
                # Start a new line with the current word
                current_line = word
        # Add the last line after the loop finishes
        wrapped_lines.append(current_line)
        # Blit each line of skill text to surface
        line_height = skill_font.get_linesize() # Get the height of a single line of text
        for i, line in enumerate(wrapped_lines):
            # Render the individual line
            rendered_line = skill_font.render(line, True, (255, 0, 0)) # Red text for skill
            # Calculate x position (you might want to center or left-align this)
            # For now, let's left-align with 5px padding:
            line_x_pos = self.x + 5
            # Calculate y position for this line
            line_y_pos = start_y_for_skill + (i * line_height)
            surface.blit(rendered_line, (line_x_pos, line_y_pos))
        if self.exhausted == True:
            exhaust_overlay = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
            exhaust_overlay.fill((100, 100, 100, 128))
            surface.blit(exhaust_overlay, (self.x, self.y))

    def handle_event(self, event):
        clicked = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            card_cord = self.image.get_rect(topleft=(self.x, self.y))
            if card_cord.collidepoint(event.pos):
                clicked = True
        return clicked
    
class Button:
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, # What the button says
                 font: pygame.font.Font, # The actual Pygame font object
                 text_color: tuple, # E.g., (0, 0, 0) for black
                 button_color: tuple, # E.g., (255, 255, 255) for white
                 action=None): # The function to call when clicked
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.text_color = text_color
        self.button_color = button_color
        self.action = action
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        # 1. Draw the button's background rectangle
        pygame.draw.rect(surface, self.button_color, self.rect)

        # 2. Render the button's text
        # Use self.font and pass the text string, antialias=True, and self.text_color
        text_surface = self.font.render(self.text, True, self.text_color)

        # 3. Get the rectangle of the rendered text surface
        text_rect = text_surface.get_rect()

        # 4. Center the text_rect on the button's self.rect
        text_rect.center = self.rect.center

        # 5. Blit the text surface onto the screen at its calculated position
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        # We only care about mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the mouse click position (event.pos) is inside the button's rectangle
            if self.rect.collidepoint(event.pos):
                # If there's an action function assigned to this button, call it!
                if self.action: # Make sure action is not None
                    self.action()
                return True # Indicate that the button was clicked
        return False # No click on this button, or not a MOUSEBUTTONDOWN event

# Get coordinates for Merry (Player's first melee slot)
player_merry_x, player_merry_y = player_battlefield_slots["player_melee_00"]
player_merry_card = Card(
    "Merry",
    1,
    10,
    "Sleep: recover 2 HP",
    "/home/marshimoto/programming/game dev/ravenous/assets/merry.jpeg",
    player_merry_x, # Use the retrieved x coordinate
    player_merry_y  # Use the retrieved y coordinate
)

# Get coordinates for Eowyn (Player's second melee slot)
player_eowyn_x, player_eowyn_y = player_battlefield_slots["player_melee_01"]
player_eowyn_card = Card(
    "Eowyn",
    5,
    3,
    "Whirling Dervish: Eowyn gains an extra attack at half its current damage",
    "/home/marshimoto/programming/game dev/ravenous/assets/eowyn.jpeg",
    player_eowyn_x, # Use the retrieved x coordinate
    player_eowyn_y  # Use the retrieved y coordinate
)

# Get coordinates for Eowyn (Enemy's first melee slot)
enemy_eowyn_x, enemy_eowyn_y = enemy_battlefield_slots["enemy_melee_00"]
enemy_eowyn_card = Card(
    "Eowyn",
    5,
    3,
    "Whirling Dervish: Eowyn gains an extra attack at half its current damage",
    "/home/marshimoto/programming/game dev/ravenous/assets/eowyn.jpeg",
    enemy_eowyn_x, # Use the retrieved x coordinate
    enemy_eowyn_y  # Use the retrieved y coordinate
)

# Get coordinates for Eowyn (Enemy's first melee slot)
enemy_merry_x, enemy_merry_y = enemy_battlefield_slots["enemy_melee_01"]
enemy_merry_card = Card(
    "Merry",
    1,
    10,
    "Sleep: recover 2 HP",
    "/home/marshimoto/programming/game dev/ravenous/assets/merry.jpeg",
    enemy_merry_x, # Use the retrieved x coordinate
    enemy_merry_y  # Use the retrieved y coordinate
)

end_turn_font = pygame.font.SysFont('Arial', 24, bold=True)
end_turn_button = Button((SCREEN_WIDTH - HORIZONTAL_MARGIN - BUTTON_WIDTH), (player_melee_row_y + CARD_HEIGHT + BUTTON_ROW_GAP), BUTTON_WIDTH, BUTTON_HEIGHT, 'END TURN', end_turn_font, (0,0,0), button_color=(255,255,255), action=end_player_turn)


player_battlefield = [player_eowyn_card, player_merry_card]
enemy_battlefield = [enemy_eowyn_card, enemy_merry_card]

game_over = False
win_status = None
running = True

while running:
    # Event Handling Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over == False:
            # Handle button clicks BEFORE card clicks to prevent accidental card selection
            if end_turn_button.handle_event(event):
            # If the button was clicked, its action (end_player_turn) already ran.
            # We can skip the rest of the event loop for this frame if needed,
            # or just let it continue. For now, a 'pass' is fine.
                pass    
            if current_turn == 'Player':
                if targeting_mode == False:
                    for card in player_battlefield:
                        if card.handle_event(event): # This calls the method and checks if it returned True
                            if card.exhausted == False:
                                print(f"{card.name} card selected!")
                                targeting_mode = True
                                selected_attacker = card
                elif targeting_mode == True:
                    for card in enemy_battlefield:
                        if card.handle_event(event): # This calls the method and checks if it returned True
                            print(f"{card.name} card attacked!")    
                            targeting_mode = False
                            selected_attacker.deal_damage(target_card=card)
    
    # Process Player Battlefield
    cards_to_keep_player = []
    for card in player_battlefield:
        if card.health <= 0:
            print(f"{card.name} has been defeated and moved to graveyard!")
            player_graveyard.append(card)
            # DO NOT call card.draw(screen) for defeated cards
        else:
            cards_to_keep_player.append(card)
    player_battlefield = cards_to_keep_player # Update the battlefield list
    
    # Process Enemy Battlefield (apply the same logic)
    cards_to_keep_enemy = []
    for card in enemy_battlefield:
        if card.health <= 0:
            print(f"{card.name} has been defeated and moved to graveyard!")
            enemy_graveyard.append(card)
            # DO NOT call card.draw(screen) for defeated cards
        else:
            cards_to_keep_enemy.append(card)
    enemy_battlefield = cards_to_keep_enemy # Update the battlefield list
    
    if not cards_to_keep_enemy and cards_to_keep_player == []:
        game_over = True
        win_status="Draw!"
    elif cards_to_keep_enemy == []:
        game_over = True
        win_status = "Victory!"
    elif cards_to_keep_player == []:
        game_over = True
        win_status = "Defeat!"

    if current_turn == 'Enemy':
        if player_battlefield and enemy_battlefield:
            enemy_battlefield[0].deal_damage(player_battlefield[0])
            print("Enemy turn ended!")
            current_turn = 'Player'

            for card in player_battlefield:
                if card.exhausted == True:
                    card.exhausted = False
            for card in enemy_battlefield:
                if card.exhausted == True:
                    card.exhausted = False

    # --- Drawing (Rendering) ---
    screen.fill((0, 0, 0)) # Black background

    for index, card in enumerate(player_battlefield):
        slot_key = f"player_melee_{index:02d}"
        new_x, new_y = player_battlefield_slots[slot_key]
        card.x = new_x
        card.y = new_y
        card.draw(screen) # Only draw living cards
    for index, card in enumerate(enemy_battlefield):
        slot_key = f"enemy_melee_{index:02d}"
        new_x, new_y = enemy_battlefield_slots[slot_key]
        card.x = new_x
        card.y = new_y
        card.draw(screen) # Only draw living cards
    
    end_turn_button.draw(screen)

    if game_over:
        overlay_surface.fill((0, 0, 0, 185)) # Example: black with 50% transparency
        font_obj = pygame.font.SysFont('Arial', 50)
        win_status_font = font_obj.render(win_status, True, (255,0,0))
        x = (SCREEN_WIDTH / 2) - (win_status_font.get_width() / 2)
        y = (SCREEN_HEIGHT / 2) - (win_status_font.get_height() / 2)
        overlay_surface.blit(win_status_font, (x, y))
        screen.blit(overlay_surface, (0, 0))
    else:
        font_obj = pygame.font.SysFont('Arial', 30) # Choose a font and size
        text_color = (255, 255, 255) # White color
        text_surface = font_obj.render(f"Current Turn: {current_turn}", True, text_color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50)) # Center at top
        screen.blit(text_surface, text_rect)

    # Update the display
    pygame.display.flip() # Or pygame.display.update()

# Quit Pygame
pygame.quit()