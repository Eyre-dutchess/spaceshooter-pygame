import pygame
from os.path import join

from random import randint, uniform

class Player(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.original_surf = pygame.image.load(join("images", "player.png")).convert_alpha()
        self.image =self.original_surf
        self.rect = self.image.get_rect(center = (WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT - 100 ))
        self.direction = pygame.Vector2()
        self.speed = 300

        self.can_shoot = True
        self.laser_shoot_timestamp = 0
        self.cooldown_duration = 400
    
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_timestamp >= self.cooldown_duration:
                self.can_shoot = True
                
    def update(self, dt):
        keys = pygame.key.get_pressed() 
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize( ) if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        
        recent_keys = pygame.key.get_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            laser_sound.play()
            self.laser_shoot_timestamp = pygame.time.get_ticks()
            self.can_shoot = False
         
        self.laser_timer()

class Laser( pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(midbottom = pos)
    
    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()
  
class Star(pygame.sprite.Sprite):
    def __init__(self, *groups, surf):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_rect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))     

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, *groups):
        super().__init__(*groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_rect(center = pos)
        self.start_time = pygame.time.get_ticks() 
        self.lifetime = 2000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(600, 700)
        self.mask = pygame.mask.from_surface(self.image)
        self.rotation_speed = randint(60, 80)
        self.rotation = 0
        
    def update(self, dt):
        self.rect.centery += 500 * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

        # continuous rotation
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotate(self.original_surf, self.rotation)
        self.rect = self.image.get_rect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos,  *groups):
        super().__init__(*groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        
    def update(self, dt):
        self.frame_index += 20 * dt 
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()
                 
def collisions():
    global running
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        # running = False
        print("kill")
    
    for laser in laser_sprites:
        collision_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collision_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()
            
def display_score():
    current_time = pygame.time.get_ticks() //100
    text_turf = font.render(str(current_time), True, (240, 240, 240)) 
    text_rect = text_turf.get_rect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_turf, text_rect)  
    pygame.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 16).move(0, -2) , 5, 10)
          
#general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("game-try1")
running = True
clock = pygame.time.Clock()

#import
star_surf = pygame.image.load(join("images", "star.png")).convert_alpha()
laser_surf = pygame.image.load(join("images", "laser.png")).convert_alpha()
meteor_surf = pygame.image.load(join("images", "meteor.png")).convert_alpha()
font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 30)
explosion_frames = [pygame.image.load(join("images", "explosion", f'{i}.png')).convert_alpha() for i in range(10)]

laser_sound = pygame.mixer.Sound(join("audio", "laser-audio.wav"))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join("audio", "explosion-audio.wav"))
# game_music = pygame.mixer.Sound(join("audio", "game_music.wav"))
# game_music.set_volume(0.1)
# game_music.play(loops= -1 )


#sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()


for i in range(20):
    Star(all_sprites, surf=star_surf)
player = Player(all_sprites)

#custom event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)


while running:
    dt = clock.tick() / 1000
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type ==  meteor_event:
            x, y = randint(0, WINDOW_WIDTH),randint(-200, -100)
            Meteor(meteor_surf, (x, y) , (all_sprites , meteor_sprites))
    
    #update game       
    all_sprites.update(dt)
    collisions()
    
    #draw game
    display_surface.fill("gray")
    display_score()
    all_sprites.draw(display_surface)
    
    #test collison
    pygame.display.update()
pygame.quit()