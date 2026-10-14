import pygame

from managers import ui
from managers.settings_manager import load_settings, save_settings
from managers.sound_manager import sounds


class SettingsScreen:
    def __init__(self, screen, w, h):
        self.screen = screen
        self.w = w
        self.h = h
        self.action = None

        self.settings = load_settings()
        self.settings.setdefault("sound_enabled", True)
        self.settings.setdefault("music_enabled", True)
        self.settings.setdefault("mobile_controls", False)

        cx = w // 2
        self.back_btn = pygame.Rect(24, 22, 44, 44)
        self.card = pygame.Rect(cx - 250, 110, 500, 300)

        self.rows = []
        items = [
            ("sound_enabled", "Sounds", ""),
            ("music_enabled", "Music", ""),
            ("mobile_controls", "Mobile Control", "Use touch controls"),
        ]

        for i, (key, label, hint) in enumerate(items):
            rect = pygame.Rect(cx - 220, 130 + i * 90, 440, 74)
            self.rows.append((key, label, hint, rect))

    def draw(self):
        cx = self.w // 2
        mouse = pygame.mouse.get_pos()

        ui.draw_background(self.screen, self.w, self.h)
        ui.draw_back_button(
            self.screen, self.back_btn, self.back_btn.collidepoint(mouse)
        )

        ui.draw_outline_text(
            self.screen, "SETTINGS", 38, (150, 255, 110),
            (8, 60, 20), (cx, 45)
        )

        ui.draw_card(self.screen, self.card)

        for key, label, hint, rect in self.rows:
            hover = rect.collidepoint(mouse)
            pygame.draw.rect(
                self.screen,
                (16, 62, 36) if hover else (8, 36, 22),
                rect, border_radius=16
            )
            pygame.draw.rect(
                self.screen, (40, 150, 80), rect, 2, border_radius=16
            )

            if hint:
                ui.draw_text(self.screen, label, 20, ui.TEXT_DARK,
                             topleft=(rect.x + 24, rect.y + 14), bold=True)
                ui.draw_text(self.screen, hint, 14, ui.TEXT_MUTED,
                             topleft=(rect.x + 24, rect.y + 43))
            else:
                ui.draw_text(self.screen, label, 20, ui.TEXT_DARK,
                             topleft=(rect.x + 24, rect.centery - 12),
                             bold=True)

            toggle = pygame.Rect(
                rect.right - 90, rect.centery - 17, 70, 34
            )
            ui.draw_toggle(self.screen, toggle, self.settings[key])

    def handle_events(self, events):
        self.action = None

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse_click(event.pos)

    def mouse_click(self, pos):
        if self.back_btn.collidepoint(pos):
            sounds.play_button()
            self.action = "back"
            return

        for key, _, _, rect in self.rows:
            if rect.collidepoint(pos):
                sounds.play_button()
                self.settings[key] = not self.settings[key]
                save_settings(self.settings)
                sounds.refresh()
                return