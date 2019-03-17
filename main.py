# TODO: Fix relative path issues on PI (after adding the server to run on boot)
# TODO: Remove unused imports
import communication.data_manager as dm
from communication.server import Server
from communication.video_stream import VideoStream
from cv2 import VideoCapture


# TODO: Remove this test script
def sample_video_stream():
    cap = VideoCapture(0)
    while True:
        ret, frame = cap.read()
        video_stream.frame = frame


# TODO: Remove this test script
def sample_text_debug():
    while True:
        print(dm.get_data(dm.SURFACE), dm.get_data(dm.ARDUINO_A), dm.get_data(dm.ARDUINO_I), dm.get_data(dm.ARDUINO_M))


if __name__ == "__main__":

    # Clear the cache on start
    dm.clear()

    # Initialise the server
    server = Server()

    # Initialise the video stream
    video_stream = VideoStream()

    # Start the tasks
    server.run()
    video_stream.run()

    # TODO: Remove this test script
    sample_video_stream()
