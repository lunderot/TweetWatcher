
from twython import Twython
from twython import TwythonStreamer
import json
import urllib
import threading
import time
import urllib.request
import cv2
import cvlib as cv
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
		self.interval = 0.01
		threading.Thread(target=self.face_scanner).start()
	
	def face_scanner(self):
		while(True):
			if len(photo_list) > self.processed:
				image = self.download_photo(photo_list[self.processed]['url'])
				faces, _ = cv.detect_face(image)
				for f in faces:
					gender = self.detect_gender(image, f)
					processed_list.append({	'url': photo_list[self.processed]['url'],
											'id': photo_list[self.processed]['id'],
											'gender': gender,
											'box': [[f[0], f[1]], [f[2], f[3]]]
											})
					print(processed_list[-1])
				self.processed += 1
			time.sleep(self.interval)
	
	def detect_gender(self, image, f):
		(startX,startY) = f[0],f[1]
		(endX,endY) = f[2],f[3]
		face_crop = np.copy(image[startY:endY, startX:endX])
		(label, confidence) = cv.detect_gender(face_crop)
		index = np.argmax(confidence)
		gender = label[index]
		return gender

	def download_photo(self, url):
		response = urllib.request.urlopen(url)	
		image = np.asarray(bytearray(response.read()), dtype="uint8")
		image = cv2.imdecode(image, cv2.IMREAD_COLOR)
		return image



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