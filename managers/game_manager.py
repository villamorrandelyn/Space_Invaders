import random
import pygame

from entities.player import Player
from entities.enemy import Enemy
from entities.bullet import Bullet
from entities.button import MobileButtons
from entities.boss import Boss

from db import save_score
from managers import ui
from managers.live_bg import LiveBackground
from managers.settings_manager import load_settings
from managers.sound_manager import sounds


class GameManager:
    def __init__(self, screen, w, h):
        self.screen = screen
        self.w = w
        self.h = h

        self.current_player_id = None
        self.player_name = "PLAYER"
        self.game_state = "playing"

        self.player = None
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.shoot_cooldown = 0
        self.drop_timer = 0
        self.drop_interval = 90
        self.banner_timer = 0
        self.score_saved = False
        self.mobile_on = False
        self.mobile = MobileButtons()
        self.boss = None
        self.bg = LiveBackground(w, h)

        cx = w // 2
        self.pause_btn = pygame.Rect(w - 41, 6, 30, 30)
        self.card = pygame.Rect(cx - 190, 175, 380, 285)
        self.btn_a = pygame.Rect(cx - 150, 330, 300, 46)
        self.btn_b = pygame.Rect(cx - 150, 386, 300, 46)

    def start_again(self):
        self.player = Player(self.w, self.h)
        self.bullets = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.shoot_cooldown = 0
        self.score_saved = False
        self.mobile_on = load_settings().get("mobile_controls", False)
        self.spawn_wave()
        self.game_state = "playing"

    def spawn_wave(self):
        self.boss = None

        if self.level % 5 == 0:
            self.boss = Boss(self.level, self.w)
            self.enemies = []
            self.banner_timer = 120
            return

        count = min(4 + self.level, 8)
        speed = min(4 + 0.3 * (self.level - 1), 7)

        self.enemies = [
            Enemy(i, count, self.w) for i in range(count)
        ]

        for enemy in self.enemies:
            enemy.speed = speed

        self.drop_interval = max(35, 95 - 8 * (self.level - 1))
        self.drop_timer = self.drop_interval
        self.banner_timer = 90

    def shoot(self):
        if self.shoot_cooldown > 0:
            return

        self.shoot_cooldown = 15
        x = self.player.x + self.player.width // 2 - 16
        self.bullets.append(Bullet(x, self.player.y))

    def save_my_score(self):
        if self.score_saved:
            return

        self.score_saved = True

        if self.current_player_id is not None and self.score > 0:
            save_score(self.current_player_id, self.score)

    def end_game(self):
        self.game_state = "game_over"
        self.save_my_score()

    def go_home(self):
        self.save_my_score()
        self.game_state = "back_home"

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.key_down(event)

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                self.mouse_click(event.pos)

        if self.game_state == "playing":
            self.update_playing(events)

    def key_down(self, event):
        pause_keys = (pygame.K_ESCAPE, pygame.K_p)

        if self.game_state == "playing" and event.key in pause_keys:
            self.game_state = "paused"

        elif self.game_state == "paused" and event.key in pause_keys:
            self.game_state = "playing"

        elif self.game_state == "game_over":
            if event.key == pygame.K_RETURN:
                self.start_again()
            elif event.key == pygame.K_ESCAPE:
                self.go_home()

    def mouse_click(self, pos):
        if self.game_state == "playing":
            if self.pause_btn.collidepoint(pos):
                sounds.play_button()
                self.game_state = "paused"

        elif self.game_state == "paused":
            if self.btn_a.collidepoint(pos):
                sounds.play_button()
                self.game_state = "playing"

            elif self.btn_b.collidepoint(pos):
                sounds.play_button()
                self.go_home()

        elif self.game_state == "game_over":
            if self.btn_a.collidepoint(pos):
                sounds.play_button()
                self.start_again()

            elif self.btn_b.collidepoint(pos):
                sounds.play_button()
                self.go_home()

    def update_playing(self, events):
        player = self.player
        player.update()

        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.shoot()

        if self.mobile_on and self.mobile.handle_mouse(player, events):
            self.shoot()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        for bullet in self.bullets:
            bullet.update()

        self.bullets = [b for b in self.bullets if b.is_active]

        for enemy in self.enemies:
            enemy.update()

        self.drop_timer -= 1

        if self.drop_timer <= 0:
            waiting = [
                e for e in self.enemies
                if e.active and e.state == "waiting"
            ]

            divers = min(1 + self.level // 4, 3)

            for enemy in random.sample(
                waiting, min(divers, len(waiting))
            ):
                enemy.start_drop(player.x, player.y)

            self.drop_timer = self.drop_interval

        for bullet in self.bullets:
            for enemy in self.enemies:
                if not enemy.active:
                    continue

                if bullet.get_rect().colliderect(enemy.get_rect()):
                    enemy.active = False
                    bullet.is_active = False
                    self.score += 10
                    sounds.play_hit()
                    break

        if not player.is_blinking:
            player_box = player.get_rect().inflate(-30, -30)

            for enemy in self.enemies:
                if not enemy.active:
                    continue

                if enemy.get_rect().inflate(-30, -30).colliderect(
                    player_box
                ):
                    enemy.active = False

                    if self.hurt_player():
                        return

                    break

        if player.is_blinking and player.blink_timer >= 60:
            player.is_blinking = False
            player.visible = True

        if self.boss:
            if self.update_boss():
                return

        elif all(not e.active for e in self.enemies):
            self.level += 1
            self.spawn_wave()

        if self.banner_timer > 0:
            self.banner_timer -= 1

    def hurt_player(self):
        self.lives -= 1
        sounds.play_hit()

        if self.lives <= 0:
            self.end_game()
            return True

        self.player.is_blinking = True
        self.player.blink_timer = 0
        return False

    def update_boss(self):
        boss = self.boss
        player = self.player

        boss.update(player.x + player.width // 2)

        for bullet in self.bullets:
            if not bullet.is_active or boss.state != "fighting":
                continue

            if bullet.get_rect().colliderect(boss.get_rect()):
                bullet.is_active = False
                boss.take_hit()
                sounds.play_hit()

                if boss.hp <= 0:
                    self.score += 200
                    self.level += 1
                    self.spawn_wave()
                    return False

        if not player.is_blinking:
            box = player.get_rect().inflate(-30, -30)

            for shot in boss.shots:
                if shot.get_rect().colliderect(box):
                    boss.shots.remove(shot)
                    return self.hurt_player()

        return False

    def draw(self):
        self.bg.draw(self.screen, self.game_state == "playing")

        for enemy in self.enemies:
            enemy.draw(self.screen)

        if self.boss:
            self.boss.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        self.player.draw(self.screen)

        ui.draw_hud(self.screen, self.w, self.score,
                    self.lives, self.level)

        self.draw_pause_button()

        if self.mobile_on:
            self.mobile.draw(self.screen)

        if self.banner_timer > 0 and self.game_state == "playing":
            label = (
                f"BOSS - LEVEL {self.level}" if self.boss
                else f"LEVEL {self.level}"
            )
            pw = 200 if self.boss else 140
            popup = pygame.Rect(self.w // 2 - pw // 2, 46, pw, 32)
            pygame.draw.rect(self.screen, ui.GREEN_DARK, popup.move(0, 3),
                             border_radius=16)
            pygame.draw.rect(self.screen, ui.GREEN, popup,
                             border_radius=16)
            ui.draw_text(self.screen, label, 17,
                         (255, 255, 255), center=popup.center, bold=True)

        if self.game_state == "paused":
            self.draw_overlay("PAUSED", "Take a breather, pilot!",
                              "Resume", "Home")

        elif self.game_state == "game_over":
            self.draw_overlay(
                "GAME OVER", f"Score: {self.score}  |  Level: {self.level}",
                "Play Again", "Home"
            )

    def draw_pause_button(self):
        rect = self.pause_btn
        pygame.draw.circle(self.screen, (10, 44, 40), rect.center, 15)
        pygame.draw.circle(self.screen, (90, 175, 125), rect.center,
                           15, 2)

        cx, cy = rect.center
        pygame.draw.rect(self.screen, (255, 255, 255),
                         (cx - 5, cy - 6, 4, 12), border_radius=2)
        pygame.draw.rect(self.screen, (255, 255, 255),
                         (cx + 1, cy - 6, 4, 12), border_radius=2)

    def draw_overlay(self, title, subtitle, label_a, label_b):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 15, 10, 170))
        self.screen.blit(overlay, (0, 0))

        ui.draw_card(self.screen, self.card)

        cx = self.card.centerx
        mouse = pygame.mouse.get_pos()

        ui.draw_text(self.screen, title, 32, ui.TEXT_DARK,
                     center=(cx, self.card.y + 52), bold=True)
        ui.draw_text(self.screen, subtitle, 17, ui.TEXT_MUTED,
                     center=(cx, self.card.y + 100))

        ui.draw_button(self.screen, self.btn_a, label_a,
                       self.btn_a.collidepoint(mouse), size=19)
        ui.draw_button(self.screen, self.btn_b, label_b,
                       self.btn_b.collidepoint(mouse),
                       style="light", size=19)