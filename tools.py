import cv2 as cv


def start_camera(
    video_number: int = 0, video_res: list = [640, 480], frame_rate: int = 30
):
    try:
        cap = cv.VideoCapture(video_number, cv.CAP_DSHOW)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, video_res[0])
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, video_res[1])
        cap.set(cv.CAP_PROP_FPS, frame_rate)
        return cap
    except Exception as e:
        print(f"No camera detected, error: {e.args}")
        exit_program()


def flip_camera(frame, flip_type: int = 0):
    return cv.flip(frame, flip_type).tobytes()


def exit_program():
    print("Exiting the program...")
    sys.exit(0)
