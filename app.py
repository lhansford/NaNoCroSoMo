from datetime import datetime, timedelta
import threading
import logging
import json
import random

import easybigquery

from flask import Flask, render_template, abort, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('config')
db = SQLAlchemy(app)

import models

@app.before_first_request
def initialize():
	#Logging for heroku
	stream_handler = logging.StreamHandler()
	app.logger.addHandler(stream_handler)
	app.logger.setLevel(logging.INFO)
	app.logger.info('nanocrosomo startup')

	get_next_word()

@app.route('/')
def index():
	story = models.Story.query.first()
	paragraphs = story.get_paragraphs()
	print(paragraphs)
	timestamp = datetime.utcnow().strftime("%d-%m-%y-%H-%M-%S-%f")
	return render_template("index.html",
		story=story,
		paragraphs=paragraphs,
		load_timestamp=timestamp
	)

@app.route('/_add', methods=['POST'])
def add_word():
	post_json = request.get_json(force=True)
	print(post_json)
	if not post_json or not 'word' in post_json or not 'paragraph' in post_json or not 'story_id' in post_json:
		abort(400)
	word = post_json['word']
	paragraph = post_json['paragraph']
	story_id = post_json['story_id']
	timestamp = post_json['timestamp']

	# Capitalise word if last word was end of sentence.
	previous_words = models.Word.query.filter_by(story_id=story_id).order_by('created_at').all()
	if(len(previous_words) > 0):
		if previous_words[-1].word[-1] in ['?', '!', '.']:
			word = word.title()
	else:
		word = word.title()

	word = models.Word(
		created_at = datetime.utcnow(),
		word = word,
		end_of_paragraph = paragraph,
		generated = False,
		story_id = story_id
	)
	db.session.add(word)
	db.session.commit()
	return jsonify(get_updated_words(timestamp, story_id)), 201

def get_updated_words(timestamp, story_id):
	timestamp = datetime.strptime(timestamp, "%d-%m-%y-%H-%M-%S-%f")
	new_words = models.Word.query.filter_by(story_id=story_id).filter(timestamp < models.Word.created_at).all()
	print(new_words)

	return {
		'paragraphs':get_paragraphs(new_words),
		'timestamp':datetime.utcnow().strftime("%d-%m-%y-%H-%M-%S-%f")
	}

def get_paragraphs(words):
	paragraphs = []
	curr_p = []
	for word in words:
		curr_p.append(word.get_word())
		if word.end_of_paragraph:
			paragraphs.append(curr_p)
			curr_p = []
	paragraphs.append(curr_p)

	return [ ''.join(p) for p in paragraphs ]

def get_next_word():
	print("Thread run")
	story_id = 1
	words = models.Word.query.filter_by(story_id=story_id).order_by('created_at').all()
	if len(words) == 0:
		time_expired = True
	else:
		time_expired = words[-1].created_at < datetime.utcnow() - timedelta(seconds=30)

	if time_expired:
		if len(words) == 0:
			new_word = "The"
		elif len(words) == 1:
			new_word = singleNgram(words[0].word)
		else:
			new_word = doubleNgram(words[-2].word, words[-1].word)

		print(new_word)
		word = models.Word(
			created_at = datetime.utcnow(),
			word = new_word,
			end_of_paragraph = False,
			generated = True,
			story_id = story_id
		)
		db.session.add(word)
		db.session.commit()

	threading.Timer(31, get_next_word).start()

def singleNgram(word):
	query = "SELECT second, count(second) as second_count FROM publicdata:samples.trigrams WHERE first='%s' GROUP BY second ORDER BY second_count DESC;" % word
	result = makeQuery(query)
	if result['totalRows'] == '0':
		return "."
	return select_word_from_ngrams(result['rows'])

def doubleNgram(word1, word2):
	query = "SELECT third, count(third) as third_count FROM publicdata:samples.trigrams WHERE first='" + word1 + "'and second='" + word2 + "' GROUP BY third ORDER BY third_count DESC;"
	result = makeQuery(query)
	if result['totalRows'] == '0':
		return singleNgram(word2)
	else:
		return select_word_from_ngrams(result['rows'])

def makeQuery(query):
	# Settings
	json_key_file = 'Collections-6474de5ca182.json'

	# Load the private key associated with the Google service account
	with open(json_key_file) as json_file:
		json_data = json.load(json_file)

	API = easybigquery.GoogleAPIFromServiceAccount(511948228668, json_data['client_email'], json_data['private_key'])
	bq = easybigquery.GoogleBigQuery(API)
	result = bq.query(query)
	return result

def select_word_from_ngrams(result):
	sum_results = sum([int(r['f'][1]['v']) for r in result])
	print(sum_results)
	i = random.randint(0, sum_results)
	count = 0
	for r in result:
		if count >= i:
			return r['f'][0]['v']
		count += int(r['f'][1]['v'])

	return "and"



if __name__ == '__main__':
	app.run(debug=True)
