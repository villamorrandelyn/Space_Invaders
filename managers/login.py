import pygame

from db import login_player, register_player
from managers import ui
from managers.assets import find_asset
from managers.sound_manager import sounds


class TextInput:

    def __init__(self, rect, placeholder, password=False, max_len=30):
        self.rect = rect
        self.placeholder = placeholder
        self.password = password
        self.max_len = max_len
        self.text = ""
        self.active = False
        self.show = False

        self.eye_rect = pygame.Rect(rect.right - 46, rect.y, 46, rect.height)

    def clear(self):
        self.text = ""
        self.active = False
        self.show = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.password and self.eye_rect.collidepoint(event.pos):
                self.show = not self.show
                self.active = True
            else:
                self.active = self.rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

            elif event.key in (
                pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB
            ):
                pass

            elif event.unicode and event.unicode.isprintable():
                if len(self.text) < self.max_len:
                    self.text += event.unicode

    def draw(self, screen):
        ui.draw_input(
            screen, self.rect, self.placeholder, self.text,
            self.active, password=self.password, show=self.show
        )


class LoginManager:
    def __init__(self, screen, w, h):
        self.screen = screen
        self.w = w
        self.h = h

        self.logged_in_player = None
        self.view = "login"
        self.message = ""
        self.message_ok = False
        self.background = self.load_background()

        pw = 420
        px = w // 2 - pw // 2
        fx = px + 30
        fw = pw - 60

        self.login_panel = pygame.Rect(px, 200, pw, 262)
        self.create_panel = pygame.Rect(px, 187, pw, 314)

        L = self.login_panel
        C = self.create_panel

        self.login_inputs = [
            TextInput(pygame.Rect(fx, L.y + 56, fw, 42), "Username"),
            TextInput(pygame.Rect(fx, L.y + 106, fw, 42), "Password",
                      password=True, max_len=50),
        ]
        self.login_btn = pygame.Rect(fx, L.y + 174, fw, 44)
        self.login_msg_y = L.y + 153

        self.create_inputs = [
            TextInput(pygame.Rect(fx, C.y + 56, fw, 42), "Player Name"),
            TextInput(pygame.Rect(fx, C.y + 106, fw, 42), "Password",
                      password=True, max_len=50),
            TextInput(pygame.Rect(fx, C.y + 156, fw, 42),
                      "Confirm Password", password=True, max_len=50),
        ]
        self.create_btn = pygame.Rect(fx, C.y + 228, fw, 44)
        self.create_msg_y = C.y + 203

        self.link_rect = pygame.Rect(0, 0, 0, 0)
        self.login_inputs[0].active = True

    def load_background(self):
        try:
            image = pygame.image.load(find_asset("ranback.png")).convert()
            return pygame.transform.smoothscale(image, (self.w, self.h))

        except (FileNotFoundError, pygame.error) as e:
            print(f"Cannot load ranback.png: {e}")
            return None

    def reset(self):
        self.logged_in_player = None
        self.switch_view("login")

    def inputs(self):
        return (
            self.login_inputs
            if self.view == "login"
            else self.create_inputs
        )

    def set_message(self, text, ok=False):
        self.message = text
        self.message_ok = ok

    def switch_view(self, view, message="", ok=False):
        self.view = view

        for box in self.login_inputs + self.create_inputs:
            box.clear()

        self.inputs()[0].active = True
        self.set_message(message, ok)

    def cycle_focus(self):
        boxes = self.inputs()
        current = -1

        for i, box in enumerate(boxes):
            if box.active:
                current = i

        for box in boxes:
            box.active = False

        boxes[(current + 1) % len(boxes)].active = True

    def submit_login(self):
        username = self.login_inputs[0].text.strip()
        password = self.login_inputs[1].text

        if not username or not password:
            self.set_message("FILL IN ALL FIELDS")
            return

        player = login_player(username, password)

        if player is None:
            self.set_message("INVALID USERNAME OR PASSWORD")
            return

        self.set_message("")
        self.logged_in_player = player

        for box in self.login_inputs:
            box.clear()

    def submit_create(self):
        username = self.create_inputs[0].text.strip()
        password = self.create_inputs[1].text
        confirm = self.create_inputs[2].text

        if not username or not password or not confirm:
            self.set_message("FILL IN ALL FIELDS")
            return

        if len(username) < 3:
            self.set_message("NAME MUST BE AT LEAST 3 CHARACTERS")
            return

        if len(password) < 4:
            self.set_message("PASSWORD MUST BE AT LEAST 4 CHARACTERS")
            return

        if password != confirm:
            self.set_message("PASSWORDS DO NOT MATCH")
            return

        ok, msg = register_player(username, password)

        if ok:
            self.switch_view("login", "ACCOUNT CREATED! PLEASE LOGIN", True)
        else:
            self.set_message(msg)

    def submit(self):
        if self.view == "login":
            self.submit_login()
        else:
            self.submit_create()

    def handle_events(self, events):
        for event in events:
            for box in self.inputs():
                box.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.cycle_focus()

                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.submit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                btn = (
                    self.login_btn
                    if self.view == "login"
                    else self.create_btn
                )

                if btn.collidepoint(event.pos):
                    sounds.play_button()
                    self.submit()

                elif self.link_rect.collidepoint(event.pos):
                    sounds.play_button()

                    if self.view == "login":
                        self.switch_view("create")
                    else:
                        self.switch_view("login")

    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            ui.draw_background(self.screen, self.w, self.h, dark=True)

        ui.draw_invader(self.screen, 42, 14, 3, (160, 235, 110))
        ui.draw_outline_text(
            self.screen, "SPACE INVADERS", 28, (150, 255, 110),
            (8, 60, 20), (170, 38), 2
        )

        mouse = pygame.mouse.get_pos()

        if self.view == "login":
            panel = self.login_panel
            heading = "LOGIN"
            btn = self.login_btn
            btn_text = "Login"
            msg_y = self.login_msg_y
            link_y = panel.y + 240
        else:
            panel = self.create_panel
            heading = "CREATE ACCOUNT"
            btn = self.create_btn
            btn_text = "Sign Up"
            msg_y = self.create_msg_y
            link_y = panel.y + 294

        ui.draw_card(self.screen, panel)

        ui.draw_text(
            self.screen, heading, 22, ui.TEXT_DARK,
            center=(panel.centerx, panel.y + 28), bold=True
        )

        for box in self.inputs():
            box.draw(self.screen)

        if self.message:
            color = ui.NEON if self.message_ok else ui.NEON_RED
            ui.draw_text(
                self.screen, self.message, 13, color,
                center=(panel.centerx, msg_y + 9), bold=True
            )

        ui.draw_button(
            self.screen, btn, btn_text, btn.collidepoint(mouse), size=19
        )

        if self.view == "login":
            self.link_rect = ui.draw_link_line(
                self.screen, "Don't have an account?", "Create Account",
                link_y, self.w // 2
            )
        else:
            self.link_rect = ui.draw_link_line(
                self.screen, "Already have an account?", "Login",
                link_y, self.w // 2
            )