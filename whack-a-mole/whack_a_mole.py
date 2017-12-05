# Python 3.4.3 with Pygame
import pygame
import random
from queue import Empty

pygame.init()
pygame.display.set_caption('Whack a Mole')
pygame.mixer.music.load('Whack.wav')

# variables
screen = pygame.display.set_mode((800, 640))
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (165, 42, 42)

# This sets total number of CELLS in the grid where a mole can appear
CELLS = 9

# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 200
HEIGHT = 200
 
# This sets the margin between each cell
MARGIN = 5

# This sets time limit for the game (default to 60)
TIME_LIMIT = 60

# This sets start/end of game to GPIO
GAME_RUNNING = 0

class mole(pygame.sprite.Sprite):
    def __init__(self, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Mole.jpg').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

mole1 = mole([0, 0])

# Write Text
def _print_lable(lable, location):
    font = pygame.font.Font(None, 32)
    text1 = font.render(lable, 1, BLACK)
    screen.blit(text1, location)
    return

def _draw_grid_background():
    grid_cell_locations = _calc_cell_locations()
    for x, y in grid_cell_locations:
        pygame.draw.rect(screen,
                         WHITE,
                         [x,
                          y,
                          WIDTH,
                          HEIGHT])
    return

def _draw_grid_number():
    grid_cell_locations = _calc_cell_locations()
    for i, location in enumerate(grid_cell_locations):
        # cells are labeled 1 based
        _print_lable(str(i + 1), location)
    return

def _calc_cell_locations():
    return (_cell_location(_row(i), _column(i)) for i in range(1, CELLS + 1))

def _cell_location(row, column):
    return ((MARGIN + WIDTH) * column + MARGIN,
            (MARGIN + HEIGHT) * row + MARGIN)

def _row(cell_number):
    return (cell_number - 1) // 3

def _column(cell_number):
    return (cell_number - 1) % 3

def _score(current_score):
    new_score = current_score + 1
    pygame.mixer.music.play(0)
    return new_score    
    
def _draw_screen(randcell, score):

    _draw_grid_background()
    
    randx, randy = _cell_location(_row(randcell), _column(randcell))
    rectplace = pygame.draw.rect(screen, WHITE, (randx, randy, WIDTH, HEIGHT))
    screen.blit(mole1.image, (randx, randy))
    _draw_grid_number()
    
    _draw_score(score)
    return rectplace

def _pick_right_cell(key, randcell):
    return key == ord('0') + randcell
  
def _draw_score(score, location=(620, 5)):
    x, y = location
    pygame.draw.rect(screen, WHITE, (x, y, 175, 300))
    
    font = pygame.font.Font(None, 64)
    text_score_label = font.render("Score", 1, BLACK)
    screen.blit(text_score_label, (x, y))
    
    text_score = font.render(str(score).rjust(3), 1, BLACK)
    (_, height) = font.size("Score")
    y = y + height
    screen.blit(text_score, (x, y))
    return
    
def _draw_time_remaning(time_remaining, location=(620, 315)):
    x, y = location
    pygame.draw.rect(screen, WHITE, (x, y, 175, 300))
    
    font = pygame.font.Font(None, 64)
    text_time_label = font.render("Time", 1, BLACK)
    screen.blit(text_time_label, (x, y))
    
    str_time = str(time_remaining).rjust(3)
    if time_remaining < 0:
        str_time = "0"
    text_time = font.render(str_time, 1, BLACK)
    (_, height) = font.size("Time")
    y = y + height
    screen.blit(text_time, (x, y))
    return

def _random_cell():
    return random.randint(1, CELLS)

def _put_on_queue(q, data):
    if q:
        q.put(data)
    return

def _get_from_queue(q):
    if q:
        try:
            data = q.get(block=False)
            return data
        except Empty:
            # don't care if queue is empty, get it next time
            return None    
    return None

def _whacked(curr_randcell, curr_score, gpio_output_q):
    # notify GPIO to turn off light
    _put_on_queue(gpio_output_q, (curr_randcell, False))
    score = _score(curr_score)
    randcell = _random_cell()
    # notify GPIO to turn on light
    _put_on_queue(gpio_output_q, (randcell, True))
    rectplace = _draw_screen(randcell, score)
    return randcell, score, rectplace
  
# Main Loop
def _play_game(gpio_output_q, gpio_input_q):
    score = 0
    running = True
    
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    time_remaining = TIME_LIMIT
    
    randcell = _random_cell()
    screen.fill(BLACK)
    rectplace = _draw_screen(randcell, score)
    # notify GPIO to start of game
    _put_on_queue(gpio_output_q, (GAME_RUNNING, True))
    # notify GPIO to turn on light
    _put_on_queue(gpio_output_q, (randcell, True))
    _draw_time_remaning(time_remaining)
    pygame.display.flip()
    
    stopgame = False
    while running:      
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                stopgame = True            
            if event.type == pygame.KEYDOWN:
                if _pick_right_cell(event.key, randcell):
                    randcell, score, rectplace = _whacked(randcell, score, gpio_output_q)
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    stopgame = True
                
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos() 
                if rectplace.collidepoint(pos):
                    randcell, score, rectplace = _whacked(randcell, score, gpio_output_q)
          
            if event.type == pygame.USEREVENT:
                if time_remaining == 0:
                    # turn off timer
                    pygame.time.set_timer(pygame.USEREVENT, 0)
                    running = False
                time_remaining = time_remaining - 1
                _draw_time_remaning(time_remaining)
        
        # process GPIO input
        gpio_input = _get_from_queue(gpio_input_q)
        if gpio_input == randcell:
            randcell, score, rectplace = _whacked(gpio_input, score, gpio_output_q)
            
        pygame.display.update()
    
    print("Score was {}".format(score))
    # notify GPIO to end of game
    _put_on_queue(gpio_output_q, (GAME_RUNNING, False))
    return stopgame

def _start_game(gpio_input_q):
    (x, y, w, h) = pygame.draw.rect(screen, BLACK, (100, 200, 600, 200))
    (x, y, w, h) = pygame.draw.rect(screen, WHITE, (x + MARGIN, y + MARGIN, w - 2 * MARGIN, h - 2 * MARGIN))
    font = pygame.font.Font(None, 64)
    question = "Start game?"
    text_start_game = font.render(question, 1, BLACK)
    (q_w, _) = font.size(question)
    screen.blit(text_start_game, (x + (w - q_w) / 2, y))
    
    x = 250
    y = 300
    ans_yes = "Yes"
    text_yes = font.render(ans_yes, 1, BLACK)
    (w, h) = font.size(ans_yes)
    rectyes = pygame.draw.ellipse(screen, BROWN, [x, y, w, h])
    screen.blit(text_yes, (x, y))
    
    x = 500
    ans_no = "No"
    text_no = font.render(ans_no, 1, BLACK)
    (w, h) = font.size(ans_no)
    rectno = pygame.draw.ellipse(screen, BROWN, [x, y, w, h])
    screen.blit(text_no, (x, y))
    
    pygame.display.flip()
    
    done = False
    while not done: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False
                elif event.key == pygame.k_ESC:
                    return False
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos() 
                if rectyes.collidepoint(pos):
                    return True
                elif rectno.collidepoint(pos):
                    return False
        
        # process GPIO input
        gpio_input = _get_from_queue(gpio_input_q)
        if gpio_input == "Y":
            return True
        elif gpio_input == "N":
            return False
              
    return False

def run_whack_a_mole(gpio_output_q=None, gpio_input_q=None):
  
    playgame = _start_game(gpio_input_q)
    while playgame:
        stopgame = _play_game(gpio_output_q, gpio_input_q)
        if stopgame: 
            break
        playgame = _start_game(gpio_input_q)
               
    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()
    return
  
if __name__ == "__main__":
    run_whack_a_mole()
    
