from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivymd.app import App
from kivymd.uix.gridlayout import GridLayout

from tools import flip_camera, start_camera


class MainApp(App):
    frame = any

    def build(self):
        layout = GridLayout(
            cols=1,
            rows=2,
        )
        self.image = Image()
        layout.add_widget(
            self.image,
        )
        self.buttons_layout = BoxLayout(size_hint_y=0.2)
        self.btn1 = Button(text="Mirar abajo")
        self.btn2 = Button(text="Mirar arriba")
        self.btn3 = Button(text="Cerrar ojos")
        self.btn4 = Button(text="Sin accion")
        self.buttons_layout.add_widget(self.btn1)
        self.buttons_layout.add_widget(self.btn2)
        self.buttons_layout.add_widget(self.btn3)
        self.buttons_layout.add_widget(self.btn4)
        layout.add_widget(self.buttons_layout)
        # Inicializar el video en hilo
        self.capture = start_camera(
            video_number=0, frame_rate=20, video_res=[1280, 720]
        )
        Clock.schedule_interval(self.load_video_thread, 1.0 / 20.0)
        return layout

    def load_video_thread(self, *args):
        ret, self.frame = self.capture.read()
        buffer = flip_camera(self.frame, 0)
        texture = Texture.create(
            size=(self.frame.shape[1], self.frame.shape[0]),
            colorfmt="bgr",
        )
        texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
        self.image.texture = texture


if __name__ == "__main__":
    app = MainApp()
    app.run()
