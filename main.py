import heapq
import math
import re
import os

global stop_words

def read_stopwords():
	words = []
	with open(os.getcwd() + os.sep + "stopwords.txt", "r") as f:
		for line in f.readlines():
			line = line.strip()
			if len(line):
				words.append(line.lower())
	return words

stop_words=read_stopwords()

def contains_hashtag(tweet):
  val = re.search(r".*(#\w+)",tweet)
  return True if val else False

def process_tweet(tweet, ret_original):
  tweet = re.sub('@[\S]+','',tweet)
  tweet = re.sub('((www\.[\S]+)|(https?://[\S]+))','URL', tweet)
  tweet = tweet.strip('\'"?.,!')
  tweet = re.sub('[-\'"\.\?!\(\)~]', '', tweet)
  tweet = re.sub('[\s]+', ' ', tweet)
  if not contains_hashtag(tweet):
    return tweet if ret_original else "" #empty since this tweet won't make a difference in our result
  return tweet.strip().lower()

def process_tweets(T):
	Ts = []
	for tweet in T:
		x = process_tweet(tweet, False)
		if len(x):
			Ts.append(x)
	return Ts

def retrieve_hashtags(tweet):
	pattern = re.compile(r"#[\w_-]+")
	return [hashtag.lower() for hashtag in pattern.findall(tweet)]

def get_hashtags(T):
	hashtags = []
	for tweet in T:
		hashtags.extend(retrieve_hashtags(tweet))
	return hashtags

def get_hashtag_freq(H):
	hash_freq = {}
	for hashtag in H:
		if hash_freq.has_key(hashtag):
			hash_freq[hashtag] += 1
		else:
			hash_freq[hashtag] = 1
	return hash_freq

def clean_tweet(tweet):
	t = tweet.split()
	t = set(t) - set(stop_words)
	return list(t)

def get_hashtag_to_word_freq(T):
	freq = dict()
	for tweet in T:
		hashtags = set(retrieve_hashtags(tweet))
		tweet = set(clean_tweet(tweet))
		tweet = tweet - hashtags
		for tag in hashtags:
			for word in tweet:
				if freq.has_key(tag):
					freq[tag].update({word: freq[tag].get(word, 0) + 1})
				else:
					freq[tag] = {word: 1}
	return freq

"""
W list of tweets to nb_classify
T dataset of tweets
"""
def nb_classify(W, T, n):
	print "Normalizing dataset. Please wait..."
	Ts = process_tweets(T)
	print "done processing tweets"
	print "retrieving hashtags"
	H = get_hashtags(Ts)
	print "done retrieving hashtags"
	print "retrieving hashtag freq"
	hashtag_freq = get_hashtag_freq(H)
	print "done retrieving hashtag freq"
	print "retrieving hashtag to word freq"
	h_to_w_freq = get_hashtag_to_word_freq(Ts)
	print "done retrieving hashtag to word freq"
	print "Done"
	H = set(H)
	final_classification = dict()
	for tweet in W:
		# print "cleaning tweet", tweet
		c_tweet = list(set(clean_tweet(process_tweet(tweet, True))) - set(retrieve_hashtags(tweet)))
		# print "cleaned tweet is", c_tweet
		classifications = []
		for h in H:
			score = 0
			for w in c_tweet:
				# note here that we are using addition instead of multiplication
				# new_score = 
				# print "score for hashtag", h, "with word", w, "is", new_score
				score += (float(h_to_w_freq.get(h, {}).get(w, 0)) / float(hashtag_freq[h]))
			if score != 0:
				# print "score for hashtag", h, "and tweet", tweet, "is", score
				classifications.append((score, h))
		final_classification[tweet] = heapq.nlargest(n, classifications)
		print "Recommended Hashtags for tweet:", tweet, "are", final_classification[tweet]
	print "done everything"
	return final_classification

def TCoR(w, T, hashtag_list):
	fl = 0
	num_words = 0
	num_hash = 0
	for tweet, hashtag in zip(T, hashtag_list):
		if w in tweet:
			fl+=1
			num_words += len(tweet) - tweet.count(w)
			num_hash += len(hashtag)
	tcor = float(float(float(1/float(num_words/fl)) + float(1/float(num_hash)))/2)
	return tcor


def knn_classify(W, T, K, n):
	print "Normalizing dataset, please wait..."
	Ts = process_tweets(T)
	Tc = []
	hashtaglist = []
	for t in Ts:
		Tc.append(clean_tweet(t))
		hashtaglist.append(retrieve_hashtags(t))

	print "Done Normalizing dataset"

	final_classification = dict()
	for tweet in W:
		neighbors = []
		c_tweet = list(set(clean_tweet(process_tweet(tweet, True))) - set(retrieve_hashtags(tweet)))
		for t, orig_tweet in zip(Tc, Ts):
			score = 0
			for w in c_tweet:
				if w in t:
					score += TCoR(w, Tc, hashtaglist)
			# print "score is", score
			neighbors.append((score, orig_tweet))
		nearest_neighbors = heapq.nlargest(K, neighbors) #Get K tweets with highest score
		# print "*"*10
		# print "nearest ", nearest_neighbors
		# print "*"*10
		classifications = [] #Map of hashtag and count
		classification_map = dict()
		for __, t in nearest_neighbors:
			for h in retrieve_hashtags(t):
				classification_map.update({h: classification_map.get(h, 0) + 1}) #Add h with count of 1 (or increment count)
		for key, val in classification_map.iteritems():
			classifications.append((val, key))
		final_classification[tweet] = heapq.nlargest(n, classifications) #Return n hashtags with highest count
		print "Recommended Hashtags for tweet:", tweet, "are", final_classification[tweet]
	print "done everything"
	return final_classification


def read_tweets(file_name):
	tweets = []
	with open(os.getcwd() + os.sep + file_name, "r") as f:
		tweets.extend(f.readlines())
	return tweets

if __name__ == "__main__":
	
	dataset_file = raw_input("Enter name of the dataset file: ")
	input_file = raw_input("Enter name of input file: ")
	choice = input("Choose the Classifier to use\n1. Naive Bayes Classifier\n2. K Nearest Neighbor Classifier\nChoice: ")
	print "Reading Tweets. Wait..."
	T = read_tweets(dataset_file)
	print "Done"
	result = None
	if choice == 1:
		result = nb_classify(read_tweets(input_file), T, 10)
	else:
		result = knn_classify(read_tweets("input"), T, 10, 10)
	if result:
		total_recommended = 0
		length = len(result)
		for key, val in result:
			actual_hashtags = set(retrieve_hashtags(key))
			if len(actual_hashtags):
				recommended_hashtags = set(val(1))
				total_recommended += 1 if len(actual_hashtags & recommended_hashtags) else 0
			else:
				length -= 1
		print "Accuracy is", (float(total_recommended)/float(length))
	# print "done"
	# from pprint import pprint
	# pprint(classi)
	# print len([x for x in classi.values() if len(x)])
	# import pdb
	# pdb.set_trace()