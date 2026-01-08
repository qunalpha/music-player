from customtkinter import *
from customtkinter import filedialog
from PIL import Image, ImageDraw
from mutagen import File
from mutagen.id3 import ID3, APIC
import customtkinter
import webbrowser
import pygame
import os
import io

version = "1.2 (Unstable)"

class App(CTk):
    def __init__(self, audio_player):
        super().__init__()

        self.title(f"Qun Music Player | {version} by @qunalpha on Github")
        self.after(201, lambda :self.iconbitmap(self.resource_path("resources/icon.ico")))
        self.geometry("720x420")
        self.minsize(720, 420)

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")

        self.update_rate = 250

        self.script_dir = os.path.dirname(__file__)
        
        self.cover_size = 200

        # Loading images
        self.default_img_path = Image.open(os.path.join(self.script_dir, self.resource_path("resources/pfp.png")))
        self.play_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/play.png"))), size=(40, 40))
        self.pause_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/pause.png"))), size=(40, 40))
        self.prev_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/prev.png"))), size=(30, 30))
        self.next_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/next.png"))), size=(30, 30))
        self.mute_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/mute.png"))), size=(30, 30))
        self.vol_1_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/vol-1.png"))), size=(30, 30))
        self.vol_2_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/vol-2.png"))), size=(30, 30))
        self.vol_3_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/vol-3.png"))), size=(30, 30))
        self.github_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/github.png"))), size=(30, 30))

        self.queue_hidden = False
        self.current_index = 0
        self.queue_buttons = []

        self.songs = []
        self.current_song = ""
        self.seeked = 0

        self.default_ui = True

        self.load_ui()
        self.master_updater()

        self.mainloop()

    def load_ui(self):
        # Grid Configiration
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.bind('<space>', self.media_controler_event)

        # Queue Widgets
        self.side_frame = CTkFrame(self)
        self.side_frame.grid(column=0, row=0, sticky="ns")
        self.side_frame.grid_rowconfigure(1, weight=1)

        self.add_btn = CTkButton(self.side_frame, text="Add Music", font=("Segoe UI", 12, "bold"), fg_color="#7132CA", hover_color="#5B29A5", width=100, command=self.ask_dir)
        self.add_btn.grid(row=0, column=0, pady=5, padx=(5, 2))
        self.clear_btn = CTkButton(self.side_frame, text="Clear All", font=("Segoe UI", 12, "bold"), fg_color="#7132CA", hover_color="#5B29A5", width=100, command=self.reset_queue_list)
        self.clear_btn.grid(row=0, column=1, pady=5, padx=(2, 5))

        self.queue_list_frame = CTkScrollableFrame(self.side_frame)
        self.queue_list_frame.grid(column=0, row=1, columnspan=2, sticky="nsew")
        self.queue_list_frame.grid_columnconfigure(0, weight=1)

        self.queue_label = CTkLabel(self.side_frame, text="Queue List", font=("Segoe UI", 20, "bold"))
        self.queue_label.grid(column=0, row=2, columnspan=2, pady=5)

        self.show_frame = CTkFrame(self, width=5, fg_color="transparent")
        self.show_frame.grid(column=1, row=0, rowspan=2, sticky="ns")
        self.show_frame.grid_rowconfigure(0, weight=1)
        self.show_frame.grid_columnconfigure(0, weight=1)

        self.toggle_show_queue_btn = CTkButton(self.show_frame, text="<", font=("Segoe UI", 12, "bold"), fg_color="#7132CA", hover_color="#5B29A5", width=0, height=75, command=self.hide_show_queue)
        self.toggle_show_queue_btn.grid(row=0, column=0, sticky="ew")

        # Master Widget UI
        self.parent_frame = CTkFrame(self)
        self.parent_frame.grid(row=0, column=2, sticky="nsew")
        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.parent_frame.grid_rowconfigure(1, weight=1)

        self.music_name_label = CTkLabel(self.parent_frame, text="Currently not Playing", font=("Segoe UI", 12, "bold"))
        self.music_name_label.grid(row=0, column=0, pady=(30, 0))

        self.default_cover = CTkImage(self.image_processer(self.default_img_path).resize((200, 200)), size=(self.cover_size, self.cover_size))
        self.cover_label = CTkLabel(self.parent_frame, text="", image=self.default_cover)
        self.cover_label.grid(row=1, column=0, pady=5)

        # Seeker UI
        self.seeker_frame = CTkFrame(self.parent_frame, fg_color="transparent")
        self.seeker_frame.grid(row=2, column=0, sticky="ew")
        self.seeker_frame.grid_columnconfigure(0, weight=1)
        self.seeker_frame.grid_rowconfigure(0, weight=1)

        self.seeker_slider = CTkSlider(self.seeker_frame, orientation="horizontal", button_color="#7132CA", progress_color="#C47BE4", button_hover_color="#5B29A5", state="disabled", command=self.seek_play)
        self.seeker_slider.grid(row=0, column=0, padx=(20, 5), sticky="ew")
        self.seeker_slider.set(0)

        self.duration_label = CTkLabel(self.seeker_frame, text="--:-- / --:--")
        self.duration_label.grid(row=0, column=1, padx=(5, 20))

        # Music Control UI
        self.control_frame = CTkFrame(self.parent_frame, fg_color="transparent")
        self.control_frame.grid(row=3, column=0, pady=(0, 10), sticky="ew")
        self.control_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform='a')

        self.filler_container = CTkFrame(self.control_frame, fg_color="transparent")
        self.filler_container.grid(column=0, row=0, sticky="w", padx=25)
        self.filler_container.grid_rowconfigure(0, weight=1)

        self.playback_container = CTkFrame(self.control_frame, fg_color="transparent")
        self.playback_container.grid(column=1, row=0)
        self.playback_container.grid_rowconfigure(0, weight=1)

        self.volume_container = CTkFrame(self.control_frame, fg_color="transparent")
        self.volume_container.grid(column=2, row=0, sticky="e", padx=(0, 5))
        self.volume_container.grid_rowconfigure(0, weight=1)
        self.volume_container.grid_columnconfigure(1, weight=1)

        control_ui_width = 10

        # self.settings_button = CTkButton(self.filler_container, text="", image=self.settings_img, width=control_ui_width, fg_color="transparent", hover_color="gray30", command=self.open_github)
        # self.settings_button.grid()

        self.github_button = CTkButton(self.filler_container, text="", image=self.github_img, width=control_ui_width, fg_color="transparent", hover_color="gray30", command=self.open_github)
        self.github_button.grid()

        self.play_button = CTkButton(self.playback_container, text="", image=self.play_img, width=control_ui_width, fg_color="transparent", hover_color="gray30", state="disabled", command=self.media_controler)
        self.play_button.grid(row=0, column=1)

        self.prev_button = CTkButton(self.playback_container, text="", image=self.prev_img, width=control_ui_width, fg_color="transparent", hover_color="gray30", state="disabled", command=self.rewind_music)
        self.prev_button.grid(row=0, column=0)

        self.next_button = CTkButton(self.playback_container, text="", image=self.next_img, width=control_ui_width, fg_color="transparent", hover_color="gray30", state="disabled", command=self.next_music)
        self.next_button.grid(row=0, column=2)

        self.mute_button = CTkButton(self.volume_container, text="", image=self.vol_3_img, width=control_ui_width, fg_color="transparent", hover_color="gray30", command=self.mute_volume)
        self.mute_button.grid(row=0, column=3)

        self.volume_slider = CTkSlider(self.volume_container, orientation="horizontal", width=100, button_color="#7132CA", progress_color="#C47BE4", button_hover_color="#5B29A5", command=self.change_volume)
        self.volume_slider.grid(row=0, column=4, padx=(0, 5), sticky="w")
        self.volume_slider.set(audio_player.get_volume())

        # Directory Path Label
        self.current_path_label = CTkLabel(self.parent_frame, text=self.script_dir)
        self.current_path_label.bind('<Double-Button-1>', self.open_file_dir)
        self.current_path_label.grid(row=5, column=0)
        
    def hide_show_queue(self):
        if not self.queue_hidden:
            self.side_frame.grid_forget()
            self.toggle_show_queue_btn.configure(text=">")
            self.queue_hidden = True
        else:
            self.side_frame.grid(column=0, row=0, sticky="ns")
            self.toggle_show_queue_btn.configure(text="<")
            self.queue_hidden = False

    def mute_volume(self):
        if audio_player.get_muted():
            audio_player.mute_music()
            self.update_volume_icon()
        else:
            audio_player.mute_music()
            self.mute_button.configure(image=self.mute_img)

    def change_volume(self, volume):
        audio_player.set_volume(volume)
        self.update_volume_icon()

    def update_volume_icon(self):
        if audio_player.get_int_volume() <= 0:
            self.mute_button.configure(image=self.mute_img)
        elif audio_player.get_int_volume() <= 34:
            self.mute_button.configure(image=self.vol_1_img)
        elif audio_player.get_int_volume() <= 67:
            self.mute_button.configure(image=self.vol_2_img)
        elif audio_player.get_int_volume() <= 100:
            self.mute_button.configure(image=self.vol_3_img)

    def enable_control_btn(self):
        self.play_button.configure(state="normal")
        self.prev_button.configure(state="normal")
        self.next_button.configure(state="normal")
        self.seeker_slider.configure(state="normal")

    def disable_control_btn(self):
        self.play_button.configure(state="disabled")
        self.prev_button.configure(state="disabled")
        self.next_button.configure(state="disabled")
        self.seeker_slider.configure(state="disabled")

    def reset_seeked(self):
        self.seeked = 0

    def reset_ui(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        self.load_ui()
        self.reset_queue_list(False)
        for song in self.songs:
            self.load_queue_list(song)
        self.reset_seeked()
        self.default_ui = True
        audio_player.reset()

    def set_seeker(self, current_pos: int, duration: int, playing=False):
        try:
            if playing:
                self.seeker_slider.configure(to=audio_player.get_duration())
                self.seeker_slider.set(current_pos)
                current_pos_min = current_pos // 60
                current_pos_sec = current_pos % 60
                duration_min = duration // 60
                duration_sec = duration % 60
                self.duration_label.configure(text=f"{current_pos_min}:{current_pos_sec:02d} / {duration_min}:{duration_sec:02d}")
            else:
                self.seeker_slider.configure(to=1)
                self.seeker_slider.set(0)
                self.duration_label.configure(text=f"--:-- / --:--")
        except:
            pass

    def seek_play(self, seek):
        self.seeked = int(seek)
        audio_player.seek_player(self.seeked)
        self.play_button.configure(image=self.pause_img)

    def media_controler(self):
        if audio_player.get_if_play_pause() == "Pause":
            self.fade_out_pause()
            self.play_button.configure(image=self.play_img)
        elif audio_player.get_if_play_pause() == "Resume":
            self.fade_in_unpause()
            self.play_button.configure(image=self.pause_img)
        else:
            audio_player.play_music()
            self.play_button.configure(image=self.pause_img)

    def media_controler_event(self, event):
        self.media_controler()

    def rewind_music(self):
        if self.get_absolute_playback() <= 5 and self.current_index >= 1:
            self.reset_seeked()
            self.on_click_queue(self.current_index - 1)
            self.play_button.configure(image=self.pause_img)
        else:
            self.reset_seeked()
            audio_player.rewind_music()
            self.play_button.configure(image=self.pause_img)

    def next_music(self):
        if not self.current_index >= len(self.songs) - 1:
            self.reset_seeked()
            self.on_click_queue(self.current_index + 1)
            self.play_button.configure(image=self.pause_img)

    def fade_out_pause(self):
        def _fade(vol):
            if vol <= 0:
                audio_player.temp_set_volume(audio_player.get_volume())
                audio_player.pause_music()
                return
            audio_player.temp_set_volume(vol / 100)
            self.after(5, _fade, vol - 1)

        if audio_player.get_muted():
            audio_player.pause_music()
        else:
            _fade(audio_player.get_int_volume())

    def fade_in_unpause(self):
        def _fade(vol):
            if vol >= audio_player.get_int_volume():
                audio_player.temp_set_volume(audio_player.get_volume())
                return
            audio_player.temp_set_volume(vol / 100)
            self.after(5, _fade, vol + 1)

        audio_player.resume_music()

        if not audio_player.get_muted():
            _fade(0)

    def shorten_title(self, title, max_len=32):
        if len(title) > max_len:
            return title[:max_len - 3] + "..."
        return title

    def add_queue_list(self, path):
        self.songs.append(path)
        self.load_queue_list(path)

    def on_click_queue(self, index):
        self.queue_buttons[self.current_index].configure(fg_color="transparent", hover_color="gray30")
        self.queue_buttons[index].configure(fg_color="#7132CA", hover_color="#5B29A5")
        self.current_index = index
        self.open_audio(index)

    def load_queue_list(self, path):
        name = f"{len(self.queue_buttons) + 1}.{audio_player.get_title(path)}"
        button = CTkButton(self.queue_list_frame, text=self.shorten_title(name), font=("Segoe UI", 12), anchor="w", corner_radius=0, fg_color="transparent", hover_color="gray30", command=lambda i = len(self.queue_buttons): self.on_click_queue(i))
        button.grid(row=len(self.queue_buttons), column=0, sticky="ew")
        self.queue_buttons.append(button)

    def reset_queue_list(self, reset_songs=True):
        if reset_songs:
            self.songs = []
        for widgets in self.queue_list_frame.winfo_children():
            widgets.destroy()
        self.current_index = 0
        self.queue_buttons = []

    def master_updater(self):
        current = audio_player.get_playback_position() + self.seeked
        duration = audio_player.get_duration()
        if audio_player.is_playing():
            self.set_seeker(current, duration, playing=True)
        elif audio_player.check_for_end():
            self.next_music()
        else:
            self.set_seeker(current, duration, playing=False)
            if not self.default_ui:
                self.reset_ui()

        self.after(self.update_rate, self.master_updater)

    def get_absolute_playback(self):
        return audio_player.get_playback_position() + self.seeked

    def ask_dir(self):
        try:
            paths = filedialog.askopenfilenames(title="Select an audio file", filetypes=[
                ("Audio files", "*.mp3 *.wav *.ogg *.flac"),
                ("MP3 files", "*.mp3"),
                ("WAV files", "*.wav"),
                ("All files", "*.*")
            ])
        except:
            return
        for song in paths:
            self.add_queue_list(song)
        if not audio_player.get_busy():
            self.on_click_queue(0)

    def open_audio(self, index):
        path = self.songs[index]
        audio_player.set_filepath(path)
        audio = File(path, easy=True)
        self.music_name_label.configure(text=f"{audio.get("title", [os.path.basename(path)])[0]} | {audio.get("artist", ["Unknown"])[0]}")
        self.current_path_label.configure(text=path)

        # Playing the music

        cover_image = None # Cover image decoder is made using ChatGPT Ahhhhhhhhhhhhhh

        try:
            # Explicitly load ID3 tags from MP3
            tags = ID3(path)
            for tag in tags.values():
                if isinstance(tag, APIC):
                    cover_image = Image.open(io.BytesIO(tag.data))
                    break
        except:
            pass

        if cover_image:
            audio_cover = CTkImage(self.image_processer(cover_image).resize((200, 200)), size=(200, 200))
            self.cover_label.configure(text="", image=audio_cover)
            #self.cover_label.image = audio_cover  # keep reference
        else:
            self.cover_label.configure(text="", image=self.default_cover)

        pygame.mixer.music.load(path)
        self.enable_control_btn()
        self.play_button.configure(image=self.pause_img)
        self.reset_seeked()
        self.default_ui = False
        audio_player.play_music()

    def image_processer(self, img):
        width, height = img.size
        min_side = min(width, height)

        left = (width - min_side) // 2
        top = (height - min_side) // 2
        right = left + min_side
        bottom = top + min_side

        cropped_img = img.crop((left, top, right, bottom)).convert("RGBA")

        radius = int(min_side * 0.10)

        mask = Image.new("L", (min_side, min_side), 0)
        draw = ImageDraw.Draw(mask)

        draw.rounded_rectangle((0, 0, min_side, min_side), radius=radius, fill=255)

        cropped_img.putalpha(mask)
        return cropped_img
    
    def open_file_dir(self, event):
        try:
            os.startfile(os.path.dirname(audio_player.get_filepath()))
        except:
            os.startfile(os.path.dirname(self.script_dir))
    
    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS  # PyInstaller temp folder
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def open_toplevel(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self) # create window if its None or destroyed
        else:
            self.after(200, self.toplevel_window.focus())  # if window exists focus it
            
    def open_github(self):
        webbrowser.open("https://github.com/qunalpha")

class audioPlayer():
    def __init__(self):
        super().__init__()
        # Initiliaze pygame mixer
        pygame.init()
        pygame.mixer.init()

        self.paused = True
        self.volume = 0.7
        self.muted = False
        self.filepath = None

        self.end_endevent = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.end_endevent)

        pygame.mixer.music.set_volume(self.get_volume())
        
    def play_music(self):
        self.paused = False
        pygame.mixer.music.play(fade_ms=500)

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
        pygame.mixer.music.play()

    def seek_player(self, seconds):
        self.paused = False
        pygame.mixer.music.play(start=seconds, fade_ms=500)
            
    def mute_music(self):
        if not self.muted:
            self.muted = True
            pygame.mixer.music.set_volume(0)
        else:
            self.muted = False
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
        return File(path, easy=True).get("title", [os.path.basename(path)])[0]

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

    def temp_set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)
    
    def set_volume(self, volume):
        self.volume = volume
        self.muted = False
        pygame.mixer.music.set_volume(self.volume)

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

audio_player = audioPlayer()

App(audio_player)
