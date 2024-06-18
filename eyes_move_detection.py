import csv
import math
import os
import time
import winsound

import cv2 as cv
import joblib
import mediapipe as mp
import numpy as np

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from tensorflow.keras.models import load_model


class eyesMoveDetection:

    # Interest points
    # right_eye = [157, 158, 159, 160, 161, 163, 144, 145, 153, 154, 155, 246, 33, 133]
    right_eye = [157, 158, 159, 160, 161, 163, 144, 145, 153, 154]
    iris_derecho = [468]
    left_eye = [384, 385, 386, 387, 388, 390, 373, 374, 380, 381]
    iris_izquierdo = [473]
    references = [67, 297, 127, 264, 205, 425, 168]
    train_landmarks = right_eye + left_eye
    full_landmarks = train_landmarks + iris_izquierdo + iris_derecho
    # Load de model
    model = load_model("model/modelo_call_with_eyes.h5")

    # Load the scaler
    scaler = joblib.load("model/scaler_entrenamiento.pkl")

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
                    ref_points = []
                    for idx, landmark in enumerate(face_landmarks.landmark):
                        if idx in self.train_landmarks:
                            point = [idx, landmark.x, landmark.y]
                            points.append(point)
                            point = self.landmarks_to_px(
                                landmark, video_res[0], video_res[1]
                            )
                            cv.circle(frame, point, 2, (0, 255, 0), -1)
                        if idx in self.references:
                            ref_point = [idx, landmark.x, landmark.y]
                            ref_points.append(ref_point)
                        if idx in self.iris_derecho:
                            right_iris = idx, landmark.x, landmark.y
                        if idx in self.iris_izquierdo:
                            left_iris = idx, landmark.x, landmark.y

                return (
                    frame,
                    points,
                    self.can_process(points + ref_points),
                    right_iris,
                    left_iris,
                )
            else:
                return frame, [], False, [], []

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

    def compute_gesture(self, points, right_iris, left_iris):
        distances = []
        for p in points:
            try:
                distances.append(self.calcular_distancia(punto1=p, punto2=right_iris))
            except Exception as e:
                distances.append(0.0)
                print(f"Error: {e.args}")
        for p in points:
            try:
                distances.append(self.calcular_distancia(punto1=p, punto2=left_iris))
            except Exception as e:
                distances.append(0.0)
                print(f"Error: {e.args}")
        # caracteristicas = np.array([distances])
        X_sample = np.array([distances])
        # X_sample = np.expand_dims(distances, axis=0)
        X_sample_normalized = self.scaler.transform(X_sample)
        gesto_predicho = self.model.predict(X_sample_normalized).argmax()
        # gesto_predicho_prob = np.argmax(gesto_predicho, axis=1)
        return gesto_predicho

    def save_gesture(self, option: int, frame, freq):
        data = []
        with self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as face_mesh:
            for i in range(100):
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
                    # print(points)
                    distances = []
                    for p in points:
                        try:
                            distances.append(
                                self.calcular_distancia_dos(punto1=p, punto2=right_iris)
                            )
                        except Exception as e:
                            distances.append(0.0)
                            print(f"Error: {e.args}")
                        # print(f"distance_right:{distances}")
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
                        # print(f"distance_right:{distances}")
                    distances.append(option)
                    print(len(distances))
                    data.append(distances)
                    time.sleep(freq)
            self.write_data(data, "distances")
            winsound.PlaySound("*", winsound.SND_ALIAS)

    def write_data(self, data, name):
        with open(f"{name}.csv", "a", newline="") as file:
            writer = csv.writer(file, delimiter=",")
            writer.writerows(data)
            file.close()
