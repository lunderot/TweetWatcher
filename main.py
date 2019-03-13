import json
import threading
import time
import cv2
import cvlib as cv
import numpy as np
from twython import TwythonStreamer
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.response import FileResponse
import requests

class RunningAverage():
    def __init__(self, interval = 3600):
        self.list = []
        self.initial_time = time.time()
        self.interval = interval

    def append(self, amount = 1):
        index = int((time.time()-self.initial_time)/self.interval)
        if len(self.list) <= index:
            self.list.append(0)
        self.list[index] += amount

    def get(self):
        return sum(self.list)/len(self.list)

settings = {}
auth = {}
photo_list = []
twitter_tracker = None
twitter_tracker_stop = False
running_average_men = RunningAverage()
running_average_women = RunningAverage()
running_average_tweets = RunningAverage()
processed_list = {
    'tweets_per_hour': 0,
    'men_per_hour': 0,
    'women_per_hour': 0,
    'man': 0,
    'woman': 0,
    'images': []
}

class FaceScanner():
    def __init__(self):
        self.processed = 0
        self.interval = 0.01
        threading.Thread(target=self.face_scanner).start()
    def face_scanner(self):
        while True:
            if len(photo_list) > self.processed:
                image = self.download_photo(photo_list[self.processed]['url'])
                if image is None:
                    self.processed += 1
                    continue
                faces, _ = cv.detect_face(image)
                for f in faces:
                    w, h = image.shape[:2]
                    x0, x1 = np.clip(f[0:3:2], 0, w) #cap the coordinates to the image size
                    y0, y1 = np.clip(f[1:4:2], 0, h)
                    if x0 == x1 or y0 == y1: #if the capped coordinates are equal, the image is outside of the bounds; ignore it
                        break
                    gender = self.detect_gender(image, [x0, y0, x1, y1])
                    processed_list[gender] += 1
                    if gender == 'man':
                        running_average_men.append()
                    else:
                        running_average_women.append()
                processed_list['images'].append(photo_list[self.processed]['url'])
                if len(processed_list['images']) > 10:
                    processed_list['images'].pop(0)
                self.processed += 1
            else:
                time.sleep(self.interval)
    
    def detect_gender(self, image, face_coords):
        x0, x1 = face_coords[0:3:2]
        y0, y1 = face_coords[1:4:2]
        face_crop = np.copy(image[y0:y1, x0:x1])
        label, confidence = cv.detect_gender(face_crop)
        index = np.argmax(confidence)
        gender = label[index]
        return gender

    def download_photo(self, url):
        try:
            response = requests.get(url, timeout=5)
        except:
            return None
        if len(response.content) == 0:
            return None
        image = np.asarray(bytearray(response.content), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image



class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        global twitter_tracker_stop
        if twitter_tracker_stop:
            self.disconnect()
        running_average_tweets.append()
        if 'extended_entities' in data and 'media' in data['extended_entities']:
            for i in data['extended_entities']['media']:
                if i['type'] == 'photo':
                    #print(f"{i['media_url']} https://twitter.com/user/status/{data['id_str']}")
                    photo_list.append({'url': i['media_url'], 'id': data['id_str']})

    def on_error(self, status_code, data):
        print(status_code, data)


def twitter_stream():
    while True:
        global twitter_tracker_stop
        twitter_tracker_stop = False
        twitter_tracker.statuses.filter(track=settings['track'])

def web_static(request):
    filename = request.matchdict["name"]
    try:
        response = FileResponse(f'web/{filename}')
    except IOError:
        response = Response()
        response.status_int = 404
    return response

def web_index(request):
    return FileResponse('web/index.html')

def web_data(request):
    processed_list['tweets_per_hour'] = running_average_tweets.get()
    processed_list['men_per_hour'] = running_average_men.get()
    processed_list['women_per_hour'] = running_average_women.get()
    return Response(json.dumps(processed_list))

def web_post(request):
    global settings
    settings = json.loads(request.body)
    global twitter_tracker_stop
    twitter_tracker_stop = True
    with open('settings.json', 'w') as file:
        json.dump(settings, file)
    return Response(json.dumps({'data':'success'}))

if __name__ == "__main__":
    running_average_intitial_time = time.time()
    with open("settings.json", "r") as read_file:
        settings = json.load(read_file)

    with open("auth.json", "r") as read_file:
        auth = json.load(read_file)

    FaceScanner()
    twitter_tracker = MyStreamer(auth['APP_KEY'], auth['APP_SECRET'], auth['OAUTH_TOKEN'], auth['OAUTH_TOKEN_SECRET'])
    threading.Thread(target=twitter_stream).start()

    with Configurator() as config:
        config.add_route('index', '/')
        config.add_view(web_index, route_name='index')

        config.add_route('data', '/data')
        config.add_view(web_data, route_name='data')

        config.add_route('post', '/post')
        config.add_view(web_post, route_name='post')

        config.add_route('static', '/{name}')
        config.add_view(web_static, route_name='static')

        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
