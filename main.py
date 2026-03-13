import os
import random

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.core.window import Window

Window.clearcolor = (0.1,0.1,0.1,1)

music_folder = "/sdcard/Music"

songs = []

if os.path.exists(music_folder):
    for file in os.listdir(music_folder):
        if file.endswith(".mp3"):
            songs.append(os.path.join(music_folder,file))


class MusicPlayer(App):

    def build(self):

        self.index = 0
        self.sound = None
        self.is_seeking = False

        main = BoxLayout(orientation="vertical")

        title = Label(text="My Music Player",font_size=24,size_hint=(1,0.08))
        main.add_widget(title)

        self.song_label = Label(text="No Song",size_hint=(1,0.07))
        main.add_widget(self.song_label)

        self.time_label = Label(text="0:00 / 0:00",size_hint=(1,0.05))
        main.add_widget(self.time_label)

        # Playlist
        scroll = ScrollView(size_hint=(1,0.35))

        self.song_list = GridLayout(cols=1,size_hint_y=None)
        self.song_list.bind(minimum_height=self.song_list.setter('height'))

        for song in songs:

            name = os.path.basename(song)

            btn = Button(
                text=name[:40],
                size_hint_y=None,
                height=60
            )

            btn.fullpath = song
            btn.bind(on_press=self.play_selected)

            self.song_list.add_widget(btn)

        scroll.add_widget(self.song_list)
        main.add_widget(scroll)

        # Controls
        controls = BoxLayout(size_hint=(1,0.1))

        prev = Button(text="Prev")
        play = Button(text="Play")
        pause = Button(text="Pause")
        next = Button(text="Next")
        shuffle = Button(text="Shuffle")

        prev.bind(on_press=self.prev_song)
        play.bind(on_press=self.play_song)
        pause.bind(on_press=self.pause_song)
        next.bind(on_press=self.next_song)
        shuffle.bind(on_press=self.shuffle_song)

        controls.add_widget(prev)
        controls.add_widget(play)
        controls.add_widget(pause)
        controls.add_widget(next)
        controls.add_widget(shuffle)

        main.add_widget(controls)

        # Seek bar
        self.seek = Slider(min=0,max=100,value=0)

        self.seek.bind(on_touch_down=self.start_seek)
        self.seek.bind(on_touch_up=self.stop_seek)

        main.add_widget(self.seek)

        # Volume
        volume = BoxLayout(size_hint=(1,0.08))

        vdown = Button(text="Vol -")
        mute = Button(text="Mute")
        vup = Button(text="Vol +")

        vdown.bind(on_press=self.volume_down)
        mute.bind(on_press=self.mute_song)
        vup.bind(on_press=self.volume_up)

        volume.add_widget(vdown)
        volume.add_widget(mute)
        volume.add_widget(vup)

        main.add_widget(volume)

        Clock.schedule_interval(self.update_slider,0.5)

        return main


    def play_selected(self,instance):

        if self.sound:
            self.sound.stop()

        self.sound = SoundLoader.load(instance.fullpath)

        self.song_label.text = os.path.basename(instance.fullpath)

        if self.sound:
            self.sound.play()


    def play_song(self,instance):

        if self.sound:
            self.sound.play()


    def pause_song(self,instance):

        if self.sound:
            self.sound.stop()


    def next_song(self,instance):

        if len(songs)==0:
            return

        self.index=(self.index+1)%len(songs)

        self.play_file(songs[self.index])


    def prev_song(self,instance):

        if len(songs)==0:
            return

        self.index=(self.index-1)%len(songs)

        self.play_file(songs[self.index])


    def shuffle_song(self,instance):

        if len(songs)==0:
            return

        self.index=random.randint(0,len(songs)-1)

        self.play_file(songs[self.index])


    def play_file(self,file):

        if self.sound:
            self.sound.stop()

        self.sound = SoundLoader.load(file)

        self.song_label.text = os.path.basename(file)

        if self.sound:
            self.sound.play()


    def update_slider(self,dt):

        if self.sound and self.sound.length and not self.is_seeking:

            pos=self.sound.get_pos()

            if pos>=0:

                self.seek.max=self.sound.length
                self.seek.value=pos

                m=int(pos//60)
                s=int(pos%60)

                tm=int(self.sound.length//60)
                ts=int(self.sound.length%60)

                self.time_label.text=f"{m}:{s:02d} / {tm}:{ts:02d}"


    def start_seek(self,instance,touch):

        if instance.collide_point(*touch.pos):

            self.is_seeking=True


    def stop_seek(self,instance,touch):

        if instance.collide_point(*touch.pos):

            if self.sound:

                self.sound.seek(self.seek.value)

            Clock.schedule_once(self.enable_seek,1)


    def enable_seek(self,dt):

        self.is_seeking=False


    def mute_song(self,instance):

        if self.sound:
            self.sound.volume=0


    def volume_up(self,instance):

        if self.sound:
            self.sound.volume=min(1,self.sound.volume+0.1)


    def volume_down(self,instance):

        if self.sound:
            self.sound.volume=max(0,self.sound.volume-0.1)


MusicPlayer().run()
