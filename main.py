import communication.data_manager as dm
from communication.server import Server
from communication.video_stream import VideoStream
from cv2 import VideoCapture
from time import sleep


# TODO: Remove this test script
def blocking_test_video_stream(streams):
    caps = []
    for iterator, stream in enumerate(streams):
        caps.append(VideoCapture(iterator))
    while True:
        for iterator, stream in enumerate(streams):
            ret, frame = caps[iterator].read()
            stream.frame = frame


# TODO: Remove this test script
def blocking_test_text_debug():
    while True:
        print(dm.get_data(dm.SURFACE), dm.get_data(dm.ARDUINO_A), dm.get_data(dm.ARDUINO_I), dm.get_data(dm.ARDUINO_M))
        sleep(0.5)


if __name__ == "__main__":

    # Clear the cache on start
    dm.clear()

    # Initialise the server
    server = Server()

    # Initialise the video streams
    video_stream = VideoStream()
    vs = VideoStream(port=50002)

    # Start the tasks
    server.run()
    video_stream.run()
    vs.run()
