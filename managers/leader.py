import pygame

from db import load_leaderboard
from managers import ui
from managers.sound_manager import sounds


class Leader:
    def __init__(self, screen, w, h, player=None):
        self.screen = screen
        self.w = w
        self.h = h
        self.player = player
        self.action = None

        self.back_btn = pygame.Rect(24, 22, 44, 44)
        self.rows = load_leaderboard()[:10]

        row_h = 38
        body = len(self.rows) * row_h if self.rows else 70
        card_w = 460
        card_h = 14 + 34 + 10 + body + 10

        self.row_h = row_h
        self.card = pygame.Rect(
            w // 2 - card_w // 2, 100, card_w, card_h
        )

    def my_id(self):
        if isinstance(self.player, dict):
            return self.player.get("player_id")

        return None

    def draw(self):
        cx = self.w // 2
        mouse = pygame.mouse.get_pos()

        ui.draw_background(self.screen, self.w, self.h)
        ui.draw_back_button(
            self.screen, self.back_btn, self.back_btn.collidepoint(mouse)
        )

        ui.draw_outline_text(
            self.screen, "LEADERBOARD", 38, (150, 255, 110),
            (8, 60, 20), (cx, 45)
        )

        ui.draw_card(self.screen, self.card)

        left = self.card.x + 14
        right = self.card.right - 14
        inner_w = right - left

        head = pygame.Rect(left, self.card.y + 14, inner_w, 34)
        pygame.draw.rect(self.screen, (14, 60, 34), head,
                         border_radius=10)

        ui.draw_text(self.screen, "Player", 16, ui.NEON,
                     topleft=(left + 16, head.y + 7), bold=True)

        score_head = ui.font(16, True).size("Score")[0]
        ui.draw_text(self.screen, "Score", 16, ui.NEON,
                     topleft=(right - 16 - score_head, head.y + 7),
                     bold=True)

        if not self.rows:
            ui.draw_text(self.screen, "No scores yet", 20,
                         ui.TEXT_MUTED,
                         center=(cx, head.bottom + 38), bold=True)
            return

        for index, row in enumerate(self.rows):
            y = head.bottom + 10 + index * self.row_h
            rect = pygame.Rect(left, y, inner_w, self.row_h - 4)
            mine = row.get("player_id") == self.my_id()

            pygame.draw.rect(
                self.screen,
                (20, 90, 44) if mine else (8, 36, 22),
                rect, border_radius=10
            )

            if mine:
                pygame.draw.rect(self.screen, ui.NEON, rect, 1,
                                 border_radius=10)

            name = str(row.get("username", "PLAYER"))[:20]
            score = str(row.get("score", 0))
            score_w = ui.font(17, True).size(score)[0]

            ui.draw_text(self.screen, name, 17, ui.TEXT_DARK,
                         topleft=(left + 16, y + 8), bold=mine)
            ui.draw_text(self.screen, score, 17, ui.NEON,
                         topleft=(right - 16 - score_w, y + 8),
                         bold=True)

    def handle_events(self, events):
        self.action = None

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_btn.collidepoint(event.pos):
                    sounds.play_button()
                    self.action = "back"