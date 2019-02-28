
from twython import Twython
from twython import TwythonStreamer
import json

with open("auth.json", "r") as read_file:
    auth = json.load(read_file)

class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            print(data['text'].encode('utf-8'))
        # Want to disconnect after the first result?
        # self.disconnect()

    def on_error(self, status_code, data):
        print(status_code, data)



def main():
	# Requires Authentication as of Twitter API v1.1
	stream = MyStreamer(auth['APP_KEY'], auth['APP_SECRET'],
						auth['OAUTH_TOKEN'], auth['OAUTH_TOKEN_SECRET'])

	stream.statuses.filter(track='twitter')
	# stream.user()
	# Read the authenticated users home timeline
	# (what they see on Twitter) in real-time
	# stream.site(follow='twitter')

if __name__ == "__main__":
	main()