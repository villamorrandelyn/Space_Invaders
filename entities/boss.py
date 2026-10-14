import math

import pygame

from managers.assets import find_asset, find_asset_like

BOSS_SIZE = 150


class BossShot:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def get_rect(self):
        return pygame.Rect(int(self.x) - 8, int(self.y) - 8, 16, 16)

    def draw(self, screen):
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(screen, (255, 120, 40), pos, 9)
        pygame.draw.circle(screen, (255, 200, 90), pos, 6)
        pygame.draw.circle(screen, (255, 255, 225), pos, 3)


class Boss:
    def __init__(self, level, screen_width):
        self.level = level
        self.screen_width = screen_width

        self.image = self.load_image()
        self.width, self.height = self.image.get_size()

        self.max_hp = 12 + 3 * level
        self.hp = self.max_hp

        self.x = screen_width / 2 - self.width / 2
        self.y = -self.height - 20

        self.state = "entering"
        self.fight_time = 0
        self.flash = 0
        self.shots = []
        self.shoot_timer = 90

    def load_image(self):
        image = None
        path = find_asset_like("boss")

        if path:
            try:
                image = pygame.image.load(path).convert_alpha()
            except pygame.error:
                image = None

        if image is None:
            image = pygame.image.load(
                find_asset("ranmy.png")
            ).convert_alpha()
            image.fill((255, 110, 110, 255),
                       special_flags=pygame.BLEND_RGBA_MULT)

        w, h = image.get_size()
        scale = BOSS_SIZE / max(w, h)

        return pygame.transform.smoothscale(
            image, (int(w * scale), int(h * scale))
        )

    def get_rect(self):
        return pygame.Rect(
            int(self.x), int(self.y), self.width, self.height
        ).inflate(-16, -16)

    def take_hit(self):
        self.hp -= 1
        self.flash = 6

    def fire(self, target_x):
        cx = self.x + self.width / 2
        cy = self.y + self.height - 20

        if self.level >= 15:
            speeds = (-4, -2, 0, 2, 4)
        elif self.level >= 10:
            speeds = (-2.5, 0, 2.5)
        else:
            aim = max(-3, min(3, (target_x - cx) / 60))
            speeds = (aim,)

        for vx in speeds:
            self.shots.append(BossShot(cx, cy, vx, 5))

    def update(self, target_x):
        if self.flash > 0:
            self.flash -= 1

        if self.state == "entering":
            self.y += 2

            if self.y >= 95:
                self.y = 95
                self.state = "fighting"

        else:
            self.fight_time += 1

            amp = (self.screen_width - self.width) / 2 - 10
            speed = 0.02 + 0.0015 * self.level

            self.x = (
                self.screen_width / 2 - self.width / 2
                + amp * math.sin(self.fight_time * speed)
            )

            self.shoot_timer -= 1

            if self.shoot_timer <= 0:
                self.fire(target_x)
                self.shoot_timer = max(30, 80 - 3 * self.level)

        for shot in self.shots:
            shot.update()

        self.shots = [
            s for s in self.shots
            if -20 < s.y < 650 and -20 < s.x < 820
        ]

    def draw(self, screen):
        screen.blit(self.image, (int(self.x), int(self.y)))

        if self.flash > 0:
            tmp = self.image.copy()
            tmp.fill((90, 90, 90, 0), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(tmp, (int(self.x), int(self.y)))

        for shot in self.shots:
            shot.draw(screen)

        self.draw_hp_bar(screen)

    def draw_hp_bar(self, screen):
        bar_w = max(90, int(self.width * 0.8))
        bar_h = 7
        bx = int(self.x + self.width / 2 - bar_w / 2)
        by = int(self.y + self.height + 6)

        ratio = max(0.0, self.hp / self.max_hp)

        if ratio > 0.5:
            fill = (90, 210, 100)
        elif ratio > 0.25:
            fill = (235, 200, 60)
        else:
            fill = (230, 70, 70)

        back = pygame.Rect(bx, by, bar_w, bar_h)
        pygame.draw.rect(screen, (10, 44, 40), back, border_radius=4)

        if ratio > 0:
            pygame.draw.rect(
                screen, fill,
                (bx, by, max(4, int(bar_w * ratio)), bar_h),
                border_radius=4
            )

        pygame.draw.rect(screen, (210, 245, 210), back, 1,
                         border_radius=4)