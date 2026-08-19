import pygame, os
from jsonScript import jsonFileManagment
from mutagen import File

class audioPlayer():
    def __init__(self):
        super().__init__()
        # Initiliaze pygame mixer
        pygame.init()
        pygame.mixer.init()

        self.cache_data = jsonFileManagment("data.json",
                                            [
                                                ("appearance_mode", "System"),
                                                ("ui_scale", 100),
                                                ("volume", 0.7),
                                                ("muted", False),
                                                ("update_rate", 250),
                                                ("fade_ms", 500),
                                                ("load_queue", True),
                                                ("load_control", True)
                                            ])

        self.paused = True
        self.volume = self.cache_data.load()["volume"]
        self.muted = self.cache_data.load()["muted"]
        self.filepath = None
        self.fade_ms = self.cache_data.load()["fade_ms"]

        self.end_endevent = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.end_endevent)

        pygame.mixer.music.set_volume(self.volume)
        self.mute_calibrate()

    def load_music(self, path):
        pygame.mixer.music.load(path)
        
    def play_music(self):
        self.paused = False
        pygame.mixer.music.play(fade_ms=self.fade_ms)

    def stop_music(self):
        self.paused = True
        pygame.mixer.music.stop()

    def pause_music(self):            
        self.paused = True
        pygame.mixer.music.pause()

    def resume_music(self):
        self.paused = False
        pygame.mixer.music.unpause()

    def play_pause(self):
        if pygame.mixer.music.get_busy():
            self.pause_music()
        else:
            if self.paused:
                self.resume_music()
            else:
                self.play_music(-1)

    def rewind_music(self):
        pygame.mixer.music.play(fade_ms=self.fade_ms)

    def seek_player(self, seconds):
        self.paused = False
        pygame.mixer.music.play(start=seconds, fade_ms=self.fade_ms)
            
    def mute_music(self):
        if not self.muted:
            self.muted = True
            pygame.mixer.music.set_volume(0)
        else:
            self.muted = False
            pygame.mixer.music.set_volume(self.get_volume())
        
        if self.cache_data.load()["load_control"]:
            cache_save = self.cache_data.load()
            cache_save["muted"] = self.muted
            self.cache_data.save(cache_save)

    def mute_calibrate(self):
        if self.muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.get_volume())

    def check_for_end(self):
        for event in pygame.event.get():
            if event.type == self.end_endevent:
                return True
        return False

    def get_if_play_pause(self):
        if pygame.mixer.music.get_busy():
            return "Pause"
        else:
            if self.paused:
                return "Resume"
            else:
                return "Play"

    def get_playback_position(self):
        pos = pygame.mixer.music.get_pos()
        if pos < 0:
            return -1
        return pos // 1000
    
    def get_title(self, path):
        try:
            return File(path, easy=True).get("title", [os.path.basename(path)])[0]
        except Exception as e:
            return e

    def get_duration(self):
        try:
            audio = File(self.filepath)
            return int(audio.info.length)
        except:
            return 0
    
    def get_volume(self):
        return self.volume
    
    def get_int_volume(self):
        return int(self.volume * 100)
    
    def get_muted(self):
        return self.muted

    def get_busy(self):
        return pygame.mixer.music.get_busy()
    
    def get_paused(self):
        return self.paused
    
    def get_fade_ms(self):
        return self.fade_ms

    def temp_set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)
    
    def set_volume(self, volume):
        self.volume = volume
        self.muted = False
        pygame.mixer.music.set_volume(self.volume)
        if self.cache_data.load()["load_control"]:
            cache_save = self.cache_data.load()
            cache_save["volume"] = self.volume
            cache_save["muted"] = self.muted
            self.cache_data.save(cache_save)

    def set_fade_ms(self, fade_ms: int):
        self.fade_ms = fade_ms
        cache_save = self.cache_data.load()
        cache_save["fade_ms"] = self.fade_ms
        self.cache_data.save(cache_save)

    def reset_fade_ms(self):
        self.fade_ms = 500

    def is_playing(self):
        if self.get_busy():
            return True
        else:
            if self.get_paused():
                return True
            else:
                return False
    
    def set_filepath(self, path):
        self.filepath = path

    def get_filepath(self):
        return self.filepath

    def reset(self):
        self.filepath = None
        self.stop_music()
        pygame.mixer.music.unload()

if __name__ == "__main__":
    audioPlayer()