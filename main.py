
from twython import Twython
from twython import TwythonStreamer
import json
import urllib

with open("settings.json", "r") as read_file:
    settings = json.load(read_file)

with open("auth.json", "r") as read_file:
    auth = json.load(read_file)

photo_list = []

class MyStreamer(TwythonStreamer):
	def on_success(self, data):
		if 'extended_entities' in data and 'media' in data['extended_entities']:
			for i in data['extended_entities']['media']:
				if i['type'] == 'photo':
					print(f"{i['media_url']} https://twitter.com/user/status/{data['id_str']}")
					photo_list.append({'url': i['media_url'], 'id': data['id_str']})
		

	def on_error(self, status_code, data):
		print(status_code, data)



def main():
	# Requires Authentication as of Twitter API v1.1
	stream = MyStreamer(auth['APP_KEY'], auth['APP_SECRET'],
						auth['OAUTH_TOKEN'], auth['OAUTH_TOKEN_SECRET'])

	stream.statuses.filter(track=settings['track'])

if __name__ == "__main__":
	main()