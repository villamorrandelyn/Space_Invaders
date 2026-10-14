import os
import pygame

from managers.settings_manager import load_settings

SOUND_DIR = os.path.join("assets", "sounds")


class SoundManager:
    def __init__(self):
        self.ready = False
        self.button_sound = None
        self.hit_sound = None
        self.settings = {}

    def start(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.ready = True
        except pygame.error as e:
            print(f"Sound Error: {e}")
            return

        self.button_sound = self._load("ranbutton.mp3")
        self.hit_sound = self._load("ranllet.mp3")
        self.refresh()

    def _load(self, name):
        try:
            return pygame.mixer.Sound(os.path.join(SOUND_DIR, name))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Cannot load {name}: {e}")
            return None

    def refresh(self):
        if not self.ready:
            return

        self.settings = load_settings()
        volume = max(0, min(100, self.settings.get("sound_volume", 50))) / 100

        for snd in (self.button_sound, self.hit_sound):
            if snd:
                snd.set_volume(volume)

        pygame.mixer.music.set_volume(volume)

        if self.settings.get("music_enabled", True):
            self.play_music()
        else:
            pygame.mixer.music.stop()

    def play_music(self):
        if not self.ready:
            return

        if not self.settings.get("music_enabled", True):
            return

        if pygame.mixer.music.get_busy():
            return

        try:
            pygame.mixer.music.load(
                os.path.join(SOUND_DIR, "ranmusic.mp3")
            )
            pygame.mixer.music.play(-1)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Cannot play music: {e}")

    def _sfx_on(self):
        return self.ready and self.settings.get("sound_enabled", True)

    def play_button(self):
        if self._sfx_on() and self.button_sound:
            self.button_sound.play()

    def play_hit(self):
        if self._sfx_on() and self.hit_sound:
            self.hit_sound.play()


sounds = SoundManager()