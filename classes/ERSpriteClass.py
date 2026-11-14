import pygame

class ERSpriteClass:
    def __init__(self, image_path: str, sprite_size: tuple[int, int], frameRate: int):
        self.image_path = image_path
        self.sprite_size = sprite_size
        self.frameRate = frameRate
        
    def play_animation(self, screen: pygame.Surface, position: tuple[int, int], elapsed_time: float):
        # Load the sprite sheet
        sprite_sheet = pygame.image.load(self.image_path).convert_alpha()
        
        # Calculate the number of frames in the sprite sheet
        sheet_width, _ = sprite_sheet.get_size()
        frame_width, frame_height = self.sprite_size
        num_frames = sheet_width // frame_width
        
        # Calculate the current frame based on elapsed time and frame rate
        current_frame = int((elapsed_time * self.frameRate) % num_frames)
        
        # Calculate the rectangle for the current frame
        frame_rect = pygame.Rect(current_frame * frame_width, 0, frame_width, frame_height)
        
        # Blit the current frame onto the screen at the specified position
        screen.blit(sprite_sheet, position, frame_rect)