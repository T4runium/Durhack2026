import pygame, sys

class Button:
    def __init__(self, image, xPos, yPos, text):
        self.image = image
        self.xPos = xPos
        self.yPos = yPos
        self.rect = self.image.get_rect(center=(self.xPos, self.yPos))
        self.text = text
        self.renderedText = main_font.render(self.text, True, "white")
        self.text.rect = self.text.get_rect(center=(self.xPos, yPos))
    
    def update(self):
        screen.blit(self.image, self.rect)
    
    def checkForClick(self, pos):
        if pos[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            print('button pressed')
    
    def changeColour(self, pos):
        if pos[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.renderedText = main_font.render(self.text, True, "green")
        else:
            self.renderedText = main_font.render(self.text, True, "white")