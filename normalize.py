import os
import json
if __name__ == "__main__":
	path = os.getcwd() + os.sep + "userTweets"
	all = os.listdir(path)
	with open("normalized.txt", "w") as f:
		for item in all:
			if os.path.isfile(path + os.sep + item):
				with open(path + os.sep + item, "r") as fin:
					print "processing file: ", item
					data = []
					for line in fin.readlines():
						data.extend(json.loads(line))
					for tweet_data in data:
						f.write(tweet_data.get("text").encode('ascii', 'ignore').strip())
						f.write("\n")