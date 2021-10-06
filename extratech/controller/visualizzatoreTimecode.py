import threading
import pygame
timecode      = '00:00:00:00'
done = False
 
def run():
    pygame.init()
    size = [500, 200]
    screen = pygame.display.set_mode(size)

    clock = pygame.time.Clock()
    font  = pygame.font.Font(None, 25)

    pygame.display.set_caption("TIMECODE")

    # Define some colors
    BLACK         = (0, 0, 0)
    WHITE         = (255, 255, 255)

    frame_count = 0
    frame_rate = 25
    start_time = 90

    def doIt():
        global done
        while not done:
            screen.fill(WHITE)
            text = font.render(timecode, True, BLACK)
            screen.blit(text, [0, 0])
            clock.tick(frame_rate)
            pygame.display.flip()
        pygame.quit()

    # threading.Thread(target=doIt).start()
    doIt()

if __name__ == '__main__':
    run()
