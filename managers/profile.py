import pygame

from db import (
    update_player_profile,
    delete_player,
    get_player_highest_score,
)
from managers import ui
from managers.sound_manager import sounds


class Profile:
    def __init__(self, screen, w, h, player=None):
        self.screen = screen
        self.w = w
        self.h = h
        self.action = None

        self.player = dict(player) if isinstance(player, dict) else {}
        self.values = {
            "username": str(self.player.get("username", "")),
        }
        self.active = "username"
        self.message = ""
        self.message_ok = False
        self.confirm_delete = False

        self.highest = get_player_highest_score(
            self.player.get("player_id")
        )

        cx = w // 2
        self.back_btn = pygame.Rect(24, 22, 44, 44)
        self.card = pygame.Rect(cx - 250, 95, 500, 400)

        x = self.card.x + 30
        self.user_box = pygame.Rect(x, 335, 440, 44)
        self.save_btn = pygame.Rect(x, 400, 210, 46)
        self.delete_btn = pygame.Rect(x + 230, 400, 210, 46)

        self.dialog = pygame.Rect(cx - 190, 185, 380, 270)
        self.yes_btn = pygame.Rect(cx - 150, 340, 300, 46)
        self.no_btn = pygame.Rect(cx - 150, 396, 300, 46)

    def draw(self):
        cx = self.w // 2
        mouse = pygame.mouse.get_pos()
        active = not self.confirm_delete

        ui.draw_background(self.screen, self.w, self.h)
        ui.draw_back_button(
            self.screen, self.back_btn,
            active and self.back_btn.collidepoint(mouse)
        )

        ui.draw_outline_text(
            self.screen, "PLAYER PROFILE", 38, (150, 255, 110),
            (8, 60, 20), (cx, 45)
        )

        ui.draw_card(self.screen, self.card)

        ax, ay = self.card.x + 85, 165
        pygame.draw.circle(self.screen, ui.NEON, (ax, ay), 48, 3)
        pygame.draw.circle(self.screen, (14, 60, 34), (ax, ay), 44)
        initial = (self.player.get("username") or "?")[0].upper()
        ui.draw_text(self.screen, initial, 46, ui.NEON,
                     center=(ax, ay), bold=True)

        ui.draw_text(
            self.screen, str(self.player.get("username", ""))[:20], 30,
            ui.TEXT_DARK, topleft=(self.card.x + 160, 150), bold=True
        )

        tile = pygame.Rect(self.card.x + 30, 235, 440, 70)
        pygame.draw.rect(self.screen, (10, 44, 28), tile,
                         border_radius=16)
        pygame.draw.rect(self.screen, (40, 150, 80), tile, 2,
                         border_radius=16)
        ui.draw_icon(self.screen, "trophy", tile.x + 45, tile.centery,
                     ui.GOLD)
        ui.draw_text(self.screen, "Highest Score", 15, ui.TEXT_MUTED,
                     topleft=(tile.x + 85, tile.y + 12))
        ui.draw_text(self.screen, f"{self.highest:,}", 28,
                     ui.NEON, topleft=(tile.x + 85, tile.y + 32),
                     bold=True)

        ui.draw_text(self.screen, "Username", 14, ui.TEXT_MUTED,
                     topleft=(self.user_box.x + 4, self.user_box.y - 20),
                     bold=True)
        ui.draw_input(self.screen, self.user_box, "Username",
                      self.values["username"], self.active == "username")

        ui.draw_button(self.screen, self.save_btn, "Save Changes",
                       active and self.save_btn.collidepoint(mouse),
                       size=18)
        ui.draw_button(self.screen, self.delete_btn, "Delete Account",
                       active and self.delete_btn.collidepoint(mouse),
                       style="light", size=18)

        if self.message:
            ui.draw_text(
                self.screen, self.message, 15,
                ui.NEON if self.message_ok else ui.RED,
                center=(cx, 468), bold=True
            )

        if self.confirm_delete:
            self.draw_confirm(mouse)

    def draw_confirm(self, mouse):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 15, 10, 170))
        self.screen.blit(overlay, (0, 0))

        ui.draw_card(self.screen, self.dialog)
        cx = self.dialog.centerx

        ui.draw_text(self.screen, "DELETE ACCOUNT?", 26, ui.RED,
                     center=(cx, self.dialog.y + 50), bold=True)
        ui.draw_text(self.screen, "This will permanently delete your",
                     16, ui.TEXT_MUTED,
                     center=(cx, self.dialog.y + 92))
        ui.draw_text(self.screen, "account and all your scores.",
                     16, ui.TEXT_MUTED,
                     center=(cx, self.dialog.y + 116))

        ui.draw_button(self.screen, self.yes_btn, "Yes, Delete",
                       self.yes_btn.collidepoint(mouse), size=19)
        ui.draw_button(self.screen, self.no_btn, "Cancel",
                       self.no_btn.collidepoint(mouse),
                       style="light", size=19)

    def handle_events(self, events):
        self.action = None

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse_click(event.pos)

            elif event.type == pygame.KEYDOWN and not self.confirm_delete:
                self.keyboard_input(event)

    def mouse_click(self, pos):
        if self.confirm_delete:
            if self.yes_btn.collidepoint(pos):
                sounds.play_button()
                self.delete_account()

            elif self.no_btn.collidepoint(pos):
                sounds.play_button()
                self.confirm_delete = False

            return

        if self.back_btn.collidepoint(pos):
            sounds.play_button()
            self.action = "back"

        elif self.user_box.collidepoint(pos):
            self.active = "username"

        elif self.save_btn.collidepoint(pos):
            sounds.play_button()
            self.save()

        elif self.delete_btn.collidepoint(pos):
            sounds.play_button()
            self.confirm_delete = True

    def keyboard_input(self, event):
        limits = {"username": 30}

        if event.key == pygame.K_BACKSPACE:
            self.values[self.active] = self.values[self.active][:-1]

        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.save()

        elif event.unicode and event.unicode.isprintable():
            if len(self.values[self.active]) < limits[self.active]:
                self.values[self.active] += event.unicode

    def save(self):
        username = self.values["username"].strip()

        if len(username) < 3:
            self.set_message("Username must be at least 3 characters")
            return

        if update_player_profile(
            self.player.get("player_id"), username
        ):
            self.player["username"] = username
            self.values["username"] = username
            self.set_message("Profile updated", True)
        else:
            self.set_message("Username already taken")

    def delete_account(self):
        if delete_player(self.player.get("player_id")):
            self.action = "deleted"
        else:
            self.confirm_delete = False
            self.set_message("Could not delete account")

    def set_message(self, text, ok=False):
        self.message = text
        self.message_ok = ok