from  bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Slider, HoverTool, Select
from bokeh.plotting import figure
import pandas as pd
from bokeh.layouts import row, widgetbox
from bokeh.models.widgets import Tabs, Panel

df = pd.read_csv('/Users/deeplakkad/Downloads/bokeh/AAPL.csv',
                parse_dates=True, index_col = 'Date')

yr = '2013'
df1 = df.loc[yr]

source = ColumnDataSource(data = {
            'x': df1.index,
            'y': df1.loc[yr].Open
})

#Plotting figure for Opening Price
plot = figure(x_axis_type = 'datetime')
plot.line(x='x', y='y', color = 'blue',source=source)
plot.circle(x='x', y='y', fill_color='white', size=4, alpha=0.4, source=source)

# Define the callback: update_plot
def update_plot(attr, old, new):
    # Read the current value off the slider and 2 dropdowns: yr, x, y
    yr = str(slider.value)
    df2 = df.loc[yr]
    x = df2.index
    y = y_select.value
    # Label axes of plot
    plot.xaxis.axis_label = 'Date'
    plot.yaxis.axis_label = y
    # Set new_data
    new_data = {
        'x'       : x,
        'y'       : df2.loc[yr][y],
    }
    # Assign new_data to source.data
    source.data = new_data

    # Add title to plot
    plot.title.text = 'Stock data for %s' % yr

# Create a dropdown slider widget: slider
slider = Slider(start=2013, end=2018, step=1, value=2013, title='Year')

# Attach the callback to the 'value' property of slider
slider.on_change('value', update_plot)

# Create a dropdown Select widget for the x data: x_select
y_select = Select(
    options=['Close', 'High', 'Open', 'Low'],
    value='Open',
    title='y-axis data'
)

# Attach the update_plot callback to the 'value' property of x_select
y_select.on_change('value', update_plot)


#Creating a HoverTool
hover = HoverTool(tooltips=[('Price', '@y'),
                            ('Date', '@x')])

plot.add_tools(hover)

# Create layout and add to current document
layout = row(widgetbox(slider, y_select), plot)
curdoc().add_root(layout)
