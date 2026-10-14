import pygame

from managers import ui
from managers.assets import find_asset
from managers.sound_manager import sounds


class Home:
    def __init__(self, screen, w, h, player=None):
        self.screen = screen
        self.w = w
        self.h = h
        self.player = player
        self.action = None
        self.confirm = False

        self.background = self.load_background()

        cx = w // 2
        bw = 360

        self.play_btn = pygame.Rect(cx - bw // 2, 208, bw, 54)

        self.buttons = {}
        y = 280

        for name in ("leaderboard", "settings", "profile", "logout"):
            self.buttons[name] = pygame.Rect(cx - bw // 2, y, bw, 40)
            y += 46

        self.dialog = pygame.Rect(cx - 190, 190, 380, 245)
        self.yes_btn = pygame.Rect(cx - 150, 316, 300, 46)
        self.cancel_btn = pygame.Rect(cx - 150, 372, 300, 46)

    def load_background(self):
        try:
            image = pygame.image.load(
                find_asset("ranmenu.png")
            ).convert()

            return pygame.transform.smoothscale(
                image, (self.w, self.h)
            )

        except (FileNotFoundError, pygame.error) as e:
            print(f"Cannot load ranmenu.png: {e}")
            return None

    def username(self):
        if isinstance(self.player, dict):
            return str(self.player.get("username", "PLAYER"))

        if self.player:
            return str(self.player)

        return "PLAYER"

    def draw(self):
        cx = self.w // 2
        mouse = pygame.mouse.get_pos()
        active = not self.confirm

        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            ui.draw_background(self.screen, self.w, self.h)
            ui.draw_invader(self.screen, cx, 20, 5, (160, 235, 110))

        ui.draw_outline_text(
            self.screen, "SPACE INVADERS", 42, (150, 255, 110),
            (8, 60, 20), (cx, 160), 3
        )

        ui.draw_text(
            self.screen, "Welcome, " + self.username(), 17,
            ui.TEXT_LIGHT, center=(cx, 192), bold=True
        )

        ui.draw_button(
            self.screen, self.play_btn, "START GAME",
            active and self.play_btn.collidepoint(mouse),
            size=22, icon="play"
        )

        labels = {
            "leaderboard": ("LEADERBOARD", "trophy"),
            "settings": ("SETTINGS", "gear"),
            "profile": ("PROFILE", "user"),
            "logout": ("LOGOUT", "logout"),
        }

        for name, rect in self.buttons.items():
            text, icon = labels[name]
            ui.draw_button(
                self.screen, rect, text,
                active and rect.collidepoint(mouse),
                style="light", size=17, icon=icon
            )

        if self.confirm:
            self.draw_confirm(mouse)

    def draw_confirm(self, mouse):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 15, 10, 170))
        self.screen.blit(overlay, (0, 0))

        ui.draw_card(self.screen, self.dialog)

        cx = self.dialog.centerx
        pygame.draw.circle(
            self.screen, (4, 20, 12), (cx, self.dialog.y + 6), 36
        )
        pygame.draw.circle(
            self.screen, ui.NEON, (cx, self.dialog.y + 6), 36, 2
        )
        ui.draw_invader(
            self.screen, cx, self.dialog.y - 12, 3, (160, 235, 110)
        )

        ui.draw_text(self.screen, "LOGOUT", 26, ui.TEXT_DARK,
                     center=(cx, self.dialog.y + 66), bold=True)

        ui.draw_text(
            self.screen, "Are you sure you want to log out?", 16,
            ui.TEXT_MUTED, center=(cx, self.dialog.y + 98)
        )

        ui.draw_button(
            self.screen, self.yes_btn, "Yes, Logout",
            self.yes_btn.collidepoint(mouse), size=19
        )

        ui.draw_button(
            self.screen, self.cancel_btn, "Cancel",
            self.cancel_btn.collidepoint(mouse), style="light", size=19
        )

    def handle_events(self, events):
        self.action = None

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse_click(event.pos)

    def mouse_click(self, pos):
        if self.confirm:
            if self.yes_btn.collidepoint(pos):
                sounds.play_button()
                self.confirm = False
                self.action = "logout"

            elif self.cancel_btn.collidepoint(pos):
                sounds.play_button()
                self.confirm = False

            return

        if self.play_btn.collidepoint(pos):
            sounds.play_button()
            self.action = "play"
            return

        for name, rect in self.buttons.items():
            if rect.collidepoint(pos):
                sounds.play_button()

                if name == "logout":
                    self.confirm = True
                else:
                    self.action = name

                return