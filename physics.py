import random

class PhysicsEngine:
    def __init__(self):
        self.gravity = 1.5
        self.restitution = 0.6 
        self.friction = 0.8
        
    def update(self, pet):
        x = float(pet.x())
        y = float(pet.y())
        
        if pet.state == 'flying':
            x += pet.velocity_x
            y += pet.velocity_y
            if x <= 0 or x >= pet.screen_geo.width() - pet.width():
                pet.velocity_x *= -1
            if y <= 0:
                pet.velocity_y = abs(pet.velocity_y) 
                
        elif pet.state in ['falling', 'thrown', 'dizzy', 'idle', 'walking', 'looking_around', 'following', 'funny_face', 'dancing', 'working', 'petting', 'hiding']:
            if pet.state == 'looking_around' and random.random() < 0.05:
                pet.direction *= -1
                
            if pet.state == 'dancing':
                if random.random() < 0.1:
                    pet.direction *= -1
                # Hop occasionally if touching the ground
                surface_y = pet.get_surface_y()
                floor_y = surface_y - pet.height()
                if random.random() < 0.1 and y >= floor_y - 5:
                    pet.velocity_y = -8.0
                    
            if pet.state == 'hiding':
                nearest_wall_x = 0 if x < pet.screen_geo.width() / 2 else pet.screen_geo.width() - pet.width()
                if x < nearest_wall_x:
                    pet.velocity_x = 15.0
                    pet.direction = 1
                elif x > nearest_wall_x:
                    pet.velocity_x = -15.0
                    pet.direction = -1
                
                if abs(x - nearest_wall_x) <= 15:
                    pet.velocity_x = 0
                    x = nearest_wall_x
                
            if pet.state in ['working', 'petting']:
                pet.velocity_x = 0
                
            if pet.state == 'following':
                from PyQt6.QtGui import QCursor
                cursor_x = QCursor.pos().x()
                pet_center_x = x + pet.width() / 2
                if cursor_x < pet_center_x - 20:
                    pet.direction = -1
                    pet.velocity_x = -3.0
                elif cursor_x > pet_center_x + 20:
                    pet.direction = 1
                    pet.velocity_x = 3.0
                else:
                    pet.velocity_x = 0

            # Apply gravity
            if pet.state not in ['idle', 'walking', 'looking_around', 'following', 'working', 'petting', 'hiding']:
                pet.velocity_y += self.gravity
                
            y += pet.velocity_y
            x += pet.velocity_x
            
            surface_y = pet.get_surface_y()
            floor_y = surface_y - pet.height()
            
            if y < floor_y - 5 and pet.state in ['idle', 'walking', 'looking_around']:
                pet.state = 'falling'
                pet.velocity_y = 0
                
            if y >= floor_y:
                y = floor_y
                if abs(pet.velocity_y) > 30:
                    pet.state = 'dizzy'
                    pet.dizzy_timer.start(2500)
                    pet.audio.play_sound('bump')
                elif abs(pet.velocity_y) > 15:
                    pet.state = 'funny_face'
                    pet.dizzy_timer.start(1000)
                    pet.audio.play_sound('bump')
                    
                pet.velocity_y *= -self.restitution
                pet.velocity_x *= self.friction
                
                if abs(pet.velocity_y) < 2 and abs(pet.velocity_x) < 1:
                    pet.velocity_y = 0
                    if pet.state not in ['dizzy']:
                        if pet.state == 'thrown' or pet.state == 'falling':
                            pet.state = 'idle'
                        pet.velocity_x = 0
                        
            # Wall collisions
            if x <= 0:
                x = 0
                pet.velocity_x *= -self.restitution
                if abs(pet.velocity_x) > 30 and pet.state not in ['dizzy', 'funny_face']:
                    pet.state = 'dizzy'
                    pet.dizzy_timer.start(2500)
                    pet.audio.play_sound('bump')
                elif abs(pet.velocity_x) > 15 and pet.state not in ['dizzy', 'funny_face']:
                    pet.state = 'funny_face'
                    pet.dizzy_timer.start(1000)
                    pet.audio.play_sound('bump')
            elif x >= pet.screen_geo.width() - pet.width():
                x = pet.screen_geo.width() - pet.width()
                pet.velocity_x *= -self.restitution
                if abs(pet.velocity_x) > 30 and pet.state not in ['dizzy', 'funny_face']:
                    pet.state = 'dizzy'
                    pet.dizzy_timer.start(2500)
                    pet.audio.play_sound('bump')
                elif abs(pet.velocity_x) > 15 and pet.state not in ['dizzy', 'funny_face']:
                    pet.state = 'funny_face'
                    pet.dizzy_timer.start(1000)
                    pet.audio.play_sound('bump')
                    
        pet.move(int(x), int(y))
