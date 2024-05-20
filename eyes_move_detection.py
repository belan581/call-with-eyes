import math
import time
import cv2 as cv
import csv
import mediapipe as mp
import random


class eyesMoveDetection:

    # definir los puntos a analizar
    ojo_derecho = [157, 158, 159, 160, 161, 163, 144, 145, 153, 154]
    iris_derecho = [468]
    ojo_izquierdo = [384, 385, 386, 387, 388, 390, 373, 374, 380, 381]
    iris_izquierdo = [473]
    referencias = [67, 297, 127, 264, 205, 425, 168]
    train_landmarks = ojo_derecho + ojo_izquierdo + referencias
    full_landmarks = train_landmarks + iris_izquierdo + iris_derecho

    def __init__(self):
        self.mp_face_mesh = self.load_mediapipe()

    def load_mediapipe(self):
        mp_face_mesh = mp.solutions.face_mesh
        return mp_face_mesh

    def landmarks_to_px(self, landmark, image_width, image_height):
        return int(landmark.x * image_width), int(landmark.y * image_height)

    def get_landmarks_coordinates(self, frame, video_res=[1280, 720]):
        with self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as face_mesh:

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            frame.flags.writeable = False
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            results = face_mesh.process(frame)
            # Draw the face mesh annotations on the image.
            frame.flags.writeable = True
            frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    points = []
                    for idx, landmark in enumerate(face_landmarks.landmark):
                        if idx in self.full_landmarks:
                            point = [idx, landmark.x, landmark.y]
                            points.append(point)
                            point = self.landmarks_to_px(
                                landmark, video_res[0], video_res[1]
                            )
                            cv.circle(frame, point, 2, (0, 255, 0), -1)
                            # Colocar la etiqueta del número de punto
                            cv.putText(
                                frame,
                                str(idx),
                                point,
                                cv.FONT_HERSHEY_SIMPLEX,
                                0.3,
                                (255, 255, 255),
                                1,
                            )
            return frame, points, self.can_process(points)

    def calcular_distancia(self, punto1, punto2):
        dx = (punto1[1] - punto2[1]) ** 2
        dy = (punto1[2] - punto2[2]) ** 2
        return math.sqrt(dx + dy)

    def calcular_distancia_dos(self, punto1, punto2):
        dx = (punto1[0] - punto2[0]) ** 2
        dy = (punto1[1] - punto2[1]) ** 2
        return math.sqrt(dx + dy)

    def is_close(self, d1, d2):
        close = math.isclose(d1, d2, rel_tol=0.1)
        return close

    def compute_direction(d1, d2, d3, d4):
        volado = random.randint(0, 1)
        if volado:
            print("up")
            return "up"
        print("down")
        return "down"

    def it_moves(self, d1, d2, d3, d4):
        # print(f"d1:{d1}, d2:{d2}, d3:{d3}, d4:{d4}")
        res = d1 / d2
        dir = ""
        print(f"res:{res}")
        if res < 0.90:
            dir = "up"
        elif res > 1.05:
            dir = "down"
        print(f"dir:{dir}")
        return dir

    def signal_analyze():
        pass

    def get_data(self, x, lst):
        res = [(i, row) for i, row in enumerate(lst) if x in row]
        return res[0][1]

    def can_process(self, data):
        center = self.get_data(168, data)
        right = self.get_data(127, data)
        left = self.get_data(264, data)
        d_center_right = self.calcular_distancia(center, right)
        d_center_left = self.calcular_distancia(center, left)
        res = self.is_close(d_center_right, d_center_left)
        return res

    def move_slider(self, data):
        iris_center_right = self.get_data(468, data)
        iris_center_left = self.get_data(473, data)
        up_right = self.get_data(67, data)
        up_left = self.get_data(297, data)
        down_right = self.get_data(205, data)
        down_left = self.get_data(425, data)
        d_iris_up_left = self.calcular_distancia(iris_center_left, up_left)
        d_iris_up_right = self.calcular_distancia(iris_center_right, up_right)
        d_iris_down_left = self.calcular_distancia(iris_center_left, down_left)
        d_iris_down_right = self.calcular_distancia(iris_center_right, down_right)
        dir = self.it_moves(
            d_iris_up_left,
            d_iris_down_left,
            d_iris_up_right,
            d_iris_down_right,
        )

        return dir

    def save_gesture(self, option: int, frame, freq):
        data = []
        with self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as face_mesh:
            for i in range(10):
                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                frame.flags.writeable = False
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                results = face_mesh.process(frame)
                # Draw the face mesh annotations on the image.
                frame.flags.writeable = True
                frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        points = []
                        right_iris = []
                        left_iris = []
                        for idx, landmark in enumerate(face_landmarks.landmark):
                            if idx in self.train_landmarks:
                                point = landmark.x, landmark.y
                                points.append(point)
                            if idx in self.iris_derecho:
                                right_iris = landmark.x, landmark.y
                            if idx in self.iris_izquierdo:
                                left_iris = landmark.x, landmark.y
                    print(points)
                    distances = []
                    for p in points:
                        try:
                            distances.append(
                                self.calcular_distancia_dos(punto1=p, punto2=right_iris)
                            )
                        except Exception as e:
                            distances.append(0.0)
                            print(f"Error: {e.args}")
                        print(f"distance_right:{distances}")
                    # distances.append(option)
                    # data.append(distances)
                    for p in points:
                        try:
                            distances.append(
                                self.calcular_distancia_dos(punto1=p, punto2=left_iris)
                            )
                        except Exception as e:
                            distances = 0
                            print(f"Error: {e.args}")
                        print(f"distance_right:{distances}")
                    distances.append(option)
                    data.append(distances)
                    time.sleep(freq)
            self.write_data(data, "distances")

    def write_data(self, data, name):
        with open(f"{name}.csv", "a", newline="") as file:
            writer = csv.writer(file, delimiter=",")
            writer.writerows(data)
            file.close()
