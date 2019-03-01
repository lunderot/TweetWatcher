
from twython import Twython
from twython import TwythonStreamer
import json
import urllib
import threading
import time
import urllib.request
import cv2
import numpy as np

with open("settings.json", "r") as read_file:
    settings = json.load(read_file)

with open("auth.json", "r") as read_file:
    auth = json.load(read_file)

photo_list = []
processed_list = []

class FaceScanner():
	def __init__(self):
		self.processed = 0
		self.interval = 1
		threading.Thread(target=self.face_scanner).start()
	
	def face_scanner(self):
		while(True):
			if len(photo_list) > self.processed:
				image = self.download_photo(photo_list[self.processed]['url'])
				faces = self.detect_faces(image)
				if len(faces) > 0:
					processed_list.append({	'url': photo_list[self.processed]['media_url'],
											'id': photo_list[self.processed]['id_str'],
											'faces': faces
											})
				self.processed += 1
			time.sleep(self.interval)
	
	def download_photo(self, url):
		response = urllib.request.urlopen(url)
		image = np.asarray(bytearray(response.read()), dtype="uint8")
		image = cv2.imdecode(image, cv2.IMREAD_COLOR)
		return image
	
	def detect_faces(self, image):
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		cascade_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
		return cascade_classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30), flags = cv2.CASCADE_SCALE_IMAGE)



class MyStreamer(TwythonStreamer):
	def on_success(self, data):
		if 'extended_entities' in data and 'media' in data['extended_entities']:
			for i in data['extended_entities']['media']:
				if i['type'] == 'photo':
					#print(f"{i['media_url']} https://twitter.com/user/status/{data['id_str']}")
					photo_list.append({'url': i['media_url'], 'id': data['id_str']})

	def on_error(self, status_code, data):
		print(status_code, data)



def twitter_stream():
	stream = MyStreamer(auth['APP_KEY'], auth['APP_SECRET'], auth['OAUTH_TOKEN'], auth['OAUTH_TOKEN_SECRET'])
	stream.statuses.filter(track=settings['track'])

if __name__ == "__main__":
	FaceScanner()
	twitter_stream()