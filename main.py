import pygame

pygame.init()

from managers.sound_manager import sounds
from managers.login import LoginManager
from managers.game_manager import GameManager
from managers.home import Home
from managers.profile import Profile
from managers.leader import Leader
from managers.settings_screen import SettingsScreen

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders by Villamor, Randelyn")

sounds.start()

login = LoginManager(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
game = GameManager(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

home = None
profile = None
leader = None
settings_screen = None
current_screen = "login"

clock = pygame.time.Clock()
running = True


def new_home():
    return Home(
        screen, SCREEN_WIDTH, SCREEN_HEIGHT, login.logged_in_player
    )


while running:

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            if current_screen == "game":
                game.save_my_score()

            running = False

    if current_screen == "login":

        login.handle_events(events)
        login.draw()

        if login.logged_in_player is not None:
            home = new_home()
            current_screen = "home"

    elif current_screen == "home":

        home.handle_events(events)
        home.draw()

        if home.action == "profile":
            home.action = None
            profile = Profile(
                screen, SCREEN_WIDTH, SCREEN_HEIGHT,
                login.logged_in_player
            )
            current_screen = "profile"

        elif home.action == "leaderboard":
            home.action = None
            leader = Leader(
                screen, SCREEN_WIDTH, SCREEN_HEIGHT,
                login.logged_in_player
            )
            current_screen = "leader"

        elif home.action == "settings":
            home.action = None
            settings_screen = SettingsScreen(
                screen, SCREEN_WIDTH, SCREEN_HEIGHT
            )
            current_screen = "settings"

        elif home.action == "play":
            home.action = None
            game.current_player_id = login.logged_in_player["player_id"]
            game.player_name = login.logged_in_player["username"]
            game.start_again()
            current_screen = "game"

        elif home.action == "logout":
            home.action = None
            login.logged_in_player = None
            login.reset()
            home = None
            profile = None
            leader = None
            current_screen = "login"

    elif current_screen == "profile":

        profile.handle_events(events)
        profile.draw()

        if profile.player is not None:
            login.logged_in_player = profile.player

        if profile.action == "back":
            profile.action = None
            home = new_home()
            current_screen = "home"

        elif profile.action == "deleted":
            login.logged_in_player = None
            login.reset()
            profile = None
            home = None
            leader = None
            current_screen = "login"

    elif current_screen == "leader":

        leader.handle_events(events)
        leader.draw()

        if leader.action == "back":
            leader.action = None
            home = new_home()
            current_screen = "home"

    elif current_screen == "settings":

        settings_screen.handle_events(events)
        settings_screen.draw()

        if settings_screen.action == "back":
            settings_screen.action = None
            home = new_home()
            current_screen = "home"

    elif current_screen == "game":

        game.update(events)
        game.draw()

        if game.game_state == "back_home":
            game.game_state = "playing"
            home = new_home()
            current_screen = "home"

    pygame.display.update()
    clock.tick(60)

pygame.quit()