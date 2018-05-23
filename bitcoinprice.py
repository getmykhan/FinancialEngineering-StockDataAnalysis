from bokeh.io import curdoc
from bokeh.plotting import figure
from bs4 import BeautifulSoup
import requests
from bokeh.models import ColumnDataSource


f = figure()

def extract_value():
    headers = headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G928X Build/LMY47X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Mobile Safari/537.36'}
    r = requests.get('https://bitcoincharts.com/markets/bitstampUSD.html', headers=headers)
    c = r.content
    soup = BeautifulSoup(c, "html.parser")
    value_raw = soup.find_all('p')
    value_net = float(value_raw[0].span.text)
    return value_net

source = ColumnDataSource(dict(x=[1], y=[extract_value()]))

f.circle(x='x', y='y', color = 'brown' , line_color='orange', source=source)
f.line(x='x', y='y', source=source)


def update():
    new_data = dict(x=[source.data['x'][-1]+1], y=[extract_value()])
    source.stream(new_data, rollover=200)
    print(source.data)


curdoc().add_root(f)
curdoc().add_periodic_callback(update,10000)
