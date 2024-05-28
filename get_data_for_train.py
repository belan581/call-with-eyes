from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivymd.app import App
from kivymd.uix.gridlayout import GridLayout
import threading

from eyes_move_detection import eyesMoveDetection
from tools import flip_camera, start_camera

eyes_gesture = [
    (0, "look_down"),
    (1, "look_up"),
    (2, "close_eyes"),
    (3, "no_action"),
]

FREQ = 1.0 / 20.0


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
        self.btn = []
        for a in eyes_gesture:
            self.btn.append(Button(text=a[1]))
            self.btn[-1].bind(on_press=lambda x, a=a: self.capture_thread(a[0]))
            self.buttons_layout.add_widget(self.btn[-1])
        layout.add_widget(self.buttons_layout)
        # Inicializar el video en hilo
        self.capture = start_camera(
            video_number=0, frame_rate=20, video_res=[1280, 720]
        )
        Clock.schedule_interval(self.load_video_thread, FREQ)
        self.eyes_m_d = eyesMoveDetection()
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

    def capture_thread(self, option: int):
        t1 = threading.Thread(
            target=self.eyes_m_d.save_gesture, args=(option, self.frame, FREQ)
        )
        t1.start()


if __name__ == "__main__":
    app = MainApp()
    app.run()
