from kivymd.app import MDApp
from kivymd.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from  kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import cv2 


class MainApp(MDApp):

    def build(self):
        layout = GridLayout(cols = 2, col_force_default = True, col_default_width = 400)
        self.image = Image()
        layout.add_widget(self.image)
        carousel = Carousel(direction='bottom')
        for i in range(6):
            src = "http://placehold.it/480x270.png&text=slide-%d.png" % i
            image = AsyncImage(source=src, fit_mode="contain")
            carousel.add_widget(image)
        layout.add_widget(carousel)
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.load_video, 1.0/30.0)
        return layout
    
    def load_video(self, *args):
        ret, frame = self.capture.read()
        self.image_frame = frame
        buffer = cv2.flip(frame,0).tostring()
        texture = Texture.create(size = (frame.shape[1], frame.shape[0]), colorfmt = "bgr")
        texture.blit_buffer(buffer, colorfmt = "bgr", bufferfmt = "ubyte")
        self.image.texture = texture
    
    
if __name__ == "__main__":
    MainApp().run()