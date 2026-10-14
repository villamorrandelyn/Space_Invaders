import pygame

from managers import ui


class MobileButtons:
    def __init__(self):
        self.left = pygame.Rect(20, 520, 80, 60)
        self.right = pygame.Rect(120, 520, 80, 60)
        self.fire = pygame.Rect(680, 520, 100, 60)

    def draw_one(self, screen, rect, icon, base, pressed):
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        alpha = 215 if pressed else 150

        pygame.draw.rect(
            surface, (*base, alpha), surface.get_rect(),
            border_radius=18
        )
        pygame.draw.rect(
            surface, (210, 245, 210, 230), surface.get_rect(), 2,
            border_radius=18
        )
        screen.blit(surface, rect.topleft)

        ui.draw_icon(screen, icon, rect.centerx, rect.centery,
                     (255, 255, 255))

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        down = pygame.mouse.get_pressed()[0]

        self.draw_one(screen, self.left, "arrow_left", (25, 90, 60),
                      down and self.left.collidepoint(mouse))
        self.draw_one(screen, self.right, "arrow_right", (25, 90, 60),
                      down and self.right.collidepoint(mouse))
        self.draw_one(screen, self.fire, "fire", (200, 70, 60),
                      down and self.fire.collidepoint(mouse))

    def handle_mouse(self, player, events):
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:
            mouse_pos = pygame.mouse.get_pos()
            if self.left.collidepoint(mouse_pos):
                player.move_left()
            if self.right.collidepoint(mouse_pos):
                player.move_right()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.fire.collidepoint(event.pos):
                    return True
        return False