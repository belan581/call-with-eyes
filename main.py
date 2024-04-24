import mediapipe as mp
from kivymd.app import App
from kivymd.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import cv2
import threading
import time
from tools import can_process, move_slider


class MainApp(App):

    WEBCAM_RAW_RES = (640, 480)
    FRAMERATE = 20
    stop_threads = False
    can_process = False
    it_moves = False
    direction = ""

    def start_camera(self, *args):
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.capture.set(cv2.CAP_PROP_FPS, self.FRAMERATE)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.WEBCAM_RAW_RES[0])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.WEBCAM_RAW_RES[1])
        # self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*"MJPG"))
        Clock.schedule_interval(self.load_video, 1.0 / 30.0)

    def build(self):
        layout = GridLayout(
            cols=2,
            col_force_default=True,
            col_default_width=400,
        )
        self.image = Image()
        layout.add_widget(self.image)
        self.start_camera()
        # Inicializar el carrusel
        self.carousel = Carousel(direction="bottom")
        for i in range(6):
            src = "http://placehold.it/480x270.png&text=slide-%d.png" % i
            image = AsyncImage(source=src, fit_mode="contain")
            self.carousel.add_widget(image)
        self.t1 = threading.Thread(target=self.change_carousel)
        self.t1.start()
        layout.add_widget(self.carousel)
        # Inicializar MediaPipe Face Mesh
        self.landmarks = [168, 67, 297, 127, 264, 205, 425, 468, 473]
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        return layout

    def change_carousel(self, *args):
        print(self.stop_threads)
        while not (MainApp.get_running_app()):
            pass
        while True:
            if self.can_process:
                if self.it_moves:
                    if self.direction == "up":
                        self.carousel.load_previous()
                        print(f"Se mueve slider hacia:{self.direction}")
                        # self.direction = ""
                    elif self.direction == "down":
                        self.carousel.load_next()
                        print(f"Se mueve slider hacia:{self.direction}")
                        # self.direction = ""
                    time.sleep(2)
            if self.stop_threads:
                print("Se detiene thread en bg")
                break

    def landmarks_to_px(self, landmark, image_width, image_height):
        return int(landmark.x * image_width), int(landmark.y * image_height)

    def load_video(self, *args):
        ret, frame = self.capture.read()
        with self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as face_mesh:

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            frame.flags.writeable = False
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame)
            # Draw the face mesh annotations on the image.
            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    points = []
                    for idx, landmark in enumerate(face_landmarks.landmark):
                        if idx in self.landmarks:
                            point = [idx, landmark.x, landmark.y]
                            points.append(point)
                            point = self.landmarks_to_px(landmark, 640, 480)
                            cv2.circle(frame, point, 2, (0, 255, 0), -1)
                            # Colocar la etiqueta del número de punto
                            cv2.putText(
                                frame,
                                str(idx),
                                point,
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.3,
                                (255, 255, 255),
                                1,
                            )
                    self.can_process = can_process(points)
                    if self.can_process:
                        self.it_moves, self.direction = move_slider(points)
                        # time.sleep(2)

        self.image_frame = frame
        buffer = cv2.flip(frame, 0).tostring()
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
