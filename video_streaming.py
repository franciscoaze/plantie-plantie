# import the necessary packages
from imutils.video import WebcamVideoStream
from flask import Response
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2
from flask import Flask
import atexit

def OnExitApp():
    print("Exit Python application")

atexit.register(OnExitApp)


class VideoStreamer:
	outputFrame = None
	lock = None
	app = None
	vs = None

	PORT = '8000'

	app = Flask('video_stream')

	def __init__(self):

		self.stream = False

		self.app.add_url_rule('/video_on', 'video_on', self.start_new_stream)
		self.app.add_url_rule('/video_off', 'video_off', self.stop_stream)
		self.app.add_url_rule('/', 'index', index)
		self.app.add_url_rule('/video', 'video', self.video_feed)

		self.app.run(host='0.0.0.0', port=self.PORT, threaded=True, use_reloader=False)

	def start_new_stream(self):
		# initialize the output frame and a lock used to ensure thread-safe
		# exchanges of the output frames (useful when multiple browsers/tabs
		# are viewing the stream)
		print('starting new stream')
		self.outputFrame = None
		self.lock = threading.Lock()
		# initialize a flask object
		# initialize the video stream and allow the camera sensor to warmup
		print('pre initialize')
		try:
			self.vs = WebcamVideoStream(src=0)
		except:
			self.vs = WebcamVideoStream(src=-1)
		print(self.vs)
		self.vs.start()

		time.sleep(2.0)

		self.t = threading.Thread(target=self.get_frames, args=(32,))
		self.t.daemon = True
		self.t.start()
		# start the flask app
		self.stream = True
		print('new_stream started')
		return 'video streaming'


	def stop_stream(self):
		# release the video stream pointer
		self.stream = False
		self.vs.stream.release()
		self.vs.stop()
		print('stream stopped')
		return 'video stopped'


	def get_frames(self,frameCount):
		# grab global references to the video stream, output frame, and
		# lock variables
		total = 0
		print('entered thread')
		# loop over frames from the video stream
		while self.stream:
			print(total)
			# read the next frame from the video stream, resize it,
			# convert the frame to grayscale, and blur it
			frame = self.vs.read()
			frame = imutils.resize(frame, width=400)
			frame = cv2.flip(frame, 0)
			# frame = imutils.resize(frame, width=400)
			# grab the current timestamp and draw it on the frame
			timestamp = datetime.datetime.now()
			if frame is not None:
				cv2.putText(frame, timestamp.strftime(
					"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
							cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

				total += 1
				with self.lock:
					self.outputFrame = frame.copy()

	def generate(self):
		# grab global references to the output frame and lock variables
		# loop over frames from the output stream
		while True:
			# wait until the lock is acquired
			with self.lock:
				# check if the output frame is available, otherwise skip
				# the iteration of the loop
				if self.outputFrame is None:
					continue
				# encode the frame in JPEG format
				(flag, encodedImage) = cv2.imencode(".jpg", self.outputFrame)
				# ensure the frame was successfully encoded
				if not flag:
					continue
			# yield the output frame in the byte format
			yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


	def video_feed(self):
		# return the response generated along with the specific media
		# type (mime type)
		if self.stream:
			return Response(self.generate(), mimetype="multipart/x-mixed-replace; boundary=frame")
		else:
			return 'no video available'

def index():
	# return the rendered template
	return render_template("index.html")

if __name__ == '__main__':
    vs = VideoStreamer()

#
# # check to see if this is the main thread of execution
# if __name__ == '__main__':
#     # construct the argument parser and parse command line arguments
#     ap = argparse.ArgumentParser()
#     ap.add_argument("-i", "--ip", type=str, required=True,
#                     help="ip address of the device")
#     ap.add_argument("-o", "--port", type=int, required=True,
#                     help="ephemeral port number of the server (1024 to 65535)")
#     ap.add_argument("-f", "--frame-count", type=int, default=32,
#                     help="# of frames used to construct the background model")
#     args = vars(ap.parse_args())
#     # start a thread that will perform motion detection
#     t = threading.Thread(target=get_frames, args=(32,))
#     t.daemon = True
#     t.start()
#     # start the flask app
#     app.run(host=args["ip"], port=args["port"], debug=True,
#             threaded=True, use_reloader=False)
# release the video stream pointer
# vs.stop()

