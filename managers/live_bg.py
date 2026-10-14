import math
import random

import pygame

from managers import ui


class LiveBackground:

    SPEEDS = (0.3, 0.7, 1.3)
    SIZES = (1, 1, 2)

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.t = 0

        self.base = ui._build_background(w, h, True, stars=False)

        rnd = random.Random(11)

        self.stars = [
            [rnd.uniform(0, w), rnd.uniform(0, h * 0.66), i % 3,
             rnd.uniform(0, 6.28)]
            for i in range(90)
        ]

        self.flies = [
            [rnd.uniform(0, w), rnd.uniform(h * 0.6, h),
             rnd.uniform(0, 6.28), rnd.uniform(0.2, 0.6)]
            for _ in range(16)
        ]

        self.glows = [
            self.make_glow(150, (80, 210, 140)),
            self.make_glow(110, (140, 230, 120)),
        ]

        self.shooting = None
        self.shoot_wait = 200

    @staticmethod
    def make_glow(radius, color):
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

        for r in range(radius, 0, -5):
            alpha = int(60 * (1 - r / radius))
            pygame.draw.circle(
                surf, (*color, alpha), (radius, radius), r
            )

        return surf

    def draw(self, screen, animate=True):
        if animate:
            self.t += 1

        t = self.t
        w, h = self.w, self.h

        screen.blit(self.base, (0, 0))

        screen.blit(
            self.glows[0],
            (w * 0.25 + math.sin(t * 0.004) * 60 - 150,
             120 + math.cos(t * 0.003) * 20 - 150)
        )
        screen.blit(
            self.glows[1],
            (w * 0.75 + math.cos(t * 0.005) * 50 - 110,
             200 + math.sin(t * 0.004) * 30 - 110)
        )

        limit = h * 0.66

        for star in self.stars:
            layer = star[2]

            if animate:
                star[1] += self.SPEEDS[layer]

                if star[1] > limit:
                    star[1] = -2

            twinkle = 0.6 + 0.4 * math.sin(t * 0.06 + star[3])
            c = int(150 + 105 * twinkle)

            pygame.draw.circle(
                screen, (int(c * 0.9), c, int(c * 0.85)),
                (int(star[0]), int(star[1])), self.SIZES[layer]
            )

        self.draw_shooting_star(screen, animate)

        for fly in self.flies:
            if animate:
                fly[1] -= fly[3]
                fly[0] += math.sin(t * 0.03 + fly[2]) * 0.5

                if fly[1] < h * 0.55:
                    fly[1] = h + 5

            b = 0.5 + 0.5 * math.sin(t * 0.08 + fly[2])
            pos = (int(fly[0]), int(fly[1]))

            pygame.draw.circle(screen, (50, 120, 80), pos, 4)
            pygame.draw.circle(
                screen,
                (int(150 + 100 * b), 255, int(120 + 60 * b)),
                pos, 2
            )

    def draw_shooting_star(self, screen, animate):
        if self.shooting is None:
            if animate:
                self.shoot_wait -= 1

                if self.shoot_wait <= 0:
                    self.shooting = {
                        "x": random.uniform(self.w * 0.4, self.w),
                        "y": random.uniform(0, self.h * 0.25),
                        "life": 0,
                    }

            return

        star = self.shooting

        if animate:
            star["x"] -= 9
            star["y"] += 5
            star["life"] += 1

        fade = max(0.0, 1 - star["life"] / 45)
        color = (int(230 * fade), int(255 * fade), int(230 * fade))

        pygame.draw.line(
            screen, color, (star["x"], star["y"]),
            (star["x"] + 36, star["y"] - 20), 2
        )

        if star["life"] > 45:
            self.shooting = None
            self.shoot_wait = random.randint(240, 540)