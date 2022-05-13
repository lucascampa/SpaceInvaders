#!/usr/bin/env python
# coding: utf-8

# In[2]:


import sys
import random
import json
import pygame
from pygame import mixer

pygame.init()

# Window size
screen = pygame.display.set_mode((800, 600))
screen_rect = screen.get_rect()

# Sets the title and the icon displayed on the window
pygame.display.set_caption('Space Invaders')
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Game background
background = pygame.image.load('background.png').convert()

FONT_FILE = 'Retro Gaming.ttf'

MENU_BACKGROUND = (0, 0, 0, 127.5)
WHITE = (255, 255, 255)
GREY = (210, 210, 210)

difficulty = ['EASY', 'MEDIUM', 'HARD']
switch = ['OFF', 'ON']

# Looks for the save file. If it doesn't find it, creates one with both
# sound and music off and with the medium difficulty set by default
try:
    with open('save_file.json') as f:
        save_dict = json.load(f)
except FileNotFoundError:
    # The save file is a JSON file created from a dict that stores
    # settings and gameplay statistics
    save_dict = {
            "difficulty": "1",
            "sound": False,
            "music": False,
            "stats": {
                "0": {
                    "max score": 0,
                    "bullets shot": 0,
                    "enemies killed": 0,
                    "bottom": 300,
                    "player dx": 3,
                    "enemy dx": 1,
                    "enemy dy": 5
                },
                "1": {
                    "max score": 0,
                    "bullets shot": 0,
                    "enemies killed": 0,
                    "bottom": 300,
                    "player dx": 3,
                    "enemy dx": 1,
                    "enemy dy": 10
                },
                "2": {
                    "max score": 0,
                    "bullets shot": 0,
                    "enemies killed": 0,
                    "bottom": 450,
                    "player dx": 2.5,
                    "enemy dx": 1.5,
                    "enemy dy": 15
                },
                "matches": 0,
                "total playtime": 0
            }
        }
    save_json = json.dumps(save_dict)
    with open('save_file.json', 'w') as f:
        f.write(save_json)

# Settings that can be changed
dif_set = save_dict['difficulty']
sound_set = save_dict['sound']
music_set = save_dict['music']

# Variables to track the playtime
checkpoint = 0
elapsed = 0

# Sound
mixer.music.load('background.wav')
bullet_sound = mixer.Sound('laser.wav')
collision_sound = mixer.Sound('explosion.wav')

if sound_set:
    bullet_sound.set_volume(.0175)
    collision_sound.set_volume(.0175)
else:
    bullet_sound.set_volume(0)
    collision_sound.set_volume(0)
    
if music_set and sound_set:
    mixer.music.play(-1)
    mixer.music.set_volume(.0175)
else:
    mixer.music.stop()
    
# Classes
class Player(pygame.sprite.Sprite):
    """PLAYER icon.
    
    Sprite to render the player and update its position.
    
    Methods:
    - __init__()
    - update()"""
    
    def __init__(self):
        """Initiates the sprite."""
        
        pygame.sprite.Sprite.__init__(self)
        
        # Icon
        self.image = pygame.image.load('player.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.midbottom = screen_rect.midbottom
        
        # Speed
        self.dx = 0

    def update(self):
        """Updates the PLAYER icon."""
        
        # Moves the player
        self.rect.move_ip(self.dx, 0)
        
        # Left and right boundaries of the screen
        if self.rect.left < screen_rect.left:
            self.rect.left = screen_rect.left
        elif self.rect.right > screen_rect.right:
            self.rect.right = screen_rect.right
        
        # Game over if an enemy touches the player
        for enemy in enemies:
            if pygame.Rect.colliderect(self.rect, enemy.rect):
                bullet.shot = False
                global elapsed
                elapsed = pygame.time.get_ticks() - checkpoint
                max_score = save_dict['stats'][dif_set]['max score']
                if score.value > max_score:
                    save_dict['stats'][dif_set]['max score'] = score.value
                game_over.update()


class Bullet(pygame.sprite.Sprite):
    """BULLET icon.
    
    Sprite to render a bullet and update its position.
    
    Methods:
    - __init__()
    - update()
    - shoot()"""
    
    def __init__(self):
        """Initiates the sprite."""
        
        pygame.sprite.Sprite.__init__(self)
        
        # Icon
        self.image = pygame.image.load('bullet.png').convert_alpha()
        self.rect = self.image.get_rect()
        
        # Boolean to determine whether the bullet is in movement
        self.shot = False
        
        # Speed
        self.dy = -2.5
    
    def shoot(self):
        """Shoots the bullet.
        
        - Plays the sound of the bullet being shot
        - Blits the bullet to the screen
        - +1 to the 'bullets shot' list in the save dict"""
        
        bullet_sound.play()
        self.shot = True
        self.rect.midbottom = player.rect.midtop
        render_sprites.add(self)
        save_dict['stats'][dif_set]['bullets shot'] += 1
        
    def update(self):
        """Updates the BULLET icon."""
        
        # Checks if the shot attribute is True to keep the bullet moving
        if self.shot:
            self.rect.move_ip(0, self.dy)
            
            # Resets the bullet state upon reaching the top of the screen
            if self.rect.bottom < screen_rect.top:
                self.shot = False
                self.kill()
            
            # If the bullet hits an enemy, removes both from the screen,
            # creates a new enemy and updates the score
            for enemy in enemies:
                if pygame.Rect.colliderect(self.rect, enemy.rect):
                    collision_sound.play()
                    self.kill()
                    enemy.kill()
                    del enemy
                    new_enemy = Enemy()
                    render_sprites.add(new_enemy)
                    score.value += 1
                    save_dict['stats'][dif_set]['enemies killed'] += 1
                    self.shot = False

                    
class Enemy(pygame.sprite.Sprite):
    """ENEMY icon.
    
    Sprite to render an enemy and update its position.
    
    Methods:
    - __init__()
    - update()"""
    
    def __init__(self):
        """Initiates the sprite."""
        
        pygame.sprite.Sprite.__init__(self)
        
        # Icon
        self.image = pygame.image.load('enemy.png').convert_alpha()
        self.rect = self.image.get_rect()
        
        # The enemy's initial coordinates are randomly generated according to the difficulty set
        bottom = save_dict['stats'][dif_set]['bottom']
        self.rect.topleft = (random.randint(0, 736), random.randint(64, bottom))
        
        # Horizontal and vertical speeds
        self.dx = save_dict['stats'][dif_set]['enemy dx']
        self.dy = 0
        
        # Whenever a new enemy is initiated, it is automatically added to the enemies sprite group
        self.add(enemies)
        
    def update(self):
        """Updates the ENEMY icon."""
        
         # Automatically moves the enemy
        self.rect.move_ip(self.dx, self.dy)
        
        # Makes the enemy move in the other direction and go down when
        # it reaches either side of the screen
        if self.rect.left <= screen_rect.left:
            self.rect.left = screen_rect.left
            self.dx *= -1
            self.dy = save_dict['stats'][dif_set]['enemy dy']
        elif self.rect.right >= screen_rect.right:
            self.rect.right = screen_rect.right
            self.dx *= -1
            self.dy = save_dict['stats'][dif_set]['enemy dy']
        else:
            self.dy = 0
        

class Score(pygame.sprite.Sprite):
    """SCORE.
    
    Sprite to render and update the score.
    
    Methods:
    - __init__()
    - update()"""
        
    def __init__(self):
        """Initiates the sprite."""
        
        pygame.sprite.Sprite.__init__(self)
        
        # Value
        self.font = pygame.font.Font(FONT_FILE, 32)
        self.value = 0
        self.image = self.font.render(str(self.value), True, WHITE)
        self.rect = self.image.get_rect()
        self.rect.top = screen_rect.top
        self.rect.right = screen_rect.right - 25

    def update(self):
        """Updates the SCORE display."""
        
        self.image = self.font.render(str(self.value), True, WHITE)

        # Adjusts the rect to the text size 
        width, height = self.font.size(str(self.value))
        left = self.rect.right - width
        self.rect.update(left, self.rect.top, width, self.rect.height)

        # The maximum possible score is 1 trillion, then game over
        if self.value >= 1_000_000_000_000:
            self.value = 1_000_000_000_000
            global elapsed
            elapsed = pygame.time.get_ticks() - checkpoint
            save_dict['stats'][dif_set]['max score'] = self.value
            game_over.update()


class HomeScreen(pygame.sprite.Sprite):
    """HOME screen.
    
    The home screen of the game. Contains a button to start the
    gameplay and another to the settings screen.
    
    Methods:
    - __init__()
    - mouse_position()
    - update()
    - click()"""
    
    def __init__(self):
        """Initiates the sprite."""
        
        pygame.sprite.Sprite.__init__(self)
        
        # Menu background
        self.image = pygame.Surface((760, 570), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = screen_rect.center

        # Title text
        title_font = pygame.font.Font(FONT_FILE, 64)
        title_surface = title_font.render('SPACE INVADERS', True, WHITE)
        self.title_rect = title_surface.get_rect()
        self.title_rect.centerx = self.rect.centerx - self.rect.left
        self.title_rect.centery = self.rect.centery - self.rect.top
        
        # Dict that stores what is blitted onto the screen and each button's coordinates
        # The title coordinates aren't stored because they are never used
        self.buttons = {'blits': [(title_surface, self.title_rect)]}  # Blits: 0

        self.button_font = pygame.font.Font(FONT_FILE, 24)

        # Start game blinking button
        self.START_GAME = 'CLICK  OR  PRESS  ENTER  TO  START'
        self.start_text = self.button_font.render(self.START_GAME, True, GREY)
        self.start_rect = self.start_text.get_rect()
        self.start_rect.top = self.title_rect.bottom + 10
        self.start_rect.centerx = self.title_rect.centerx
        self.no_text = pygame.Surface(self.start_rect.size, pygame.SRCALPHA)
        self.no_text.fill((0, 0, 0, 0))
        self.buttons['blits'].append((self.start_text, self.start_rect))  # Blits: 1
        self.buttons['x'] = [range(139, 662)]  # x: 0
        self.buttons['y'] = [range(354, 378)]  # y: 0
        self.start_index = False  # Boolean that switches whenever the text blinks
        self.last = pygame.time.get_ticks()  # Last time the text blinks
        self.cooldown = 400  # Blink interval

        # Settings button
        set_surface = self.button_font.render('SETTINGS', True, GREY)
        set_rect = set_surface.get_rect()
        set_rect.midtop = self.start_rect.midbottom
        self.buttons['blits'].append((set_surface, set_rect))  # Blits: 2
        self.buttons['x'].append(range(329, 472))  # x: 1
        self.buttons['y'].append(range(384, 408))  # y: 1

        self.image.fill(MENU_BACKGROUND)
        self.image.blits(self.buttons['blits'])
        
        # Whenever this file is opened, this is the first sprite that is blitted to the screen
        self.add(render_sprites)
        
        # Difficulty set for the current match
        self.difficulty = dif_set
        
        # Boolean to determine whether the gameplay has started
        self.game_start = False

    def mouse_position(self):
        """Stores the mouse position and checks if it's over a button.
        
        Gets the x and y coordinates of the mouse and checks if they
        coincide with any of the buttons' coordinates, which are stored
        in the buttons dict."""
        
        x, y = pygame.mouse.get_pos()

        start_x = x in self.buttons['x'][0]
        start_y = y in self.buttons['y'][0]
        self.start = start_x and start_y

        settings_x = x in self.buttons['x'][1]
        settings_y = y in self.buttons['y'][1]
        self.settings_button = settings_x and settings_y
    
    def update(self):
        """Updates the HOME screen.
        
        - Checks if a game has started
        - Highlights a button when the mouse is over it
        - Makes the start button text blink"""
        
        # If a game starts, resets gameplay variables and counts a new match
        if self.game_start:
            self.kill()
            score.value = 0
            pause.paused = False
            global checkpoint, elapsed
            elapsed = 0
            checkpoint = pygame.time.get_ticks()
            save_dict['stats']['matches'] += 1
            self.difficulty = dif_set
        else:
            # New game started by pressing ENTER
            if pygame.key.get_pressed()[pygame.K_RETURN]:
                self.game_start = True
                for _ in range(6): Enemy()  # Generates 6 enemies
                render_sprites.add(player, enemies, score)
                
            # Highlights a button when the mouse hovers over it
            self.mouse_position()
        
            mouse_over = False
            
            start_text = self.start_text
        
            if self.start:
                mouse_over = True
                i = 1
                image = self.button_font.render(self.START_GAME, True, WHITE)
                start_text = image
                rect = self.start_rect
            elif self.settings_button:
                mouse_over = True
                i = 2
                image = self.button_font.render('SETTINGS', True, WHITE)
                rect = image.get_rect()
                rect.midtop = self.start_rect.midbottom
            
            # Makes the text blink by switching the start_index attribute
            now = pygame.time.get_ticks()
            if (now - self.last) >= self.cooldown:
                self.start_index = not self.start_index
                self.last = pygame.time.get_ticks()
            else:
                self.start_index = self.start_index
            
            # Updates the buttons dict with the text or the blank image
            j = self.start_index
            start_surfaces = [start_text, self.no_text]
            self.buttons['blits'][1] = (start_surfaces[j], self.start_rect)
            
            # If the mouse is over a button, uses a new list of blits
            # that is identical to the buttons dict's, except for the
            # highlighted button
            if mouse_over:
                # Since the start game button has a blinking text, this
                # makes sure that whenever the text is on and the mouse
                # is over it, it is highlighted
                if i == 1:
                    image = start_surfaces[j] 
                    
                new_blits = self.buttons['blits'][:]
                new_blits[i] = (image, rect)
                new_blits[:i] = self.buttons['blits'][:i]
                new_blits[i+1:] = self.buttons['blits'][i+1:]
                self.image.fill(MENU_BACKGROUND)
                self.image.blits(new_blits)
            else:
                # If the mouse is not over any button, uses the regular blits
                self.image.fill(MENU_BACKGROUND)
                self.image.blits(self.buttons['blits'])
            
                
    def click(self):
        """Click event handler."""
        
        self.mouse_position()
        
        # Starts the game or goes to the settings menu when the respective button is clicked
        if self.start:
            self.game_start = True
            for _ in range(6): Enemy()  # Generates 6 enemies
            render_sprites.add(player, enemies, score)
        elif self.settings_button:
            settings.previous_screen.add(self)
            render_sprites.empty()
            render_sprites.add(settings)


class Settings(pygame.sprite.Sprite):
    """SETTINGS screen.
    
    Screen that allows the player to set the sound, music and
    difficulty and to see the controls and gameplay statistics.
    
    Methods:
    - __init__()
    - mouse_position()
    - update()
    - click()"""
    
    def __init__(self):
        """Initiates the sprite."""
        
        pygame.sprite.Sprite.__init__(self)
        
        # Menu background
        self.image = pygame.Surface((760, 570), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = screen_rect.center
        self.rect.centerx = screen_rect.centerx
        
        # Sprite group that stores the previous screen. That is, the
        # screen where a settings button was pressed, opening this screen
        self.previous_screen = pygame.sprite.Group()
        
        # Title
        self.title_font = pygame.font.Font(FONT_FILE, 44)
        title_surface = self.title_font.render('SETTINGS', True, WHITE)
        title_rect = title_surface.get_rect()
        title_rect.midtop = self.rect.midtop
        
        # Dict that stores what is blitted onto the screen and each button's coordinates
        # The title coordinates aren't stored because they are never used
        self.buttons = {'blits': [(title_surface, title_rect)]} # Blits: 0
        
        # Button to go back to the previous screen
        back_surface = self.title_font.render('<<', True, GREY)
        back_rect = back_surface.get_rect()
        back_rect.topleft = self.rect.topleft
        self.buttons['blits'].append((back_surface, back_rect)) # Blits: 1
        self.buttons['x'] = [range(42, 91)] # x: 0
        self.buttons['y']= [range(43, 75)] # y: 0
        
        self.button_font = pygame.font.Font(FONT_FILE, 36)
        
        # Sound on/off button
        sound_surface = self.button_font.render('SOUND ', True, WHITE)
        self.sound_rect = sound_surface.get_rect()
        self.sound_rect.left = self.rect.left
        self.sound_rect.bottom = self.rect.centery - self.rect.top
        self.buttons['blits'].append((sound_surface, self.sound_rect)) # Blits: 2
        
        switch_surface = self.button_font.render(switch[sound_set], True, GREY)
        switch_rect = switch_surface.get_rect()
        switch_rect.topleft = self.sound_rect.topright
        self.buttons['blits'].append((switch_surface, switch_rect)) # Blits: 3
        self.buttons['x'].extend([range(194, 248), range(194, 275)]) # x: 1, 2
        self.buttons['y'].append(range(259, 292)) # y: 1
        
        # Controls button
        ctrl_surface = self.button_font.render('CONTROLS', True, GREY)
        ctrl_rect = ctrl_surface.get_rect()
        ctrl_rect.left = self.rect.left
        ctrl_rect.bottom = self.sound_rect.top - 5
        self.buttons['blits'].append((ctrl_surface, ctrl_rect)) # Blits: 4
        self.buttons['x'].append(range(39, 259)) # x: 3
        self.buttons['y'].append(range(209, 242)) # y: 2
        
        # Music on/off button
        music_surface = self.button_font.render('MUSIC ', True, WHITE)
        self.music_rect = music_surface.get_rect()
        self.music_rect.left = self.rect.left
        self.music_rect.top = self.sound_rect.bottom + 5
        self.buttons['blits'].append((music_surface, self.music_rect)) # Blit: 5
        
        switch_surface = self.button_font.render(switch[music_set], True, GREY)
        switch_rect = switch_surface.get_rect()
        switch_rect.topleft = self.music_rect.topright
        self.buttons['blits'].append((switch_surface, switch_rect)) # Blits: 6
        self.buttons['x'].extend([range(191, 245), range(191, 272)]) # x: 4, 5
        self.buttons['y'].append(range(309, 342)) # y: 3
        
        # Difficulty button
        dif_surface = self.button_font.render('DIFFICULTY ', True, WHITE)
        self.dif_rect = dif_surface.get_rect()
        self.dif_rect.left = self.rect.left
        self.dif_rect.top = self.music_rect.bottom + 5
        self.buttons['blits'].append((dif_surface, self.dif_rect)) # Blits: 7
        
        switch_surface = self.button_font.render(difficulty[int(dif_set)], True, GREY)
        switch_rect = switch_surface.get_rect()
        switch_rect.topleft = self.dif_rect.topright
        self.buttons['blits'].append((switch_surface, switch_rect)) # BLits: 8
        self.buttons['x'].extend([range(323, 487), range(323, 433)]) # x: 6, 7
        self.buttons['y'].append(range(359, 392)) # y: 4
        
        # Statistics button
        stats_surface = self.button_font.render('STATISTICS', True, GREY)
        stats_rect = stats_surface.get_rect()
        stats_rect.left = self.rect.left
        stats_rect.top = self.dif_rect.bottom + 5
        self.buttons['blits'].append((stats_surface, stats_rect)) # Blits: 9
        self.buttons['x'].append(range(39, 313)) # x: 8
        self.buttons['y'].append(range(409, 442)) # y: 5
        
        self.image.fill(MENU_BACKGROUND)
        self.image.blits(self.buttons['blits'])
    
    def mouse_position(self):
        """Stores the mouse position and checks if it's over a button.
        
        Gets the x and y coordinates of the mouse and checks if they
        coincide with any of the buttons' coordinates, which are stored
        in the buttons dict."""
        
        x, y = pygame.mouse.get_pos()
        
        back_x = x in self.buttons['x'][0]
        back_y = y in self.buttons['y'][0]
        self.back = back_x and back_y
        
        controls_x = x in self.buttons['x'][3]
        controls_y = y in self.buttons['y'][2]
        self.controls = controls_x and controls_y
        
        sound_on_x = x in self.buttons['x'][1]
        sound_on_y = y in self.buttons['y'][1]
        self.sound_on = sound_on_x and sound_on_y and sound_set
        
        sound_off_x = x in self.buttons['x'][2]
        sound_off_y = y in self.buttons['y'][1]
        self.sound_off = sound_off_x and sound_off_y and not sound_set
        
        music_on_x = x in self.buttons['x'][4]
        music_on_y = y in self.buttons['y'][3]
        self.music_on = music_on_x and music_on_y and music_set
        
        music_off_x = x in self.buttons['x'][5]
        music_off_y = y in self.buttons['y'][3]
        self.music_off = music_off_x and music_off_y and not music_set
        
        easy_dif_x = x in self.buttons['x'][6]
        easy_dif_y = y in self.buttons['y'][4]
        self.easy_dif = easy_dif_x and easy_dif_y and dif_set == "0"
        
        medium_dif_x = x in self.buttons['x'][7]
        medium_dif_y = y in self.buttons['y'][4]
        self.medium_dif = medium_dif_x and medium_dif_y and dif_set == "1"
        
        hard_dif_x = x in self.buttons['x'][6]
        hard_dif_y = y in self.buttons['y'][4]
        self.hard_dif = hard_dif_x and hard_dif_y and dif_set == "2"
        
        stats_x = x in self.buttons['x'][8]
        stats_y = y in self.buttons['y'][5]
        self.statistics = stats_x and stats_y
        
    def update(self):
        """Updates the SETTINGS screen.
        
        Highlights a button when the mouse is over it."""
        
        self.mouse_position()
        
        mouse_over = False
        
        if self.back:
            mouse_over = True
            i = 1
            image = self.title_font.render('<<', True, WHITE)
            rect = image.get_rect()
            rect.topleft = self.rect.topleft
        elif self.controls:
            mouse_over = True
            i = 4
            image = self.button_font.render('CONTROLS', True, WHITE)
            rect = image.get_rect()
            rect.left = self.rect.left
            rect.bottom = self.sound_rect.top - 5
        elif self.sound_on:
            mouse_over = True
            i = 3
            image = self.button_font.render('ON', True, WHITE)
            rect = image.get_rect()
            rect.topleft = self.sound_rect.topright
        elif self.sound_off:
            mouse_over = True
            i = 3
            image = self.button_font.render('OFF', True, WHITE)
            rect = image.get_rect()
            rect.topleft = self.sound_rect.topright
        elif self.music_on:
            mouse_over = True
            i = 6
            image = self.button_font.render('ON', True, WHITE)
            rect = image.get_rect()
            rect.topleft = self.music_rect.topright
        elif self.music_off:
            mouse_over = True
            i = 6
            image = self.button_font.render('OFF', True, WHITE)
            rect = image.get_rect()
            rect.topleft = self.music_rect.topright
        elif self.easy_dif:
            mouse_over = True
            i = 8
            image = self.button_font.render('EASY', True, WHITE)
            rect = image.get_rect()
            rect.topleft = self.dif_rect.topright
        elif self.medium_dif:
            mouse_over = True
            i = 8
            image = self.button_font.render('MEDIUM', True, WHITE)
            rect = image.get_rect()
            rect.topleft = self.dif_rect.topright
        elif self.hard_dif:
            mouse_over = True
            i = 8
            image = self.button_font.render('HARD', True, WHITE)
            rect = image.get_rect()
            rect.topleft = self.dif_rect.topright
        elif self.statistics:
            mouse_over = True
            i = 9
            image = self.button_font.render('STATISTICS', True, WHITE)
            rect = image.get_rect()
            rect.left = self.rect.left
            rect.top = self.dif_rect.bottom + 5
            
        if mouse_over:
            # If the mouse is over a button, uses a new list of blits
            # that is identical to the buttons dict's, except for the
            # highlighted button
            new_blits = self.buttons['blits'][:]
            new_blits[i] = (image, rect)
            new_blits[:i] = self.buttons['blits'][:i]
            new_blits[i+1:] = self.buttons['blits'][i+1:]
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(new_blits)
        else:
            # Otherwise, uses the regular blits
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(self.buttons['blits'])
        
    def click(self):
        """Click event handler.
        
        Executes one the following actions according to the button
        pressed:
         - Goes back to the previous screen
         - Goes to the controls screen
         - Sets the sound from on to off and vice-versa
         - Sets the music from on to off and vice-versa
         - Sets the difficulty to easy, medium or hard
         - Goes to the statistics screen."""
        
        global sound_set, music_set, dif_set
        
        self.mouse_position()
        
        button_click = False
        
        if self.back:
            render_sprites.empty()
            if pause.paused:
                self.previous_screen.empty()
                # Asks if the player is sure about changing the
                # difficulty with a running gameplay currently paused,
                # in case it was accidental
                if home_screen.difficulty != dif_set:
                    self.previous_screen.add(change_difficulty)
                else:
                    self.previous_screen.add(pause)
            render_sprites.add(self.previous_screen)
            self.previous_screen.empty()
        elif self.sound_on:
            sound_set = not sound_set
            bullet_sound.set_volume(0)
            collision_sound.set_volume(0)
            # Turns the music off as well
            if music_set:
                mixer.music.stop()
                img = self.button_font.render('OFF', True, GREY)
                rct = img.get_rect()
                rct.topleft = self.music_rect.topright
                self.buttons['blits'][6] = (img, rct)
                save_dict['music'] = music_set = False
            button_click = True
            i = 3
            image = self.button_font.render('OFF', True, GREY)
            rect = image.get_rect()
            rect.topleft = self.sound_rect.topright
            save_dict['sound'] = sound_set
        elif self.sound_off:
            sound_set = not sound_set
            bullet_sound.set_volume(.0175)
            collision_sound.set_volume(.0175)
            button_click = True
            i = 3
            image = self.button_font.render('ON', True, GREY)
            rect = image.get_rect()
            rect.topleft = self.sound_rect.topright
            save_dict['sound'] = sound_set
        elif self.music_on:
            music_set = not music_set
            mixer.music.stop()
            button_click = True
            i = 6
            image = self.button_font.render('OFF', True, GREY)
            rect = image.get_rect()
            rect.topleft = self.music_rect.topright
            save_dict['music'] = music_set
        elif self.music_off and sound_set:
            music_set = not music_set
            mixer.music.play(-1)
            mixer.music.set_volume(.0175)
            button_click = True
            i = 6
            image = self.button_font.render('ON', True, GREY)
            rect = image.get_rect()
            rect.topleft = self.music_rect.topright
            save_dict['music'] = music_set
        elif self.easy_dif:
            dif_set = "1"
            button_click = True
            i = 8
            image = self.button_font.render('MEDIUM', True, GREY)
            rect = image.get_rect()
            rect.topleft = self.dif_rect.topright
            save_dict['difficulty'] = dif_set
        elif self.medium_dif:
            dif_set = "2"
            button_click = True
            i = 8
            image = self.button_font.render('HARD', True, GREY)
            rect = image.get_rect()
            rect.topleft = self.dif_rect.topright
            save_dict['difficulty'] = dif_set
        elif self.hard_dif:
            dif_set = "0"
            button_click = True
            i = 8
            image = self.button_font.render('EASY', True, GREY)
            rect = image.get_rect()
            rect.topleft = self.dif_rect.topright
            save_dict['difficulty'] = dif_set
        elif self.controls:
            render_sprites.empty()
            render_sprites.add(controls)
        elif self.statistics:
            render_sprites.empty()
            statistics.open = True
            render_sprites.add(statistics)
        
        # Updates the save dict and file if a setting is changed
        if button_click:
            self.buttons['blits'][i] = (image, rect)
            save_json = json.dumps(save_dict)
            with open('save_file.json', 'w') as f:
                f.write(save_json)
            

class Controls(pygame.sprite.Sprite):
    """CONTROLS screen.
    
    Screen that shows the controls of the game.
    
    Methods:
    - __init__()
    - mouse_position()
    - update()
    - click()"""
    
    def __init__(self):
        """Initiates the sprite."""
        
        pygame.sprite.Sprite.__init__(self)
        
        # Menu background
        self.image = pygame.Surface((760, 570), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = screen_rect.center
        self.rect.centerx = screen_rect.centerx
        
        # Title
        self.title_font = pygame.font.Font(FONT_FILE, 44)
        title_surface = self.title_font.render('CONTROLS', True, WHITE)
        title_rect = title_surface.get_rect()
        title_rect.midtop = self.rect.midtop
        
        # Since the only clickable button is the one to return to the
        # settings screen, a list is used to store the blits instead of a dict
        self.blit_list = [(title_surface, title_rect)]
        
        # Button to go back to the previous screen
        back_surface = self.title_font.render('<<', True, GREY)
        back_rect = back_surface.get_rect()
        back_rect.topleft = self.rect.topleft
        self.blit_list.append((back_surface, back_rect))
        self.x = range(42, 91)
        self.y = range(43, 75)
        
        # Controls
        controls_font = pygame.font.Font(FONT_FILE, 30)
        
        # Spacebar
        space_surface = pygame.image.load('spacebar.png').convert_alpha()
        space_surface = pygame.transform.scale(space_surface, (235*70.8/79, 70.8))
        space_rect = space_surface.get_rect()
        space_rect.left = self.rect.left
        space_rect.centery = self.rect.centery - self.rect.top
        self.blit_list.append((space_surface, space_rect))
        
        text_surface = controls_font.render('  SHOOT BULLET', True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.left = space_rect.right
        text_rect.centery = space_rect.centery
        self.blit_list.append((text_surface, text_rect))
        
        # Left and right arrows
        arrows_surface = pygame.image.load('arrow keys.png').convert_alpha()
        arrows_surface = pygame.transform.scale(arrows_surface, (144.3, 70.8))
        arrows_rect = arrows_surface.get_rect()
        arrows_rect.left = self.rect.left
        arrows_rect.bottom = space_rect.top - 20
        self.blit_list.append((arrows_surface, arrows_rect))
        
        text_surface = controls_font.render('  PLAYER MOVEMENT', True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.left = arrows_rect.right
        text_rect.centery = arrows_rect.centery
        self.blit_list.append((text_surface, text_rect))
        
        # ESC
        esc_surface = pygame.image.load('esc.png').convert_alpha()
        esc_surface = pygame.transform.scale(esc_surface, (491*70.8/497, 70.8))
        esc_rect = esc_surface.get_rect()
        esc_rect.left = self.rect.left
        esc_rect.top = space_rect.bottom + 20
        self.blit_list.append((esc_surface, esc_rect))
        
        text_surface = controls_font.render('  PAUSE/RESUME GAME', True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.left = esc_rect.right
        text_rect.centery = esc_rect.centery
        self.blit_list.append((text_surface, text_rect))
        
        self.image.fill(MENU_BACKGROUND)
        self.image.blits(self.blit_list)
        
    def mouse_position(self):
        """Stores the mouse position and checks if it's over the return
        button.
        
        Gets the x and y coordinates of the mouse and checks if they
        coincide with the buttons' coordinates."""
        
        x, y = pygame.mouse.get_pos()

        back_x = x in self.x
        back_y = y in self.y
        self.back = back_x and back_y

    def update(self):
        """Updates the CONTROLS screen.
        
        Highlights the return button when the mouse is over it."""
        
        self.mouse_position()

        mouse_over = False

        if self.back:
            mouse_over = True
            image = self.title_font.render('<<', True, WHITE)
            rect = image.get_rect()
            rect.topleft = self.rect.topleft

        if mouse_over:
            # If the mouse is over the button, uses a new list of blits
            # that is identical to the original, except for the
            # highlighted button
            new_blits = self.blit_list[:]
            new_blits[1] = (image, rect)
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(new_blits)
        else:
            # Otherwise, uses the regular blits
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(self.blit_list)

    def click(self):
        """Click event handler.
        
        Returns to the settings screen if the button is clicked."""
        
        if self.back:
            render_sprites.empty()
            render_sprites.add(settings)
        

class Statistics(pygame.sprite.Sprite):
    """STATISTICS screen.
    
    Screen that shows gameplay statistics:
    - Maximum score and hit rate for each of the difficulties
    - Total playtime
    - Average playtime
    
    Methods:
    - __init__()
    - mouse_position()
    - update()
    - click()"""
    
    def __init__(self):
        """Initiates the sprite."""
        
        pygame.sprite.Sprite.__init__(self)
        
        # Menu background
        self.image = pygame.Surface((760, 570), pygame.SRCALPHA)
        self.image.fill(MENU_BACKGROUND)
        self.rect = self.image.get_rect()
        self.rect.center = screen_rect.center
        
        # Title
        self.title_font = pygame.font.Font(FONT_FILE, 44)
        title_surface = self.title_font.render('STATISTICS', True, WHITE)
        title_rect = title_surface.get_rect()
        title_rect.midtop = self.rect.midtop
        
        self.blit_list = [(title_surface, title_rect)] # 0
        
        # Button to go back to the previous screen
        back_surface = self.title_font.render('<<', True, GREY)
        back_rect = back_surface.get_rect()
        back_rect.topleft = self.rect.topleft
        self.blit_list.append((back_surface, back_rect)) # 1
        self.x = range(42, 91)
        self.y = range(43, 75)
        
        stats_font = pygame.font.Font(FONT_FILE, 24)
        self.val_font = pygame.font.Font(FONT_FILE, 16)
        
        # Maximum score
        score_surface = stats_font.render('MAX SCORE ', True, WHITE)
        self.score_rect = score_surface.get_rect()
        height = self.score_rect.height
        self.score_rect.left = self.rect.left
        self.score_rect.top = title_rect.bottom + 6*height
        self.blit_list.append((score_surface, self.score_rect)) # 2
        
        # Maximum score (easy)
        easy = str(save_dict['stats']['0']['max score'])
        easy_score_surface = self.val_font.render(easy, True, GREY)
        easy_score_rect = easy_score_surface.get_rect()
        easy_score_rect.centery = self.score_rect.centery
        easy_score_rect.left = self.score_rect.right + 30
        easy_score_rect.center = 289, 272
        self.blit_list.append((easy_score_surface, easy_score_rect)) # 3
        
        easy_surface = stats_font.render('EASY', True, WHITE)
        easy_rect = easy_surface.get_rect()
        easy_rect.centerx = easy_score_rect.centerx
        easy_rect.bottom = self.score_rect.top
        self.blit_list.append((easy_surface, easy_rect)) # 4
        
        # Maximum score (medium)
        medium = str(save_dict['stats']['1']['max score'])
        mid_score_surface = self.val_font.render(medium, True, GREY)
        mid_score_rect = mid_score_surface.get_rect()
        mid_score_rect.top = easy_score_rect.top
        mid_score_rect.left = easy_score_rect.right + 30
        mid_score_rect.center = 471, 272
        self.blit_list.append((mid_score_surface, mid_score_rect)) # 5
        
        mid_surface = stats_font.render('MEDIUM', True, WHITE)
        mid_rect = mid_surface.get_rect()
        mid_rect.centerx = mid_score_rect.centerx
        mid_rect.bottom = self.score_rect.top
        self.blit_list.append((mid_surface, mid_rect)) # 6
        
        # Maximum score (hard)
        hard = str(save_dict['stats']['2']['max score'])
        hard_score_surface = self.val_font.render(hard, True, GREY)
        hard_score_rect = hard_score_surface.get_rect()
        hard_score_rect.top = mid_score_rect.top
        hard_score_rect.left = mid_score_rect.right + 30
        hard_score_rect.center = 653, 272
        self.blit_list.append((hard_score_surface, hard_score_rect)) # 7
        
        hard_surface = stats_font.render('HARD', True, WHITE)
        hard_rect = hard_surface.get_rect()
        hard_rect.centerx = hard_score_rect.centerx
        hard_rect.bottom = self.score_rect.top
        self.blit_list.append((hard_surface, hard_rect)) # 8
        
        # Hit rate
        hit_surface = stats_font.render('HIT RATE ', True, WHITE)
        self.hit_rect = hit_surface.get_rect()
        self.hit_rect.topleft = self.score_rect.bottomleft
        self.blit_list.append((hit_surface, self.hit_rect)) # 9
        
        # Hit rate (easy)
        hits = save_dict['stats']['0']['enemies killed']
        shots = save_dict['stats']['0']['bullets shot']
        if not shots:
            rate = '0.00%'
        else:
            rate = f'{(hits/shots):.2%}'
        easy_hit_surface = self.val_font.render(rate, True, GREY)
        easy_hit_rect = easy_hit_surface.get_rect()
        easy_hit_rect.centerx = easy_score_rect.centerx
        easy_hit_rect.centery = self.hit_rect.centery
        self.blit_list.append((easy_hit_surface, easy_hit_rect)) # 10
        
        # Hit rate (medium)
        hits = save_dict['stats']['1']['enemies killed']
        shots = save_dict['stats']['1']['bullets shot']
        if not shots:
            rate = '0.00%'
        else:
            rate = f'{(hits/shots):.2%}'
        mid_hit_surface = self.val_font.render(rate, True, GREY)
        mid_hit_rect = mid_hit_surface.get_rect()
        mid_hit_rect.top = easy_hit_rect.top
        mid_hit_rect.centerx = mid_score_rect.centerx
        self.blit_list.append((mid_hit_surface, mid_hit_rect)) # 11
        
        # Hit rate (hard)
        hits = save_dict['stats']['2']['enemies killed']
        shots = save_dict['stats']['2']['bullets shot']
        if not shots:
            rate = '0.00%'
        else:
            rate = f'{(hits/shots):.2%}'
        hard_hit_surface = self.val_font.render(rate, True, GREY)
        hard_hit_rect = hard_hit_surface.get_rect()
        hard_hit_rect.top = easy_hit_rect.top
        hard_hit_rect.centerx = hard_score_rect.centerx
        self.blit_list.append((hard_hit_surface, hard_hit_rect)) # 12
        
        # Total playtime string
        time = save_dict['stats']['total playtime']
        seconds = (time/1000)%60
        minutes = int((time/60000)%60)
        hours = int(time/(1000*60*60))
        playtime = f'{hours:02d}:{minutes:02d}:{seconds:06.3f}'
        
        # Average playtime string
        matches = save_dict['stats']['matches']
        if not matches:
            avg_time = 0
        else:
            avg_time = time/matches
        seconds = (avg_time/1000)%60
        minutes = int((avg_time/60000)%60)
        hours = int(avg_time/(1000*60*60))
        avg_playtime = f'{hours:02d}:{minutes:02d}:{seconds:06.3f}'
        
        
        time_surface = stats_font.render('TOTAL PLAYTIME ', True, WHITE)
        self.time_rect = time_surface.get_rect()
        self.time_rect.top = self.hit_rect.bottom + height
        self.time_rect.left = self.rect.left
        self.blit_list.append((time_surface, self.time_rect)) # 13
        
        avg_surface = stats_font.render('AVERAGE PLAYTIME ', True, WHITE)
        self.avg_rect = avg_surface.get_rect()
        self.avg_rect.topleft = self.time_rect.bottomleft
        self.blit_list.append((avg_surface, self.avg_rect)) # 14
        
        # Average playtime
        avg_time_surface = self.val_font.render(avg_playtime, True, GREY)
        avg_time_rect = avg_time_surface.get_rect()
        avg_time_rect.left = self.avg_rect.right + 30
        avg_time_rect.centery = self.avg_rect.centery
        self.blit_list.append((avg_time_surface, avg_time_rect)) # 15
        
        # Total playtime
        playtime_surface = self.val_font.render(playtime, True, GREY)
        playtime_rect = playtime_surface.get_rect()
        playtime_rect.centerx = avg_time_rect.centerx
        playtime_rect.centery = self.time_rect.centery
        self.blit_list.append((playtime_surface, playtime_rect)) # 16
        
        self.image.fill(MENU_BACKGROUND)
        self.image.blits(self.blit_list)
        
        # Boolean to determine whether the screen was just opened
        self.open = False
        
    def mouse_position(self):
        """Stores the mouse position and checks if it's over the return
        button.
        
        Gets the x and y coordinates of the mouse and checks if they
        coincide with the buttons' coordinates."""
        x, y = pygame.mouse.get_pos()

        back_x = x in self.x
        back_y = y in self.y
        self.back = back_x and back_y

    def update(self):
        """Updates the STATISTICS screen.
        
        - Updates the sprite with the current statistics when the
        screen is open for the first time
        - Highlights the return button when the mouse is over it"""
        
        # Updates the statistics
        if self.open:
            # Maximum score (easy)
            easy = str(save_dict['stats']['0']['max score'])
            easy_score_surface = self.val_font.render(easy, True, GREY)
            easy_score_rect = easy_score_surface.get_rect()
            easy_score_rect.centery = self.score_rect.centery
            easy_score_rect.left = self.score_rect.right + 30
            easy_score_rect.center = 289, 272
            self.blit_list[3] = (easy_score_surface, easy_score_rect)
            
            # Maximum score (medium)
            medium = str(save_dict['stats']['1']['max score'])
            mid_score_surface = self.val_font.render(medium, True, GREY)
            mid_score_rect = mid_score_surface.get_rect()
            mid_score_rect.top = easy_score_rect.top
            mid_score_rect.left = easy_score_rect.right + 30
            mid_score_rect.center = 471, 272
            self.blit_list[5] = (mid_score_surface, mid_score_rect)

            # Maximum score (hard)
            hard = str(save_dict['stats']['2']['max score'])
            hard_score_surface = self.val_font.render(hard, True, GREY)
            hard_score_rect = hard_score_surface.get_rect()
            hard_score_rect.top = mid_score_rect.top
            hard_score_rect.left = mid_score_rect.right + 30
            hard_score_rect.center = 653, 272
            self.blit_list[7] = (hard_score_surface, hard_score_rect)

            # Hit rate (easy)
            hits = save_dict['stats']['0']['enemies killed']
            shots = save_dict['stats']['0']['bullets shot']
            if not shots:
                rate = '0.00%'
            else:
                rate = f'{(hits/shots):.2%}'
            easy_hit_surface = self.val_font.render(rate, True, GREY)
            easy_hit_rect = easy_hit_surface.get_rect()
            easy_hit_rect.centerx = easy_score_rect.centerx
            easy_hit_rect.centery = self.hit_rect.centery
            self.blit_list[10] = (easy_hit_surface, easy_hit_rect)

            # Hit rate (medium)
            hits = save_dict['stats']['1']['enemies killed']
            shots = save_dict['stats']['1']['bullets shot']
            if not shots:
                rate = '0.00%'
            else:
                rate = f'{(hits/shots):.2%}'
            mid_hit_surface = self.val_font.render(rate, True, GREY)
            mid_hit_rect = mid_hit_surface.get_rect()
            mid_hit_rect.top = easy_hit_rect.top
            mid_hit_rect.centerx = mid_score_rect.centerx
            self.blit_list[11] = (mid_hit_surface, mid_hit_rect)

            # Hit rate (hard)
            hits = save_dict['stats']['2']['enemies killed']
            shots = save_dict['stats']['2']['bullets shot']
            if not shots:
                rate = '0.00%'
            else:
                rate = f'{(hits/shots):.2%}'
            hard_hit_surface = self.val_font.render(rate, True, GREY)
            hard_hit_rect = hard_hit_surface.get_rect()
            hard_hit_rect.top = easy_hit_rect.top
            hard_hit_rect.centerx = hard_score_rect.centerx
            self.blit_list[12] = (hard_hit_surface, hard_hit_rect)

            # Total playtime string
            time = save_dict['stats']['total playtime']
            seconds = (time/1000)%60
            minutes = int((time/60000)%60)
            hours = int(time/(1000*60*60))
            playtime = f'{hours:02d}:{minutes:02d}:{seconds:06.3f}'

            # Average playtime string
            matches = save_dict['stats']['matches']
            if not matches:
                avg_time = 0
            else:
                avg_time = time/matches
            seconds = (avg_time/1000)%60
            minutes = int((avg_time/60000)%60)
            hours = int(avg_time/(1000*60*60))
            avg_playtime = f'{hours:02d}:{minutes:02d}:{seconds:06.3f}'

            # Average playtime
            avg_time_surface = self.val_font.render(avg_playtime, True, GREY)
            avg_time_rect = avg_time_surface.get_rect()
            avg_time_rect.left = self.avg_rect.right + 30
            avg_time_rect.centery = self.avg_rect.centery
            self.blit_list[15] = (avg_time_surface, avg_time_rect)

            # Total playtime
            playtime_surface = self.val_font.render(playtime, True, GREY)
            playtime_rect = playtime_surface.get_rect()
            playtime_rect.centerx = avg_time_rect.centerx
            playtime_rect.centery = self.time_rect.centery
            self.blit_list[16] = (playtime_surface, playtime_rect)
            
            # Once the screen is open, the boolean is set to False
            self.open = False
        
        self.mouse_position()

        mouse_over = False

        if self.back:
            mouse_over = True
            image = self.title_font.render('<<', True, WHITE)
            rect = image.get_rect()
            rect.topleft = self.rect.topleft

        if mouse_over:
            # If the mouse is over the button, uses a new list of blits
            # that is identical to the original, except for the
            # highlighted button
            new_blits = self.blit_list[:]
            new_blits[1] = (image, rect)
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(new_blits)
        else:
            # Otherwise, uses the regular blits
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(self.blit_list)  
        
    def click(self):
        """Click event handler.
        
        Returns to the settings screen if the button is clicked."""
        
        if self.back:
            render_sprites.empty()
            render_sprites.add(settings)
    
    
class Pause(pygame.sprite.Sprite):
    """PAUSE screen.
    
    Contains buttons to resume the gameplay, to the settings screen and
    to quit the game.
    
    Methods:
    - __init__()
    - mouse_position()
    - update()
    - click()
    - pause()
    - resume()"""
    
    def __init__(self):
        """Initiates the sprite."""
        
        pygame.sprite.Sprite.__init__(self)

        # Menu background
        self.image = pygame.Surface((760, 570), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = screen_rect.center

        # Title
        title_font = pygame.font.Font(FONT_FILE, 64)
        title_surface = title_font.render('PAUSED', True, WHITE)
        self.title_rect = title_surface.get_rect()
        self.title_rect.centerx = self.rect.centerx - self.rect.left
        self.title_rect.centery = self.rect.centery - self.rect.top
        
        # Dict that stores what is blitted onto the screen and each button's coordinates
        # The title coordinates aren't stored because they are never used
        self.buttons = {'blits': [(title_surface, self.title_rect)]}

        self.button_font = pygame.font.Font(FONT_FILE, 24)

        # Resume game
        resume_surface = self.button_font.render('RESUME GAME', True, GREY)
        self.resume_rect = resume_surface.get_rect()
        self.resume_rect.top = self.title_rect.bottom + 10
        self.resume_rect.centerx = self.title_rect.centerx
        self.buttons['blits'].append((resume_surface, self.resume_rect))
        self.buttons['x'] = [range(304, 496)]
        self.buttons['y'] = [range(354, 378)]
        
        # Settings
        set_surface = self.button_font.render('SETTINGS', True, GREY)
        self.set_rect = set_surface.get_rect()
        self.set_rect.midtop = self.resume_rect.midbottom
        self.buttons['blits'].append((set_surface, self.set_rect))
        self.buttons['x'].append(range(329, 472))
        self.buttons['y'].append(range(384, 408))
        
        # Quit game
        quit_surface = self.button_font.render('QUIT', True, GREY)
        quit_rect = quit_surface.get_rect()
        quit_rect.midtop = self.set_rect.midbottom
        self.buttons['blits'].append((quit_surface, quit_rect))
        self.buttons['x'].append(range(365, 435))
        self.buttons['y'].append(range(414, 438))

        self.image.fill(MENU_BACKGROUND)
        self.image.blits(self.buttons['blits'])
        
        # Boolean to determine whether a gameplay is paused
        self.paused = False

    def mouse_position(self):
        """Stores the mouse position and checks if it's over a button.
        
        Gets the x and y coordinates of the mouse and checks if they
        coincide with any of the buttons' coordinates, which are stored
        in the buttons dict."""
        
        x, y = pygame.mouse.get_pos()

        resume_x = x in self.buttons['x'][0]
        resume_y = y in self.buttons['y'][0]
        self.resume_button = resume_x and resume_y

        settings_x = x in self.buttons['x'][1]
        settings_y = y in self.buttons['y'][1]
        self.settings_button = settings_x and settings_y
        
        quit_x = x in self.buttons['x'][2]
        quit_y = y in self.buttons['y'][2]
        self.quit = quit_x and quit_y
    
    def update(self):
        """Updates the PAUSE screen.
        
        Highlights a button when the mouse is over it."""
        
        self.mouse_position()
        
        mouse_over = False
        
        if self.resume_button:
            mouse_over = True
            i = 1
            image = self.button_font.render('RESUME GAME', True, WHITE)
            rect = image.get_rect()
            rect.top = self.title_rect.bottom + 10
            rect.centerx = self.title_rect.centerx
        elif self.settings_button:
            mouse_over = True
            i = 2
            image = self.button_font.render('SETTINGS', True, WHITE)
            rect = image.get_rect()
            rect.midtop = self.resume_rect.midbottom
        elif self.quit:
            mouse_over = True
            i = 3
            image = self.button_font.render('QUIT', True, WHITE)
            rect = image.get_rect()
            rect.midtop = self.set_rect.midbottom
        
        if mouse_over:
            # If the mouse is over a button, uses a new list of blits
            # that is identical to the buttons dict's, except for the
            # highlighted button
            new_blits = self.buttons['blits'][:]
            new_blits[i] = (image, rect)
            new_blits[:i] = self.buttons['blits'][:i]
            new_blits[i+1:] = self.buttons['blits'][i+1:]
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(new_blits)
        else:
            # Otherwise, uses the regular blits
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(self.buttons['blits'])
    
    def click(self):
        """Click event handler.
        
        Resumes the game, quits it or goes to the settings screen if
        one of the respective buttons is pressed."""
        
        self.mouse_position()
        
        if self.resume_button:
            self.resume()
        elif self.settings_button:
            settings.previous_screen.add(self)
            render_sprites.empty()
            render_sprites.add(settings)
        elif self.quit:
            render_sprites.empty()
            render_sprites.add(quit_screen)

    def pause(self):
        """Pauses the game."""

        # Records the time elapsed since the gameplay started/resumed 
        global elapsed
        elapsed = pygame.time.get_ticks() - checkpoint
        save_dict['stats']['total playtime'] += elapsed
        
        # Checks if the score so far has surpassed the last maximum, in
        # case the game is closed
        max_score = save_dict['stats'][dif_set]['max score']
        if score.value > max_score:
            save_dict['stats'][dif_set]['max score'] = score.value
        
        render_sprites.empty()
        render_sprites.add(self)
        
        # Updates the save file, in case the game is closed
        save_json = json.dumps(save_dict)
        with open('save_file.json', 'w') as f:
            f.write(save_json)

    def resume(self):
        """Resumes the game."""
        
        render_sprites.empty()

        # Checks if the bullet's shot attribute is True so that, if so,
        # the bullet is redrawn at the position it was when the game
        # was paused
        if bullet.shot:
            render_sprites.add(player, bullet, score, enemies)
        else:
            render_sprites.add(player, score, enemies)

        self.paused = False
        
        # Resets the checkpoint
        global checkpoint
        checkpoint = pygame.time.get_ticks()
            

class GameOver(pygame.sprite.Sprite):
    """GAME OVER screen.
    
    Contains the score and buttons to the main and settings screens.
    
    Methods:
    - __init__()
    - mouse_position()
    - update()
    - click()"""
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # Menu background
        self.image = pygame.Surface((760, 570), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = screen_rect.center
        
        # Game over message
        title_font = pygame.font.Font(FONT_FILE, 64)
        title_surface = title_font.render('GAME OVER', True, WHITE)
        self.title_rect = title_surface.get_rect()
        self.title_rect.centerx = self.rect.centerx - self.rect.left
        self.title_rect.centery = self.rect.centery - self.rect.top
        
        # Dict that stores what is blitted onto the screen and each
        # button's coordinates
        # The title and score coordinates aren't stored because they
        # are never used
        self.buttons = {'blits': [(title_surface, self.title_rect)]}    
        
        # Score
        self.score_font = pygame.font.Font(FONT_FILE, 30)
        score_surface = self.score_font.render('SCORE: ' + str(score.value), True, WHITE)
        self.score_rect = score_surface.get_rect()
        self.score_rect.top = self.title_rect.bottom + 10
        self.score_rect.centerx = self.title_rect.centerx
        self.buttons['blits'].append((score_surface, self.score_rect))
        
        self.button_font = pygame.font.Font(FONT_FILE, 24)
        
        # Home screen button
        home_surface = self.button_font.render('HOME SCREEN', True, GREY)
        self.home_rect = home_surface.get_rect()
        self.home_rect.top = self.score_rect.bottom + 15
        self.home_rect.centerx = self.title_rect.centerx
        self.buttons['blits'].append((home_surface, self.home_rect))
        self.buttons['x'] = [range(304, 496)]
        self.buttons['y'] = [range(406, 430)]

        # Settings button
        set_surface = self.button_font.render('SETTINGS', True, GREY)
        set_rect = set_surface.get_rect()
        set_rect.midtop = self.home_rect.midbottom
        self.buttons['blits'].append((set_surface, set_rect))
        self.buttons['x'].append(range(329, 472))
        self.buttons['y'].append(range(438, 462))
            
        self.image.fill(MENU_BACKGROUND)
        self.image.blits(self.buttons['blits'])
        
        # Boolean to determine whether a gameplay is just finished
        self.over = False
            
    def mouse_position(self):
        """Stores the mouse position and checks if it's over either
        button.
        
        Gets the x and y coordinates of the mouse and checks if they
        coincide with any of the button's coordinates, which are stored
        in the buttons dict."""
        
        x, y = pygame.mouse.get_pos()
        
        home_x = x in self.buttons['x'][0]
        home_y = y in self.buttons['y'][0]
        self.home = home_x and home_y
        
        settings_x = x in self.buttons['x'][1]
        settings_y = y in self.buttons['y'][1]
        self.settings_button = settings_x and settings_y
    
    def update(self):
        """Updates the GAME OVER screen.
        
        This method is called for the first time when the game is
        over. The score rect's dimensions are updated to accomodate
        the score's length. This is because when the score is higher
        than 9, the original rect becomes too short, since it is
        dimensioned when this object is initialized (which happens
        before the game loop starts running, when the score is
        defaulted to 0). The enemies sprite group is emptied as well so
        that, should a new game start, brand new enemies are blitted to
        the screen.
        
        On later calls, this highlights a button when the mouse is over
        it."""
        
        if not self.over:
            self.over = True
            bullet.shot = False
            home_screen.game_start = False
            render_sprites.empty()
            enemies.empty()
            
            if not pause.paused:
                # Whenever the game is over mid-gameplay (due to the player
                # dying or the maximum score is reached), the elapsed
                # playtime is updated to the save dict
                save_dict['stats']['total playtime'] += elapsed
            else:
                # If the game is quit (only possible when the gameplay
                # is paused), the paused boolean is reset to False
                pause.paused = False
            
            # Updates the score rect's dimensions
            score_surface = self.score_font.render('SCORE: ' + str(score.value), True, WHITE)
            score_rect = score_surface.get_rect()
            score_rect.top = self.title_rect.bottom + 10
            score_rect.centerx = self.title_rect.centerx
            self.buttons['blits'][1] = (score_surface, score_rect)
            
            self.add(render_sprites)
        
        # Highlights a button when the mouse hovers over it
        self.mouse_position()
        
        mouse_over = False
        
        if self.home:
            mouse_over = True
            i = 2
            image = self.button_font.render('HOME SCREEN', True, WHITE)
            rect = image.get_rect()
            rect.top = self.score_rect.bottom + 15
            rect.centerx = self.title_rect.centerx
        elif self.settings_button:
            mouse_over = True
            i = 3
            image = self.button_font.render('SETTINGS', True, WHITE)
            rect = image.get_rect()
            rect.midtop = self.home_rect.midbottom
        
        if mouse_over:
            # If the mouse is over a button, uses a new list of blits
            # that is identical to the buttons dict's, except for the
            # highlighted button
            new_blits = self.buttons['blits'][:]
            new_blits[i] = (image, rect)
            new_blits[:i] = self.buttons['blits'][:i]
            new_blits[i+1:] = self.buttons['blits'][i+1:]
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(new_blits)
        else:
            # Otherwise, uses the regular blits
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(self.buttons['blits'])
        
    
    def click(self):
        """Click event handler.
        
        Goes to the home or settings screen if one of the respective
        buttons is pressed."""
        
        self.mouse_position()
        
        if self.home:
            render_sprites.empty()
            render_sprites.add(home_screen)
            self.over = False
        elif self.settings_button:
            settings.previous_screen.add(self)
            render_sprites.empty()
            render_sprites.add(settings)
        

class QuitScreen(pygame.sprite.Sprite):
    """Screen that asks if the player is sure about quitting the game.
    
    Appears after the player clicks 'QUIT' on the pause menu.
    Asks 'ARE YOU SURE YOU WANT TO QUIT THE GAME?' and has the 'YES' or
    'NO' options.
    
    Methods:
    - __init__()
    - mouse_position()
    - update()
    - click()"""
    
    def __init__(self):
        """Initiates the sprite."""
        
        pygame.sprite.Sprite.__init__(self)
        
        # Menu background
        self.image = pygame.Surface((760, 570), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = screen_rect.center
        
        # Question 'ARE YOU SURE YOU WANT TO QUIT THE GAME?'
        question_font = pygame.font.Font(FONT_FILE, 44)
        
        line_1 = 'ARE YOU SURE YOU WANT'
        
        width, height = question_font.size(line_1)
        
        question_rect = pygame.Rect(0, 0, width, 2*height)
        question_rect.centerx = self.rect.centerx - self.rect.left
        question_rect.centery = self.rect.centery - self.rect.top - height

        line_1_surface = question_font.render(line_1, True, WHITE)
        line_1_rect = line_1_surface.get_rect()
        line_1_rect.midtop = question_rect.midtop
        
        # Dict that stores what is blitted onto the screen and each button's coordinates
        # The question rects coordinates aren't stored because they are never used
        self.buttons = {'blits': [(line_1_surface, line_1_rect)]}
        
        line_2 = 'TO QUIT THE GAME?'
        line_2_surface = question_font.render(line_2, True, WHITE)
        line_2_rect = line_2_surface.get_rect()
        line_2_rect.midbottom = question_rect.midbottom
        self.buttons['blits'].append((line_2_surface, line_2_rect))

        # Answers
        self.answer_font = pygame.font.Font(FONT_FILE, 40)
        
        self.answer_rect = pygame.Rect(0, 0, width-200, height)
        self.answer_rect.top = question_rect.bottom + 30
        self.answer_rect.centerx = question_rect.centerx
        
        # 'YES'
        yes = self.answer_font.render('YES', True, GREY)
        yes_rect = yes.get_rect()
        yes_rect.topleft = self.answer_rect.topleft
        self.buttons['blits'].append((yes, yes_rect))
        self.buttons['x'] = [range(179, 271)] # x: 0
        self.buttons['y'] = range(337, 372) # y: 0
        
        # 'NO'
        no = self.answer_font.render('NO', True, GREY)
        no_rect = no.get_rect()
        no_rect.topright = self.answer_rect.topright
        self.buttons['blits'].append((no, no_rect))
        self.buttons['x'].append(range(562, 624)) # x: 1

        self.image.fill(MENU_BACKGROUND)
        self.image.blits(self.buttons['blits'])

    def mouse_position(self):
        """Stores the mouse position and checks if it's over either
        button.
        
        Gets the x and y coordinates of the mouse and checks if they
        coincide with any of the button's coordinates, which are stored
        in the buttons dict."""

        x, y = pygame.mouse.get_pos()
        
        yes_x = x in self.buttons['x'][0]
        yes_y = y in self.buttons['y']
        self.yes = yes_x and yes_y
        
        no_x = x in self.buttons['x'][1]
        no_y = y in self.buttons['y']
        self.no = no_x and no_y
        
    def update(self):
        """Updates the QUIT GAME screen.
        
        Highlights a button when the mouse is over it."""
        
        self.mouse_position()
        
        mouse_over = False
        
        if self.yes:
            mouse_over = True
            i = 2
            image = self.answer_font.render('YES', True, WHITE)
            rect = image.get_rect()
            rect.topleft = self.answer_rect.topleft
        elif self.no:
            mouse_over = True
            i = 3
            image = self.answer_font.render('NO', True, WHITE)
            rect = image.get_rect()
            rect.topright = self.answer_rect.topright
        
        if mouse_over:
            # If the mouse is over a button, uses a new list of blits
            # that is identical to the buttons dict's, except for the
            # highlighted button
            new_blits = self.buttons['blits'][:]
            new_blits[i] = (image, rect)
            new_blits[:i] = self.buttons['blits'][:i]
            new_blits[i+1:] = self.buttons['blits'][i+1:]
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(new_blits)
        else:
            # Otherwise, uses the regular blits
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(self.buttons['blits'])
     
    def click(self):
        """Click event handler.
        
        - If the player clicked 'YES', finishes the game
        - If the player clicked 'NO', goes back to the pause screen"""
        
        self.mouse_position()
        
        if self.yes:
            game_over.update()
        elif self.no:
            render_sprites.empty()
            render_sprites.add(pause)

                
class ChangingDifficulty(pygame.sprite.Sprite):
    """Screen that asks if the player is sure about changing the
    difficulty, because, if so, the game has to be quit.
    
    Appears after the player changes the difficulty on the settings
    screen, in case it was done accidentally or the player changes
    their mind.
    Asks 'CHANGING THE DIFFICULTY WILL QUIT THE GAME. ARE YOU SURE?'
    and has the 'YES' or 'NO' options.
    
    Methods:
    - __init__()
    - mouse_position()
    - update()
    - click()"""
    
    def __init__(self):
        """Initiates the sprite."""
        pygame.sprite.Sprite.__init__(self)
        
        # Menu background
        self.image = pygame.Surface((760, 570), pygame.SRCALPHA)
        self.image.fill(MENU_BACKGROUND)
        self.rect = self.image.get_rect()
        self.rect.center = screen_rect.center

        # Question
        question_font = pygame.font.Font(FONT_FILE, 44)
        
        line_1 = 'CHANGING THE DIFFICULTY'
        
        width, height = question_font.size(line_1)
        
        question_rect = pygame.Rect(0, 0, width, 3*height)
        question_rect.centerx = self.rect.centerx - self.rect.left
        question_rect.centery = self.rect.centery - self.rect.top - height
        
        line_1_surface = question_font.render(line_1, True, WHITE)
        line_1_rect = line_1_surface.get_rect()
        line_1_rect.midtop = question_rect.midtop
        
        self.buttons = {'blits': [(line_1_surface, line_1_rect)]} # Blits: 0
        
        line_2 = 'WILL QUIT THE GAME. ARE'
        line_2_surface = question_font.render(line_2, True, WHITE)
        line_2_rect = line_2_surface.get_rect()
        line_2_rect.center = question_rect.center
        self.buttons['blits'].append((line_2_surface, line_2_rect)) # Blits: 1
        
        line_3 = 'YOU SURE?'
        line_3_surface = question_font.render(line_3, True, WHITE)
        line_3_rect = line_3_surface.get_rect()
        line_3_rect.midbottom = question_rect.midbottom
        self.buttons['blits'].append((line_3_surface, line_3_rect)) # Blits: 2
        
        # Answers
        self.answer_font = pygame.font.Font(FONT_FILE, 40)
        
        self.answer_rect = pygame.Rect(0, 0, width-284, height)
        self.answer_rect.top = question_rect.bottom + 30
        self.answer_rect.centerx = question_rect.centerx
        
        # 'YES'
        yes = self.answer_font.render('YES', True, GREY)
        yes_rect = yes.get_rect()
        yes_rect.topleft = self.answer_rect.topleft
        self.buttons['blits'].append((yes, yes_rect)) # BLits: 3
        self.buttons['x'] = [range(179, 271)] # x: 0
        self.buttons['y'] = range(365, 400)
        
        # 'NO'
        no = self.answer_font.render('NO', True, GREY)
        no_rect = no.get_rect()
        no_rect.topright = self.answer_rect.topright
        self.buttons['blits'].append((no, no_rect)) # Blits: 4
        self.buttons['x'].append(range(562, 624)) # x: 1

        self.image.fill(MENU_BACKGROUND)
        self.image.blits(self.buttons['blits'])

    def mouse_position(self):
        """Stores the mouse position and checks if it's over either
        button.
        
        Gets the x and y coordinates of the mouse and checks if they
        coincide with any of the button's coordinates, which are stored
        in the buttons dict."""

        x, y = pygame.mouse.get_pos()
        
        yes_x = x in self.buttons['x'][0]
        yes_y = y in self.buttons['y']
        self.yes = yes_x and yes_y
        
        no_x = x in self.buttons['x'][1]
        no_y = y in self.buttons['y']
        self.no = no_x and no_y
        
    def update(self):
        """Updates the QUIT GAME screen.
        
        Highlights a button when the mouse is over it."""
        
        self.mouse_position()
        
        mouse_over = False
        
        if self.yes:
            mouse_over = True
            i = 3
            image = self.answer_font.render('YES', True, WHITE)
            rect = image.get_rect()
            rect.topleft = self.answer_rect.topleft
        elif self.no:
            mouse_over = True
            i = 4
            image = self.answer_font.render('NO', True, WHITE)
            rect = image.get_rect()
            rect.topright = self.answer_rect.topright
        
        if mouse_over:
            # If the mouse is over a button, uses a new list of blits
            # that is identical to the buttons dict's, except for the
            # highlighted button
            new_blits = self.buttons['blits'][:]
            new_blits[i] = (image, rect)
            new_blits[:i] = self.buttons['blits'][:i]
            new_blits[i+1:] = self.buttons['blits'][i+1:]
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(new_blits)
        else:
            # Otherwise, uses the regular blits
            self.image.fill(MENU_BACKGROUND)
            self.image.blits(self.buttons['blits'])
        
    def click(self):
        """Click event handler.
        
        - If the player clicked 'YES', finishes the game
        - If the player clicked 'NO', goes back to the settings screen"""

        self.mouse_position()

        if self.yes:
            game_over.update()
        elif self.no:
            # If the player clicked 'NO', the difficulty is reset in
            # the save dict and file and in the settings sprite dict
            global dif_set
            dif_set = save_dict['difficulty'] = home_screen.difficulty
            
            save_json = json.dumps(save_dict)
            with open('save_file.json', 'w') as f:
                f.write(save_json)
            
            image = settings.button_font.render(difficulty[int(dif_set)], True, GREY)
            rect = image.get_rect()
            rect.topleft = settings.dif_rect.topright
            settings.buttons['blits'][8] = (image, rect)
            
            render_sprites.empty()
            render_sprites.add(settings)


# Sprites
render_sprites = pygame.sprite.RenderUpdates()
enemies = pygame.sprite.Group()

player = Player()
bullet = Bullet()
score = Score()
home_screen = HomeScreen()
settings = Settings()
controls = Controls()
statistics = Statistics()
pause = Pause()
change_difficulty = ChangingDifficulty()
quit_screen = QuitScreen()
game_over = GameOver()

# Game loop
try:
    while True:
        # Pygame's default framerate was making the player move too
        # fast, so it was set to 1000 to make the gameplay more natural
        clock = pygame.time.Clock()
        clock.tick(1000)
        
        # Updates the screen so that the player, enemies and other
        # icons don't leave trails of duplicates when moving
        screen.blit(background, (0, 0))
        
        # Only the QUIT and KEYUP/DOWN events are allowed for better
        # performance
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYUP, pygame.KEYDOWN])
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if home_screen.game_start:
                    if not pause.paused:
                        # Moves the player
                        if event.key == pygame.K_LEFT:
                            player.dx = -save_dict['stats'][dif_set]['player dx']
                        if event.key == pygame.K_RIGHT:
                            player.dx = save_dict['stats'][dif_set]['player dx']

                        # Shoots the bullet
                        if event.key == pygame.K_SPACE and (
                                not bullet.shot):
                            bullet.shoot()

                        # Pauses the game
                        if event.key == pygame.K_ESCAPE:
                            pause.paused = True
                            pause.pause()
                    else:
                        # Resumes the game
                        if event.key == pygame.K_ESCAPE:
                            pause.resume()
                        
            # Keeps the player icon from moving after releasing
            # the left or right key
            if event.type == pygame.KEYUP and (
                    event.key == pygame.K_LEFT or
                    event.key == pygame.K_RIGHT):
                player.dx = 0  
            
            # Handles click events
            if event.type == pygame.MOUSEBUTTONDOWN and (
                    not home_screen.game_start or pause.paused):
                for sprite in render_sprites:
                    sprite.click()
            
            # Throws the SystemExit exception in order to break the
            # loop and quit the game
            if event.type == pygame.QUIT:
                if home_screen.game_start:
                    if not pause.paused:
                        # If the window is closed mid-gameplay, the
                        # elapsed playtime is recorded in the save dict
                        # and the maximum score is updated if it was
                        # surpassed
                        elapsed = pygame.time.get_ticks() - checkpoint
                        save_dict['stats']['total playtime'] += elapsed
                        max_score = save_dict['stats'][dif_set]['max score']
                        if score.value > max_score:
                            save_dict['stats'][dif_set]['max score'] = score.value
                        
                # Updates the save file
                save_json = json.dumps(save_dict)
                with open('save_file.json', 'w') as f:
                    f.write(save_json)
                sys.exit()
        
        render_sprites.update()
        render_sprites.draw(screen)
        pygame.display.update()
        
except SystemExit:
    pygame.quit()

