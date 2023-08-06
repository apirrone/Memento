import pygame


# Chat window on the right of the screen
class Chat:
    def __init__(self, frame_getter):
        ws = frame_getter.window_size
        self.w = ws[0] // 5
        self.x = ws[0] - self.w
        self.y = 0
        self.h = ws[1]

        self.active = False
        self.input = ""

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
        self.input = ""

    # Draw chatbox with input region at the bottom
    def draw(self, screen):
        if not self.active:
            return

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (self.x, self.y, self.w, self.h),
            border_radius=10,
        )

        font = pygame.font.SysFont("Arial", 20)
        text = font.render(self.input, True, (0, 0, 0))
        screen.blit(text, (self.x + 10, self.y + 10))

        if len(self.input) > 0:
            cursor_pos = font.size(self.input)[0] + 10
        else:
            cursor_pos = 10

        if pygame.time.get_ticks() % 1000 < 500:
            pygame.draw.rect(
                screen,
                (0, 0, 0),
                (
                    self.x + cursor_pos,
                    self.y + 10,
                    2,
                    20,
                ),
            )

