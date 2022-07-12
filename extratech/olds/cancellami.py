# Simple pygame program

# Import and initialize the pygame library
import pygame
pygame.init()

size = [500, 200]
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()
font  = pygame.font.Font(None, 25)
# Define some colors
BLACK         = (0, 0, 0)
WHITE         = (255, 255, 255)
timecode      = '00:00:00:00'

done = False
frame_count = 0
frame_rate = 25
start_time = 90

# Run until the user asks to quit
running = True
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    screen.fill((255, 255, 255))

    # Draw a solid blue circle in the center
    pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()