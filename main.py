from kivy.config import Config

Config.set("graphics", "resizable", False)
Config.set("graphics", "width", "1280")
Config.set("graphics", "height", "720")

from kivymd.app import App
from kivymd.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import threading
import time
import statistics as st
import winsound

from tools import start_camera, flip_camera
from eyes_move_detection import eyesMoveDetection


class MainApp(App):
    stop_threads = False
    can_process = False
    points = []
    gestures = []
    right_iris = any
    left_iris = any
    counter = 0
    direction = ""
    video_res = [640, 480]
    needs = [0, 1, 2, 3, 4]

    def build(self):
        layout = GridLayout(
            cols=2,
        )
        boxLayout = BoxLayout(orientation="vertical")
        self.image = Image()
        self.image_up = Image(
            source="images/image4.jpg",
            size_hint_x=0.4,
            allow_stretch=True,
        )
        self.image_down = Image(
            source="images/image1.jpg",
            size_hint_x=0.4,
            allow_stretch=True,
        )
        # layout.add_widget(self.image)
        self.carousel = Carousel(direction="bottom", loop=True)
        for i in range(5):
            src = f"images/image{i}.jpg"
            image = AsyncImage(source=src, fit_mode="contain")
            self.carousel.add_widget(image)
        # Inicializar el video en hilo
        self.capture = start_camera(
            video_number=0, frame_rate=10, video_res=self.video_res
        )
        Clock.schedule_interval(self.load_video_thread, 1.0 / 10.0)
        # Inicializar movimiento de carrusel en hilo
        self.t1 = threading.Thread(target=self.change_carousel_thread)
        self.t1.start()
        # Add the widgets
        layout.add_widget(self.image)
        boxLayout.add_widget(self.image_up)
        boxLayout.add_widget(self.carousel)
        boxLayout.add_widget(self.image_down)
        layout.add_widget(boxLayout)

        # Inicializar deteccion de ojos
        self.eyes_m_d = eyesMoveDetection()
        return layout

    def change_carousel_thread(self, *args):

        def change_options(index: int):
            self.image_up.source = f"images/image{self.needs[index - 1]}.jpg"
            if index == 4:
                self.image_down.source = f"images/image{0}.jpg"
            else:
                self.image_down.source = f"images/image{self.needs[index + 1]}.jpg"

        print(self.stop_threads)
        while not (MainApp.get_running_app()):
            print("Wait for initialize the camera...")
        while True:
            if self.can_process:
                mode = 3
                gesto = self.eyes_m_d.compute_gesture(
                    self.points, self.right_iris, self.left_iris
                )

                self.gestures.append(gesto)
                if len(self.gestures) == 17:
                    mode = st.mode(self.gestures)
                    self.gestures.clear()

                if mode == 0:
                    change_options(self.carousel.index)
                    self.carousel.load_next()
                    print("Carga siguiente")
                elif mode == 1:
                    change_options(self.carousel.index)
                    self.carousel.load_previous()
                    print("Carga anterior")
                elif mode == 2:
                    print(f"Accion: {self.carousel.index}")
                    winsound.PlaySound("*", winsound.SND_ALIAS)
                else:
                    print("No hay cambio en mirada")
                # time.sleep(1 / 5)
            if self.stop_threads:
                print("Se detiene thread en bg")
                break

    def load_video_thread(self, *args):
        ret, frame = self.capture.read()
        frame, self.points, self.can_process, self.right_iris, self.left_iris = (
            self.eyes_m_d.get_landmarks_coordinates(frame, video_res=self.video_res)
        )
        buffer = flip_camera(frame, -1)
        texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]),
            colorfmt="bgr",
        )
        texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
        self.image.texture = texture

    def on_stop(self):
        self.stop_threads = True
        self.t1.join()


if __name__ == "__main__":
    app = MainApp()
    app.run()
