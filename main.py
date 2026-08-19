from customtkinter import *
from customtkinter import filedialog
from PIL import Image, ImageDraw
from mutagen import File
from mutagen.id3 import ID3, APIC
from jsonScript import jsonDatabase, version as json_version
from audioPlayer import audioPlayer
import customtkinter
import threading
import webbrowser
import pygame
import os
import io

version = "2.0.5 (Remastered)"

class App(CTk):
    def __init__(self, audio_player):
        super().__init__()

        self.title(f"Qun Music Player | {version} by @qunalpha on Github")
        self.after(201, lambda :self.iconbitmap(self.resource_path("resources/icon.ico")))
        self.geometry("800x420")
        self.minsize(720, 420)
        # self.resizable(0, 0)

        customtkinter.set_appearance_mode(audio_player.cache_data.load()["appearance_mode"])
        customtkinter.set_default_color_theme("dark-blue")
        customtkinter.set_widget_scaling(float(audio_player.cache_data.load()["ui_scale"]) / 100)

        self.update_rate = audio_player.cache_data.load()["update_rate"] # Default 250

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
        self.config_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/config.png"))), size=(30, 30))

        self.mini_play_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/play.png"))), size=(30, 30))
        self.mini_pause_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/pause.png"))), size=(30, 30))
        self.mini_next_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/next.png"))), size=(25, 25))
        self.mini_mute_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/mute.png"))), size=(25, 25))
        self.mini_vol_1_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/vol-1.png"))), size=(25, 25))
        self.mini_vol_2_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/vol-2.png"))), size=(25, 25))
        self.mini_vol_3_img = CTkImage(Image.open(os.path.join(self.script_dir, self.resource_path("resources/vol-3.png"))), size=(25, 25))

        self.queue_hidden = False
        self.current_index = 0
        self.queue_buttons = []

        self.songs = []
        self.corrupted_index = []
        self.current_song = ""
        self.seeked = 0

        self.ui_color = "#7132CA" # Default - "#7132CA"
        self.hover_color = "#5B29A5" # Default - "#5B29A5"
        self.progress_color = "#C47BE4" # Default - "#C47BE4"

        self.default_ui = True

        self.config_variable_auto_update = False

        self.load_ui()
        
        if not audio_player.get_muted():
            self.update_volume_ui()
        # threading.Thread(target=self.master_updater, daemon=True).start()
        self.master_updater()

        self.bind("<Configure>", self.on_resize)
        
        if audio_player.cache_data.load()["load_queue"]:
            self.load_db()
            
        self.mainloop()

    def load_ui(self):
        # Grid Configiration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.bind('<space>', self.media_controler_event)

        self.music_player_frame = CTkFrame(self, fg_color="transparent")
        self.music_player_frame.grid(sticky="nsew")
        self.music_player_frame.grid_columnconfigure(2, weight=1)
        self.music_player_frame.grid_rowconfigure(0, weight=1)

        # Queue Widgets
        self.side_frame = CTkFrame(self.music_player_frame)
        self.side_frame.grid(column=0, row=0, sticky="ns")
        self.side_frame.grid_rowconfigure(1, weight=1)

        self.add_btn = CTkButton(self.side_frame, text="Add Music", font=("Segoe UI", 12, "bold"), fg_color=self.ui_color, hover_color=self.hover_color, width=100, command=self.ask_dir)
        self.add_btn.grid(row=0, column=0, pady=5, padx=(5, 2))
        self.clear_btn = CTkButton(self.side_frame, text="Clear All", font=("Segoe UI", 12, "bold"), fg_color=self.ui_color, hover_color=self.hover_color, width=100, command=self.reset_queue_list)
        self.clear_btn.grid(row=0, column=1, pady=5, padx=(2, 5))

        self.queue_list_frame = CTkScrollableFrame(self.side_frame)
        self.queue_list_frame.grid(column=0, row=1, columnspan=2, sticky="nsew")
        self.queue_list_frame.grid_columnconfigure(0, weight=1)

        self.queue_label = CTkLabel(self.side_frame, text="Queue List", font=("Segoe UI", 20, "bold"))
        self.queue_label.grid(column=0, row=2, columnspan=2, pady=5)

        self.show_frame = CTkFrame(self.music_player_frame, width=5, fg_color="transparent")
        self.show_frame.grid(column=1, row=0, rowspan=2, sticky="ns")
        self.show_frame.grid_rowconfigure(0, weight=1)
        self.show_frame.grid_columnconfigure(0, weight=1)

        self.toggle_show_queue_btn = CTkButton(self.show_frame, text="<", font=("Segoe UI", 12, "bold"), fg_color=self.ui_color, hover_color=self.hover_color, width=0, height=75, command=self.hide_show_queue)
        self.toggle_show_queue_btn.grid(row=0, column=0, sticky="ew")

        # Master Widget UI
        self.parent_frame = CTkFrame(self.music_player_frame)
        self.parent_frame.grid(row=0, column=2, sticky="nsew")
        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.parent_frame.grid_rowconfigure(1, weight=1)

        self.music_name_label = CTkLabel(self.parent_frame, text="Currently not Playing", font=("Segoe UI", 12, "bold"))
        self.music_name_label.grid(row=0, column=0, pady=(30, 0))

        self.default_cover = CTkImage(self.image_processer(self.default_img_path), size=(self.cover_size, self.cover_size))
        self.cover_label = CTkLabel(self.parent_frame, text="", image=self.default_cover)
        self.cover_label.grid(row=1, column=0, pady=5, sticky="nsew")

        # Seeker UI
        self.seeker_frame = CTkFrame(self.parent_frame, fg_color="transparent")
        self.seeker_frame.grid(row=2, column=0, sticky="ew")
        self.seeker_frame.grid_columnconfigure(0, weight=1)
        self.seeker_frame.grid_rowconfigure(0, weight=1)

        self.seeker_slider = CTkSlider(self.seeker_frame, orientation="horizontal", button_color=self.ui_color, progress_color=self.progress_color, button_hover_color=self.hover_color, state="disabled", command=self.seek_play)
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

        self.config_button = CTkButton(self.filler_container, text="", image=self.config_img, width=control_ui_width, fg_color="transparent", hover_color=("gray70", "gray30"), command=self.open_config)
        self.config_button.grid(row=0, column=1)

        self.github_button = CTkButton(self.filler_container, text="", image=self.github_img, width=control_ui_width, fg_color="transparent", hover_color=("gray70", "gray30"), command=self.open_github)
        self.github_button.grid(row=0, column=0)

        self.play_button = CTkButton(self.playback_container, text="", image=self.play_img, width=control_ui_width, fg_color="transparent", hover_color=("gray70", "gray30"), state="disabled", command=self.media_controler)
        self.play_button.grid(row=0, column=1)

        self.prev_button = CTkButton(self.playback_container, text="", image=self.prev_img, width=control_ui_width, fg_color="transparent", hover_color=("gray70", "gray30"), state="disabled", command=self.rewind_music)
        self.prev_button.grid(row=0, column=0)

        self.next_button = CTkButton(self.playback_container, text="", image=self.next_img, width=control_ui_width, fg_color="transparent", hover_color=("gray70", "gray30"), state="disabled", command=self.next_music)
        self.next_button.grid(row=0, column=2)

        self.mute_button = CTkButton(self.volume_container, text="", image=self.mute_img, width=control_ui_width, fg_color="transparent", hover_color=("gray70", "gray30"), command=self.mute_volume)
        self.mute_button.grid(row=0, column=3)

        self.volume_slider = CTkSlider(self.volume_container, orientation="horizontal", width=100, button_color=self.ui_color, progress_color=self.progress_color, button_hover_color=self.hover_color, command=self.change_volume)
        self.volume_slider.grid(row=0, column=4, padx=(0, 5), sticky="w")
        self.volume_slider.set(audio_player.get_volume())

        # Directory Path Label
        self.current_path_label = CTkLabel(self.parent_frame, text=self.script_dir)
        self.current_path_label.bind('<Double-Button-1>', self.open_file_dir)
        self.current_path_label.grid(row=5, column=0)

        ## Master Config Frame UI
        self.config_frame = CTkFrame(self)
        self.config_frame.grid_rowconfigure(1, weight=1)
        self.config_frame.grid_columnconfigure(1, weight=1)

        self.config_nav_frame = CTkFrame(self.config_frame, fg_color=("gray85", "gray15"), corner_radius=0)
        self.config_nav_frame.grid(row=0, columnspan=2, sticky="ew")
        self.config_nav_frame.grid_rowconfigure(1, weight=1)
        self.config_nav_frame.grid_columnconfigure(1, weight=1)

        self.config_back_button = CTkButton(self.config_nav_frame, text="Back", width=10, fg_color=self.ui_color, font=("Segoe UI", 12, "bold"), hover_color=self.hover_color, command=self.open_music_player)
        self.config_back_button.grid(row=0, column=0, pady=5, padx=5)

        self.restore_default_button = CTkButton(self.config_nav_frame, text="Restore Default", width=20, fg_color=self.ui_color, font=("Segoe UI", 12, "bold"), hover_color=self.hover_color, command=self.reset_config)
        self.restore_default_button.grid(row=0, column=2, pady=5, padx=(5, 3))

        self.save_config_button = CTkButton(self.config_nav_frame, text="Save", width=20, fg_color="#008d07", font=("Segoe UI", 12, "bold"), hover_color="#005e05", command=self.save_config)
        self.save_config_button.grid(row=0, column=3, pady=5, padx=(3, 5))

        self.config_menu_frame = CTkFrame(self.config_frame, corner_radius=0)
        self.config_menu_frame.grid(row=1, column=0, sticky="ns")

        self.general_config_button = CTkButton(self.config_menu_frame, text="General", text_color="white", fg_color=self.ui_color, hover_color=self.hover_color, font=("Segoe UI", 12, "bold"), corner_radius=0, command=lambda: self.onclick_config_button(0))
        self.general_config_button.grid(row=0, column=0, sticky="ew", pady=(5, 0))

        self.playback_config_button = CTkButton(self.config_menu_frame, text="Playback", text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12), corner_radius=0, command=lambda: self.onclick_config_button(1))
        self.playback_config_button.grid(row=1, column=0, sticky="ew")

        self.audio_config_button = CTkButton(self.config_menu_frame, text="Audio", text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12), corner_radius=0, command=lambda: self.onclick_config_button(2))
        self.audio_config_button.grid(row=2, column=0, sticky="ew")
        
        self.variable_config_button = CTkButton(self.config_menu_frame, text="Variable", text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12), corner_radius=0, command=lambda: self.onclick_config_button(3))
        self.variable_config_button.grid(row=3, column=0, sticky="ew")

        self.library_config_button = CTkButton(self.config_menu_frame, text="Library", text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12), corner_radius=0, command=lambda: self.onclick_config_button(4))
        self.library_config_button.grid(row=4, column=0, sticky="ew")

        self.appearance_config_button = CTkButton(self.config_menu_frame, text="Appearance", text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12), corner_radius=0, command=lambda: self.onclick_config_button(5))
        self.appearance_config_button.grid(row=5, column=0, sticky="ew")

        self.advanced_config_button = CTkButton(self.config_menu_frame, text="Advanced", text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12), corner_radius=0, command=lambda: self.onclick_config_button(6))
        self.advanced_config_button.grid(row=6, column=0, sticky="ew")

        self.log_config_button = CTkButton(self.config_menu_frame, text="Log", text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12), corner_radius=0, command=lambda: self.onclick_config_button(7))
        self.log_config_button.grid(row=7, column=0, sticky="ew")

        # self.queue_buttons[self.current_index].configure(fg_color="transparent", hover_color="gray30", font=("Segoe UI", 12))
        # self.queue_buttons[index].configure(fg_color=self.ui_color, hover_color=self.hover_color, font=("Segoe UI", 12, "bold"))

        self.config_container_frame = CTkFrame(self.config_frame, corner_radius=0)
        self.config_container_frame.grid(row=1, column=1, sticky="nsew")
        self.config_container_frame.grid_columnconfigure(0, weight=1)
        self.config_container_frame.grid_rowconfigure(0, weight=1)

        self.config_player_frame = CTkFrame(self.config_frame, fg_color=("gray85", "gray15"), height=40)
        self.config_player_frame.grid(row=2, columnspan=2, sticky="ew", padx=5, pady=5)
        self.config_player_frame.grid_columnconfigure(6, weight=1)

        self.default_mini_cover = CTkImage(self.image_processer(self.default_img_path), size=(40, 40))
        self.mini_cover_label = CTkLabel(self.config_player_frame, text="", image=self.default_mini_cover)
        self.mini_cover_label.grid(row=0, column=0, padx=5, pady=5)

        self.config_play_button = CTkButton(self.config_player_frame, text="", image=self.mini_play_img, width=10, fg_color="transparent", hover_color=("gray70", "gray30"), state="disabled", command=self.media_controler)
        self.config_play_button.grid(row=0, column=1, padx=(5, 0))

        self.config_next_button = CTkButton(self.config_player_frame, text="", image=self.mini_next_img, width=10, fg_color="transparent", hover_color=("gray70", "gray30"), state="disabled", command=self.next_music)
        self.config_next_button.grid(row=0, column=2)

        self.config_player_duration = CTkLabel(self.config_player_frame, text=f"--:-- / --:--", font=("Segoe UI", 14))
        self.config_player_duration.grid(row=0, column=4, padx=5)

        self.config_player_title = CTkLabel(self.config_player_frame, text="Currently Not Playing", font=("Segoe UI", 14, "bold"))
        self.config_player_title.grid(row=0, column=5, padx=5)

        self.config_mute_button = CTkButton(self.config_player_frame, text="", image=self.mini_mute_img, width=control_ui_width, fg_color="transparent", hover_color=("gray70", "gray30"), command=self.mute_volume)
        self.config_mute_button.grid(row=0, column=7, padx=5)

        ### Config menu frame ui

        # General Config
        self.general_config_frame = CTkFrame(self.config_container_frame, fg_color="transparent")
        self.general_config_frame.grid(row=0, column=0, sticky="nsew")
        self.general_config_frame.grid_columnconfigure(0, weight=1)

        CTkLabel(self.general_config_frame, text="Remember Last Playlist", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.config_switch_1 = CTkSwitch(self.general_config_frame, width=0, text="", progress_color=self.progress_color, button_color=self.ui_color, button_hover_color=self.hover_color, variable=BooleanVar(value=audio_player.cache_data.load()["load_queue"]), command=self.toggle_load_queue)
        self.config_switch_1.grid(row=0, column= 1, padx=5, pady=(10, 5), sticky="e")
        
        CTkLabel(self.general_config_frame, text="Remember Last Control", font=("Segoe UI", 14, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.config_switch_2 = CTkSwitch(self.general_config_frame, width=0, text="", font=("Segoe UI", 14, "bold"), progress_color=self.progress_color, button_color=self.ui_color, button_hover_color=self.hover_color, variable=BooleanVar(value=audio_player.cache_data.load()["load_control"]), command=self.toggle_ui_control)
        self.config_switch_2.grid(row=1, column= 1, padx=5, pady=5, sticky="e")

        self.config_warning_1 = CTkLabel(self.general_config_frame, text="*Restart the App to take effect!", text_color="red", font=("Segoe UI", 12, "italic"), anchor="w")

        # Playback Config
        self.playback_config_frame = CTkFrame(self.config_container_frame, fg_color="transparent")
        self.playback_config_frame.grid_columnconfigure(0, weight=1)

        CTkLabel(self.playback_config_frame, text="Starting Fade", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.config_entry_1 = CTkEntry(self.playback_config_frame, width=80, height=20, validate="key", validatecommand=(self.register(self.only_integer), "%P"))
        self.config_entry_1.insert(0, audio_player.get_fade_ms())
        self.config_entry_1.grid(row=0, column=1, padx=5, pady=(10, 5), sticky="e")
        CTkLabel(self.playback_config_frame, text="ms", font=("Segoe UI", 12, "italic")).grid(row=0, column=2, padx=(5, 10), pady=(10, 5), sticky="e")

        # Audio Config
        self.audio_config_frame = CTkFrame(self.config_container_frame, fg_color="transparent")
        self.audio_config_frame.grid_columnconfigure(0, weight=1)

        CTkLabel(self.audio_config_frame, text="Volume", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.config_slider_1 = CTkSlider(self.audio_config_frame, orientation="horizontal", button_color=self.ui_color, progress_color=self.progress_color, button_hover_color=self.hover_color, command=self.change_volume)
        self.config_slider_1.grid(row=0, column=1, padx=5, pady=(10, 5), sticky="ew")
        self.config_slider_1.set(audio_player.get_volume())
        self.config_label_1 = CTkLabel(self.audio_config_frame, text=f"{audio_player.get_int_volume()}%", anchor="e", width=32, font=("Segoe UI", 12, "bold"))
        self.config_label_1.grid(row=0, column=2, padx=(5, 10), pady=(10, 5), sticky="e")
        CTkLabel(self.audio_config_frame, text="Mute", font=("Segoe UI", 14, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.config_button_3 = CTkButton(self.audio_config_frame, text=f"{"Mute" if audio_player.get_muted() else "Unmute"}", font=("Segoe UI", 12, "bold"), width=80, fg_color=self.ui_color, hover_color=self.hover_color, command=self.mute_volume)
        self.config_button_3.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="e")

        # Variable Config
        self.variable_config_frame = CTkFrame(self.config_container_frame, fg_color="transparent")
        self.variable_config_frame.grid_rowconfigure(2, weight=1)
        self.variable_config_frame.grid_columnconfigure(0, weight=1)

        CTkLabel(self.variable_config_frame, text="Auto Update", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.config_switch_3 = CTkSwitch(self.variable_config_frame, width=0, text="", progress_color=self.progress_color, button_color=self.ui_color, button_hover_color=self.hover_color, variable=BooleanVar(value=self.config_variable_auto_update), command=self.toggle_auto_variable_updater)
        self.config_switch_3.grid(row=0, column= 1, padx=5, pady=(10, 5), sticky="e")
        self.config_button_1 = CTkButton(self.variable_config_frame, text="Refresh", width=10, fg_color=self.ui_color, font=("Segoe UI", 12, "bold"), hover_color=self.hover_color, command=self.refresh_variable_value)
        self.config_button_1.grid(row=1, column= 1, padx=5, pady=5, sticky="e")

        self.variable_config_master = CTkScrollableFrame(self.variable_config_frame, fg_color="transparent")
        self.variable_config_master.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.variable_config_master.grid_columnconfigure(0, weight=1)

        CTkLabel(self.variable_config_master, text="version", font=("Segoe UI", 14, "bold")).grid(row=2, column=0, padx=10, pady=(10, 2), sticky="w")
        self.config_variable_label_1 = CTkLabel(self.variable_config_master, text=version, anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_1.grid(row=2, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="update_rate", font=("Segoe UI", 14, "bold")).grid(row=3, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_2 = CTkLabel(self.variable_config_master, text=self.update_rate, anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_2.grid(row=3, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="script_dir", font=("Segoe UI", 14, "bold")).grid(row=4, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_3 = CTkLabel(self.variable_config_master, text=self.script_dir, anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_3.grid(row=4, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="cover_size", font=("Segoe UI", 14, "bold")).grid(row=5, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_4 = CTkLabel(self.variable_config_master, text=self.cover_size, anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_4.grid(row=5, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="queue_hidden", font=("Segoe UI", 14, "bold")).grid(row=6, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_5 = CTkLabel(self.variable_config_master, text=self.queue_hidden, anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_5.grid(row=6, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="current_index", font=("Segoe UI", 14, "bold")).grid(row=7, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_6 = CTkLabel(self.variable_config_master, text=self.current_index, anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_6.grid(row=7, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="queue_buttons", font=("Segoe UI", 14, "bold")).grid(row=8, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_7 = CTkLabel(self.variable_config_master, text=str(self.queue_buttons)[:70]+"...", anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_7.grid(row=8, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="songs", font=("Segoe UI", 14, "bold")).grid(row=9, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_8 = CTkLabel(self.variable_config_master, text=str(self.songs)[:70]+"...", anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_8.grid(row=9, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="corrupted_index", font=("Segoe UI", 14, "bold")).grid(row=10, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_9 = CTkLabel(self.variable_config_master, text=self.corrupted_index, anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_9.grid(row=10, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="current_song", font=("Segoe UI", 14, "bold")).grid(row=11, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_10 = CTkLabel(self.variable_config_master, text=self.current_song, anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_10.grid(row=11, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="seeked", font=("Segoe UI", 14, "bold")).grid(row=12, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_11 = CTkLabel(self.variable_config_master, text=self.seeked, anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_11.grid(row=12, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="ui_color", font=("Segoe UI", 14, "bold")).grid(row=13, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_12 = CTkLabel(self.variable_config_master, text=self.ui_color, anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_12.grid(row=13, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="hover_color", font=("Segoe UI", 14, "bold")).grid(row=14, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_13 = CTkLabel(self.variable_config_master, text=self.hover_color, anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_13.grid(row=14, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="progress_color", font=("Segoe UI", 14, "bold")).grid(row=15, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_14 = CTkLabel(self.variable_config_master, text=self.progress_color, anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_14.grid(row=15, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="default_ui", font=("Segoe UI", 14, "bold")).grid(row=16, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_15 = CTkLabel(self.variable_config_master, text=self.default_ui, anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_15.grid(row=16, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="Audio Player", font=("Segoe UI", 16, "bold")).grid(row=17, column=0, columnspan=2, padx=10, pady=(6, 2), sticky="ew")
        CTkLabel(self.variable_config_master, text="get_if_play_pause", font=("Segoe UI", 14, "bold")).grid(row=18, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_16 = CTkLabel(self.variable_config_master, text=audio_player.get_if_play_pause(), anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_16.grid(row=18, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="get_playback_position", font=("Segoe UI", 14, "bold")).grid(row=19, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_17 = CTkLabel(self.variable_config_master, text=audio_player.get_playback_position(), anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_17.grid(row=19, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="get_title", font=("Segoe UI", 14, "bold")).grid(row=20, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_18 = CTkLabel(self.variable_config_master, text=audio_player.get_title(audio_player.get_filepath()), anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_18.grid(row=20, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="get_duration", font=("Segoe UI", 14, "bold")).grid(row=21, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_19 = CTkLabel(self.variable_config_master, text=audio_player.get_duration(), anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_19.grid(row=21, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="get_volume", font=("Segoe UI", 14, "bold")).grid(row=22, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_20 = CTkLabel(self.variable_config_master, text=audio_player.get_volume(), anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_20.grid(row=22, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="get_int_volume", font=("Segoe UI", 14, "bold")).grid(row=23, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_21 = CTkLabel(self.variable_config_master, text=audio_player.get_int_volume(), anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_21.grid(row=23, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="get_muted", font=("Segoe UI", 14, "bold")).grid(row=24, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_22 = CTkLabel(self.variable_config_master, text=audio_player.get_muted(), anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_22.grid(row=24, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="get_busy", font=("Segoe UI", 14, "bold")).grid(row=25, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_23 = CTkLabel(self.variable_config_master, text=audio_player.get_busy(), anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_23.grid(row=25, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="get_paused", font=("Segoe UI", 14, "bold")).grid(row=26, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_24 = CTkLabel(self.variable_config_master, text=audio_player.get_paused(), anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_24.grid(row=26, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="get_fade_ms", font=("Segoe UI", 14, "bold")).grid(row=27, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_25 = CTkLabel(self.variable_config_master, text=audio_player.get_fade_ms(), anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_25.grid(row=27, column=1, padx=10, pady=(10, 2), sticky="e")
        CTkLabel(self.variable_config_master, text="get_filepath", font=("Segoe UI", 14, "bold")).grid(row=28, column=0, padx=10, pady=2, sticky="w")
        self.config_variable_label_26 = CTkLabel(self.variable_config_master, text=str(audio_player.get_filepath())[:70]+"...", anchor="e", width=32, font=("Segoe UI", 14,))
        self.config_variable_label_26.grid(row=28, column=1, padx=10, pady=(10, 2), sticky="e")

        self.library_config_frame = CTkFrame(self.config_container_frame, fg_color="transparent")

        # Appearance Config
        self.appearance_config_frame = CTkFrame(self.config_container_frame, fg_color="transparent")
        self.appearance_config_frame.grid_columnconfigure(0, weight=1)

        CTkLabel(self.appearance_config_frame, text="Appearance", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w") 
        self.config_appearance_menu = CTkOptionMenu(self.appearance_config_frame, values=["System", "Light", "Dark"], font=("Segoe UI", 12, "bold"), anchor="center", fg_color=self.ui_color, button_color=self.ui_color, button_hover_color=self.hover_color, command=self.set_appearance_mode)
        self.config_appearance_menu.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="e")
        self.config_appearance_menu.set(audio_player.cache_data.load()["appearance_mode"])

        CTkLabel(self.appearance_config_frame, text="UI Scale", font=("Segoe UI", 14, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w") 
        self.config_scaling_menu = CTkOptionMenu(self.appearance_config_frame, values=["80%", "90%", "100%", "110%", "120%"], font=("Segoe UI", 12, "bold"), anchor="center", fg_color=self.ui_color, button_color=self.ui_color, button_hover_color=self.hover_color, command=self.set_ui_scale_striped)
        self.config_scaling_menu.grid(row=1, column=1, padx=10, pady=5, sticky="e")
        self.config_scaling_menu.set(str(audio_player.cache_data.load()["ui_scale"])+"%")

        # Advance Config
        self.advanced_config_frame = CTkFrame(self.config_container_frame, fg_color="transparent")
        self.advanced_config_frame.grid_columnconfigure(0, weight=1)

        CTkLabel(self.advanced_config_frame, text="Update Rate", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.config_entry_2 = CTkEntry(self.advanced_config_frame, width=80, height=20, validate="key", validatecommand=(self.register(self.only_integer), "%P"))
        self.config_entry_2.insert(0, self.update_rate)
        self.config_entry_2.grid(row=0, column=1, padx=5, pady=(10, 5), sticky="e")
        CTkLabel(self.advanced_config_frame, text="ms", font=("Segoe UI", 12, "italic")).grid(row=0, column=2, padx=(5, 10), pady=(10, 5), sticky="e")

        CTkLabel(self.advanced_config_frame, text="Force UI Update", font=("Segoe UI", 14, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.config_button_2 = CTkButton(self.advanced_config_frame, text="Reset", width=10, fg_color="#ff0000", font=("Segoe UI", 12, "bold"), hover_color="#c50000", command=self.reset_ui)
        self.config_button_2.grid(row=1, column= 1, columnspan=2, padx=5, pady=5, sticky="e")
        
        self.log_config_frame = CTkFrame(self.config_container_frame, fg_color="transparent")

    def set_appearance_mode(self, mode: str["System", "Light", "Dark"] = "System"):
        customtkinter.set_appearance_mode(mode)
        save = audio_player.cache_data.load()
        save["appearance_mode"] = mode
        audio_player.cache_data.save(save)

    def set_ui_scale(self, scale: float = 100):
        customtkinter.set_widget_scaling(scale / 100)
        save = audio_player.cache_data.load()
        save["ui_scale"] = int(scale)
        audio_player.cache_data.save(save)

    def set_ui_scale_striped(self, value: str):
        self.set_ui_scale(float(value.strip("%")))

    def load_db(self):
        self.db = jsonDatabase("queue.json", ("path",))

        def _add(songs):
            for song in songs:
                self.songs.append(song["path"])
                self.load_queue_list(song["path"])

        threading.Thread(target=_add, args=(self.db.load(),), daemon=False).start()

    def toggle_load_queue(self):
        save = audio_player.cache_data.load()
        if save["load_queue"]:
            save["load_queue"] = False
        else:
            save["load_queue"] = True

        audio_player.cache_data.save(save)
        self.config_switch_1.configure(variable=BooleanVar(value=audio_player.cache_data.load()["load_queue"]))
        self.config_warning_1.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="we")

    def toggle_ui_control(self):
        save = audio_player.cache_data.load()
        if save["load_control"]:
            save["load_control"] = False
        else:
            save["load_control"] = True
        audio_player.cache_data.save(save)
        self.config_switch_2.configure(variable=BooleanVar(value=audio_player.cache_data.load()["load_control"]))
        self.config_warning_1.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="we")

    def toggle_auto_variable_updater(self):
        if not self.config_variable_auto_update:
            self.config_variable_auto_update = True
        else:
            self.config_variable_auto_update = False
        self.config_switch_3.configure(variable=BooleanVar(value=self.config_variable_auto_update))

    def refresh_variable_value(self):
        self.config_variable_label_1.configure(text=version)
        self.config_variable_label_2.configure(text=self.update_rate)
        self.config_variable_label_3.configure(text=self.script_dir)
        self.config_variable_label_4.configure(text=self.cover_size)
        self.config_variable_label_5.configure(text=self.queue_hidden)
        self.config_variable_label_6.configure(text=self.current_index)
        self.config_variable_label_7.configure(text=str(self.queue_buttons)[:70]+"...")
        self.config_variable_label_8.configure(text=str(self.songs)[:70]+"...")
        self.config_variable_label_9.configure(text=self.corrupted_index)
        self.config_variable_label_10.configure(text=self.current_song)
        self.config_variable_label_11.configure(text=self.seeked)
        self.config_variable_label_12.configure(text=self.ui_color)
        self.config_variable_label_13.configure(text=self.hover_color)
        self.config_variable_label_14.configure(text=self.progress_color)
        self.config_variable_label_15.configure(text=self.default_ui)
        self.config_variable_label_16.configure(text=audio_player.get_if_play_pause())
        self.config_variable_label_17.configure(text=audio_player.get_playback_position())
        self.config_variable_label_18.configure(text=audio_player.get_title(audio_player.get_filepath()))
        self.config_variable_label_19.configure(text=audio_player.get_duration())
        self.config_variable_label_20.configure(text=audio_player.get_volume())
        self.config_variable_label_21.configure(text=audio_player.get_int_volume())
        self.config_variable_label_22.configure(text=audio_player.get_muted())
        self.config_variable_label_23.configure(text=audio_player.get_busy())
        self.config_variable_label_24.configure(text=audio_player.get_paused())
        self.config_variable_label_25.configure(text=audio_player.get_fade_ms())
        self.config_variable_label_26.configure(text=str(audio_player.get_filepath())[:70]+"...")

    def on_resize(self, event):
        if event.widget == self:
            w = event.width
            h = event.height
            print(f"{w}, {h}")
            self.cover_size = max(min(w, h) - 500, 200)
            self.music_name_label.configure(font=("Segoe UI", h/30, "bold"))

            if not self.default_ui and self.audio_cover:
                self.audio_cover.configure(size=(self.cover_size, self.cover_size))
            self.default_cover.configure(size=(self.cover_size, self.cover_size))

            if max(w, h) >= 920:
                self.cover_label.grid(row=1, column=0, padx=(50, 0), pady=25, sticky="sw")
                self.music_name_label.grid(row=0, column=0, columnspan=2, pady=(30, 0), sticky="nsew")

                # self.parent_frame.grid_columnconfigure(1, weight=1)
                # self.parent_frame.grid_rowconfigure(0, weight=1)

                self.seeker_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
                self.control_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10), sticky="ew")
                self.current_path_label.grid(row=5, column=0, columnspan=2)
                pass
            else:
                self.cover_label.grid(row=1, column=0, padx=0, pady=5, sticky="nsew")
                self.music_name_label.grid(row=0, column=0, columnspan=1, pady=(30, 0), sticky="nsew")
                
                # self.parent_frame.grid_columnconfigure(0, weight=1)
                # self.parent_frame.grid_rowconfigure(1, weight=1)

                self.seeker_frame.grid(row=2, column=0, columnspan=1, sticky="ew")
                self.control_frame.grid(row=3, column=0, columnspan=1, pady=(0, 10), sticky="ew")
                self.current_path_label.grid(row=5, column=0, columnspan=1)
        
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
            self.update_volume_ui()
            self.config_button_3.configure(text="Mute")
        else:
            audio_player.mute_music()
            self.mute_button.configure(image=self.mute_img)
            self.config_mute_button.configure(image=self.mini_mute_img)
            self.config_button_3.configure(text="Unmute")

    def change_volume(self, volume):
        audio_player.set_volume(volume)
        self.update_volume_ui()

    def update_volume_ui(self):
        if audio_player.get_int_volume() <= 0:
            self.mute_button.configure(image=self.mute_img)
            self.config_mute_button.configure(image=self.mini_mute_img)
        elif audio_player.get_int_volume() <= 34:
            self.mute_button.configure(image=self.vol_1_img)
            self.config_mute_button.configure(image=self.mini_vol_1_img)
        elif audio_player.get_int_volume() <= 67:
            self.mute_button.configure(image=self.vol_2_img)
            self.config_mute_button.configure(image=self.mini_vol_2_img)
        elif audio_player.get_int_volume() <= 100:
            self.mute_button.configure(image=self.vol_3_img)
            self.config_mute_button.configure(image=self.mini_vol_3_img)
        self.volume_slider.set(audio_player.get_volume())
        self.config_slider_1.set(audio_player.get_volume())
        self.config_label_1.configure(text=f"{audio_player.get_int_volume()}%")
        self.config_button_3.configure(text="Mute")

    def enable_control_btn(self):
        self.play_button.configure(state="normal")
        self.prev_button.configure(state="normal")
        self.next_button.configure(state="normal")
        self.seeker_slider.configure(state="normal")
        self.config_play_button.configure(state="normal")
        self.config_next_button.configure(state="normal")

    def disable_control_btn(self):
        self.play_button.configure(state="disabled")
        self.prev_button.configure(state="disabled")
        self.next_button.configure(state="disabled")
        self.seeker_slider.configure(state="disabled")
        self.config_play_button.configure(state="disabled")
        self.config_next_button.configure(state="disabled")

    def reset_seeked(self):
        self.seeked = 0

    def reset_ui(self):
        for widgets in self.winfo_children():
            widgets.grid_remove()
        self.load_ui()
        self.update_volume_ui()
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
                self.config_player_duration.configure(text=f"{current_pos_min}:{current_pos_sec:02d} / {duration_min}:{duration_sec:02d}")
            else:
                self.seeker_slider.configure(to=1)
                self.seeker_slider.set(0)
                self.duration_label.configure(text=f"--:-- / --:--")
                self.config_player_duration.configure(text=f"--:-- / --:--")
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
            self.config_play_button.configure(image=self.mini_play_img)
        elif audio_player.get_if_play_pause() == "Resume":
            self.fade_in_unpause()
            self.play_button.configure(image=self.pause_img)
            self.config_play_button.configure(image=self.mini_pause_img)
        else:
            audio_player.play_music()
            self.play_button.configure(image=self.pause_img)
            self.config_play_button.configure(image=self.mini_pause_img)

    def media_controler_event(self, event):
        if not self.default_ui:
            self.media_controler()

    def rewind_music(self):
        # Curroipt 0, 1 
        # 2
        if self.get_absolute_playback() <= 5 and self.current_index >= 1:
            i = self.current_index
            while i >= 0:
                i -= 1
                if i not in self.corrupted_index:
                    self.on_click_queue(i)
                    break
            self.reset_seeked()
            # self.on_click_queue(i)
            self.play_button.configure(image=self.pause_img)
            self.config_play_button.configure(image=self.mini_pause_img)

            self.see_queue_list()

        # elif self.get_absolute_playback() <= 5 and self.current_index >= 1 and self.current_index - 1 in self.corrupted_index:
        #     self.reset_seeked()
        #     self.on_click_queue(self.current_index - 2)
        #     self.play_button.configure(image=self.pause_img)
        #     self.config_play_button.configure(image=self.mini_pause_img)
        else:
            self.reset_seeked()
            audio_player.rewind_music()
            self.play_button.configure(image=self.pause_img)
            self.config_play_button.configure(image=self.mini_pause_img)

    def next_music(self):
        # if not self.current_index >= len(self.songs) - 1 and not self.current_index + 1 in self.corrupted_index:
        #     self.reset_seeked()
        #     self.on_click_queue(self.current_index + 1)
        #     self.play_button.configure(image=self.pause_img)
        #     self.config_play_button.configure(image=self.mini_pause_img)
        if not self.current_index >= len(self.songs) - 1:
            i = self.current_index
            while i <= len(self.songs):
                i += 1
                if i not in self.corrupted_index:
                    self.on_click_queue(i)
                    break
            self.reset_seeked()
            # self.on_click_queue(i)
            self.play_button.configure(image=self.pause_img)
            self.config_play_button.configure(image=self.mini_pause_img)

            self.see_queue_list()

    def see_queue_list(self):
        if len(self.queue_buttons) >= 0 and not self.default_ui:
            y1, y2 = self.queue_list_frame._parent_canvas.yview()
            y1 = y1 * len(self.queue_buttons) * self.queue_buttons[0].winfo_height()
            y2 = y2 * len(self.queue_buttons) * self.queue_buttons[0].winfo_height()
            y3 = self.current_index * self.queue_buttons[0].winfo_height()
            if y1 >= y3:
                self.queue_list_frame._parent_canvas.yview_scroll(int(y1-y3)*-1, "units")
            elif y2 <= y3:
                self.queue_list_frame._parent_canvas.yview_scroll(int(y3-y1), "units")

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
        self.queue_buttons[self.current_index].configure(fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12), text_color=("black", "white"))
        self.queue_buttons[index].configure(fg_color=self.ui_color, hover_color=self.hover_color, font=("Segoe UI", 12, "bold"), text_color="white")
        self.current_index = index
        self.open_audio(index)

    def load_queue_list(self, path):
        name = f"{len(self.queue_buttons) + 1}.{audio_player.get_title(path)}"
        button = CTkButton(self.queue_list_frame, text=self.shorten_title(name), font=("Segoe UI", 12), text_color=("black", "white"), anchor="w", corner_radius=0, fg_color="transparent", hover_color=("gray70", "gray30"), text_color_disabled="red", command=lambda i = len(self.queue_buttons): self.on_click_queue(i))
        button.grid(row=len(self.queue_buttons), column=0, sticky="ew")
        button.bind("<Button-3>", lambda event, i = len(self.queue_buttons): self.queue_menu(event, i))
        if self.songs.index(path) in self.corrupted_index:
            button.configure(state="disabled")
        self.queue_buttons.append(button)

    def reset_queue_list(self, reset_songs=True):
        if reset_songs:
            self.songs = []
            self.corrupted_index = []
            if audio_player.cache_data.load()["load_queue"]:
                self.db.reset()
        for widgets in self.queue_list_frame.winfo_children():
            widgets.destroy()
        self.title(f"Qun Music Player | {version} by @qunalpha on Github")
        self.current_index = -1
        self.queue_buttons = []

    def queue_menu(self, event, index: int):
        array = [i for i in str(event)]
        array.pop(-1)
        for i in range(array.index("x")):
            array.pop(0)

    def onclick_config_button(self, index):
        self.general_config_button.configure(text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12))
        self.playback_config_button.configure(text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12))
        self.audio_config_button.configure(text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12))
        self.variable_config_button.configure(text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12))
        self.library_config_button.configure(text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12))
        self.appearance_config_button.configure(text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12))
        self.advanced_config_button.configure(text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12))
        self.log_config_button.configure(text_color=("black", "white"), fg_color="transparent", hover_color=("gray70", "gray30"), font=("Segoe UI", 12))
        self.general_config_frame.grid_forget()
        self.playback_config_frame.grid_forget()
        self.audio_config_frame.grid_forget()
        self.variable_config_frame.grid_forget()
        self.library_config_frame.grid_forget()
        self.appearance_config_frame.grid_forget()
        self.advanced_config_frame.grid_forget()
        self.log_config_frame.grid_forget()
        if index == 0:
            self.general_config_button.configure(text_color="white", fg_color=self.ui_color, hover_color=self.hover_color, font=("Segoe UI", 12, "bold"))
            self.general_config_frame.grid(row=0, column=0, sticky="nsew")
        elif index == 1:
            self.playback_config_button.configure(text_color="white", fg_color=self.ui_color, hover_color=self.hover_color, font=("Segoe UI", 12, "bold"))
            self.playback_config_frame.grid(row=0, column=0, sticky="nsew")
        elif index == 2:
            self.audio_config_button.configure(text_color="white", fg_color=self.ui_color, hover_color=self.hover_color, font=("Segoe UI", 12, "bold"))
            self.audio_config_frame.grid(row=0, column=0, sticky="nsew")
        elif index == 3:
            self.variable_config_button.configure(text_color="white", fg_color=self.ui_color, hover_color=self.hover_color, font=("Segoe UI", 12, "bold"))
            self.variable_config_frame.grid(row=0, column=0, sticky="nsew")
        elif index == 4:
            self.library_config_button.configure(text_color="white", fg_color=self.ui_color, hover_color=self.hover_color, font=("Segoe UI", 12, "bold"))
            self.library_config_frame.grid(row=0, column=0, sticky="nsew")
        elif index == 5:
            self.appearance_config_button.configure(text_color="white", fg_color=self.ui_color, hover_color=self.hover_color, font=("Segoe UI", 12, "bold"))
            self.appearance_config_frame.grid(row=0, column=0, sticky="nsew")
        elif index == 6:
            self.advanced_config_button.configure(text_color="white", fg_color=self.ui_color, hover_color=self.hover_color, font=("Segoe UI", 12, "bold"))
            self.advanced_config_frame.grid(row=0, column=0, sticky="nsew")
        elif index == 7:
            self.log_config_button.configure(text_color="white", fg_color=self.ui_color, hover_color=self.hover_color, font=("Segoe UI", 12, "bold"))
            self.log_config_frame.grid(row=0, column=0, sticky="nsew")

    def save_config(self):
        audio_player.set_fade_ms(int(self.config_entry_1.get()))
        self.update_rate = int(self.config_entry_2.get())

        cache_save = audio_player.cache_data.load()
        cache_save["update_rate"] = self.update_rate
        cache_save["fade_ms"] = audio_player.get_fade_ms()
        audio_player.cache_data.save(cache_save)

    def reset_config(self):
        self.config_entry_1.delete(0, END)
        self.config_entry_2.delete(0, END)
        self.config_entry_1.insert(0, 500)
        self.config_entry_2.insert(0, 250)

        self.save_config()

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
            # self.on_click_queue(0)
        if self.config_variable_auto_update:
            self.refresh_variable_value()
        
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
        
        def _add(paths):
            for song in paths:
                self.add_queue_list(song)
                if audio_player.cache_data.load()["load_queue"]:
                    self.db.add((song,))
            if not audio_player.get_busy():
                self.on_click_queue(0)

        threading.Thread(target=_add, args=(paths,), daemon=False).start()

    def open_audio(self, index):
        path = self.songs[index]
        
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
            size = self.cover_size
            self.audio_cover = CTkImage(self.image_processer(cover_image), size=(size, size))
            self.mini_cover_label.configure(image=CTkImage(self.image_processer(cover_image), size=(40, 40)))
            self.cover_label.configure(text="", image=self.audio_cover)
            #self.cover_label.image = audio_cover  # keep reference
        else:
            self.cover_label.configure(text="", image=self.default_cover)
            self.mini_cover_label.configure(image=self.default_mini_cover)
        try:
            audio_player.set_filepath(path)
            audio = File(path, easy=True)
            audio_player.load_music(path)
            self.music_name_label.configure(text=f"{audio.get("title", [os.path.basename(path)])[0]} | {audio.get("artist", ["Unknown"])[0]}")
            self.config_player_title.configure(text=f"{audio.get("title", [os.path.basename(path)])[0]}")
            self.current_path_label.configure(text=path)
            self.title(f"{audio.get("title", [os.path.basename(path)])[0]} | Qun Music Player {version}")
            self.enable_control_btn()
            self.play_button.configure(image=self.pause_img)
            self.config_play_button.configure(image=self.mini_pause_img)
            self.reset_seeked()
            self.default_ui = False
            audio_player.play_music()
        except:
            self.queue_buttons[index].configure(fg_color="transparent", hover_color="gray30", font=("Segoe UI", 12), state="disabled")
            # self.queue_buttons[index].configure(fg_color=self.ui_color, hover_color=self.hover_color, font=("Segoe UI", 12, "bold"))
            if not index in self.corrupted_index:
                self.corrupted_index.append(index)
            audio_player.reset()
            self.reset_ui()
            self.next_music()

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
        image = cropped_img.resize((200, 200))
        return image
    
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
    
    def open_music_player(self):
        self.config_frame.grid_remove()
        self.music_player_frame.grid()

    def open_config(self):
        self.config_frame.grid(row=0, column=0, sticky="nsew")
        self.music_player_frame.grid_remove()
            
    def open_github(self):
        webbrowser.open("https://github.com/qunalpha")

    def only_integer(self, value):
        return value.isdigit() or value == ""

if __name__ == "__main__":
    audio_player = audioPlayer()
    App(audio_player)
