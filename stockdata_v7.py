## Build: Passing

from flask import Flask, request, redirect, url_for, send_from_directory,render_template, send_file
from flask_table import Table, Col
from nltk.corpus import stopwords
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import re
import pandas as pd
from collections import Counter
import operator
import pygal
import pandas_datareader.data as web
import datetime
from pygal.style import RedBlueStyle
import wikipedia
import random
import time
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import preprocessor as p


app = Flask(__name__)

def top3(TCKER):
	"""
	Function to random generate top five or so tickers to view next
	"""

	## Maniupulate the list below with tickers of choice
	#====================================================
	pool_of_tickers = ['AMZN', 
	'AAPL', 
	'GOOGL',
	'FB',
	'INTC',
	'MU',
	'CSCO']
	#======================================================
	
	top3_list = []
	while len(top3_list) <= 2:
		choice = random.choice(pool_of_tickers)
		if choice == TCKER:
			print(choice)
			time.sleep(5)
			continue
		else:
			if choice not in top3_list:
				top3_list.append(choice)
				print(choice)

	return (top3_list)



## Twitter Scrapping
def twitterscrape(what_in, company_what_in):
	access_token = "3226Zv36xcefpk"
	access_token_secret = 'SNgxaPUsnwONJeMcn'
	consumer_key = "BfetCrIN"
	consumer_secret = "ysbxdg6TDF7TksSRy9G0J3S"

	tweets_scraped_list = []

	fopen = open('tweets1.txt', 'w', encoding='UTF-8')
	class listener(StreamListener):
		time = 20
		def on_data(self, data):
		    print(listener.time)
		    if listener.time != 0:
		        listener.time -= 1 
		        try:
		            all_data = json.loads(data)
		            tweet = all_data["text"]
		            fopen.write(str(tweet))
		            print(tweet)
		            tweets_scraped_list.append(tweet)
		        except:
		            pass
		        return True
		    else:
		        return False


		def on_error(self, status):
			print(status)

	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	twitterStream = Stream(auth, listener())
	twitterStream.filter(track = [what_in, company_what_in,'stock','stocktrader','nasdaq', 'etrade', 'stockexchange'])
	return tweets_scraped_list


#removing stop words and numbers 

def complete_clean(cleaned_content):

	# keep only words
	letters_only_text = re.sub("[^a-zA-Z]", " ", cleaned_content)

	# convert to lower case and split 
	words = letters_only_text.lower().split()

	# remove stopwords
	stopword_set = set(stopwords.words("english"))
	meaningful_words = [w for w in words if w not in stopword_set]

	# join the cleaned words in a list
	cleaned_word_list = " ".join(meaningful_words)

	return cleaned_word_list


@app.route('/', methods= ['POST', 'GET'])
def index():
	""" Drop down option to select to and from year to stream line """
	drop_down_year_from = list(reversed(range(2000, datetime.datetime.now().year + 1)))
	drop_down_month_from = ['01', '02', '03', '04', '05', '06', '07', '08', '09','10','11','12']	

	drop_down_year_to = list(reversed(range(2000, datetime.datetime.now().year + 1)))
	drop_down_month_to = ['01', '02', '03', '04', '05', '06', '07', '08', '09','10','11','12']
	
	if request.method == 'POST':
		try:
			symbol = request.form['Tcker'].strip().upper()
			print(symbol)
			#symbol = 'WIKI/AAPL'  # or 'AAPL.US'
			print(datetime.datetime.now())

			## Datetime now
			year_selected_from = request.form['drop_down_year_from']
			month_selected_from = request.form['drop_down_month_from']

			full_date_from = '{}-{}-01'.format(year_selected_from, month_selected_from)
			print(full_date_from)

			year_selected_to = request.form['drop_down_year_to']
			month_selected_to = request.form['drop_down_month_to']

			print(year_selected_to)
			full_date_to = '{}-{}-01'.format(year_selected_to, month_selected_to)
			print(full_date_to)

			df = web.DataReader(symbol, 'morningstar', full_date_from, full_date_to)
			#df = web.DataReader(symbol, 'morningstar', '2018-01-01', datetime.datetime.now())
			#print(df.head())

			df.sort_index(inplace = True)
			print(df['Open'])
			print(df.index)


			days_in_between = np.abs((pd.to_datetime(full_date_from) - pd.to_datetime(full_date_to)).days)

			print("The days in between are: {}".format(days_in_between))
			line_chart = pygal.Line(x_label_rotation=0, show_y_guides=False, height= 700, width = 1000)

			if days_in_between < 90:
				line_chart.x_labels = range(len(df.index))
				#line_chart.x_labels = df.index
			#['Close', 'High', 'Low', 'Open', 'Volume']
			line_chart.add("Open", df['Open'])
			line_chart.add("Close", df['Close'])
			line_chart.add("High", df['High'])
			line_chart.add("Low", df['Low'])
			#line_chart.add("Volume", df['Volume'])
			lcdata = line_chart.render_data_uri()
			#lctable = line_chart.render_table()

			# Dictionary to hold the values
			stock_d = {}
			stock_d['Open'] = df['Open'].head(20).values
			stock_d['Close'] = df['Close'].head(20).values
			stock_d['High'] = df['High'].head(20).values
			stock_d['Low'] = df['Low'].head(20).values

			print(20 * '=')
			print(stock_d)
			print(20 * '=')

			sample = zip(df['Open'].head(10), df['Close'].head(10),
			 			df['High'].head(10), df['Low'].head(10))
			print (sample)

			print(20 * '=')
			print(20 * '=')
			##############################################################


			## Company name is captured
			try:
				comp = pd.read_csv('companylist.csv')

				print(comp.head(5))
				company_name = comp[comp['Symbol'] == symbol.upper()].iloc[0,1]
				print("The company name is: {}".format(company_name))
				company_summary = wikipedia.summary(company_name)

				top = top3(symbol)
				print(top)
				thatlist = twitterscrape(symbol, company_name)
				print("The contents in the list {}".format(thatlist))

				#print(wikipedia.summary(company_name))

				return render_template('plot.html', lcdata=lcdata, symbol = symbol,
			 						open = df['Open'][:10], close = df['Close'][:10], stock_d = stock_d,
			 						sample = sample, top = top, drop_down_month_from = drop_down_month_from,
			 						drop_down_year_from = drop_down_year_from,
			 						drop_down_month_to=drop_down_month_to, drop_down_year_to=drop_down_year_to,
			 						company_summary=company_summary, thatlist = thatlist)
			except:
				return render_template('plot.html', lcdata=lcdata, symbol = symbol,
			 						open = df['Open'][:10], close = df['Close'][:10], stock_d = stock_d,
			 						sample = sample, top = top, drop_down_month_from = drop_down_month_from,
			 						drop_down_year_from = drop_down_year_from,
			 						drop_down_month_to=drop_down_month_to, drop_down_year_to=drop_down_year_to)

		except:
			return render_template('error.html')

	return render_template('index.html', drop_down_month_from = drop_down_month_from,
			 						drop_down_year_from = drop_down_year_from,
			 						drop_down_month_to=drop_down_month_to, 
			 						drop_down_year_to=drop_down_year_to)


@app.errorhandler(404)
def page_not_found(e):
    return (render_template('error.html'), 404)



if __name__ == '__main__':
	app.run(debug=True)