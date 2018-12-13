import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.tools as tools
from dash.dependencies import Input, Output, State
from dateutil.parser import parse
import squarify
import math
from datetime import datetime
from bisect import bisect_left
import grasia_dash_components as gdc

####################################################
### 			DASH SETUP CODE					 ###
####################################################

# Setup Dash's default CSS stylesheet
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Setup the Dash application
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets, static_folder='static')
app = dash.Dash(__name__, static_folder='static')


####################################################
### 		DESCENTRALIZED  CODE				 ###
####################################################

tm_width = 100
tm_height = 100
tm_x = 0
tm_y = 0

# color pallette for the viz
cList = ['lightcyan', 'lightblue', 'deepskyblue', 'dodgerblue', 'steelblue',
         'midnightblue']

table = [['Name', 'Estimated Balance'],
         ['Planktons', '0 to 1 Bitcoin'],
         ['Clowfishes', '1 to 10 Bitcoins'],
         ['Lionfishes', '10 to 100 Bitcoins'],
         ['Swordfishes', '100 to 1000 Bitcoins'],
         ['Sharks', '1000 to 10000 Bitcoins'],
         ['Whales', 'More than 10000 Bitcoins']]

df_table = pd.DataFrame(table)
df_table.columns = df_table.iloc[0]
df_table = df_table[1:]

df_val_per_month = pd.read_csv('change_bins_values_per_month.csv')
df_val_per_month.fillna(0, inplace=True)
df_val_per_month.loc[:,"_0_to_1":"More_10000"] = df_val_per_month.loc[:,"_0_to_1":"More_10000"].div(df_val_per_month.sum(axis=1), axis=0) * 100
df_val_per_month.columns = ["Month", "Planktons", "Clownfishes",
                            "Lionfishes", "Swordfishes", "Sharks", "Whales"]
df_val_per_month = df_val_per_month.sort_values(by='Month')
df_val_per_month.Month = pd.to_datetime(df_val_per_month.Month)
df_val_per_month = df_val_per_month.set_index(['Month'])

df_ct_per_month = pd.read_csv('change_count_bins_per_month.csv')
df_ct_per_month.fillna(0, inplace=True)
df_ct_per_month.loc[:,"_0_to_1":"More_10000"] = df_ct_per_month.loc[:,"_0_to_1":"More_10000"].div(df_ct_per_month.sum(axis=1), axis=0) * 100
df_ct_per_month.columns = ["Month", "Planktons", "Clownfishes",
                            "Lionfishes", "Swordfishes", "Sharks", "Whales"]
df_ct_per_month = df_ct_per_month.sort_values(by='Month')
df_ct_per_month.Month = pd.to_datetime(df_ct_per_month.Month)
df_ct_per_month = df_ct_per_month.set_index(['Month'])

epoch = datetime.utcfromtimestamp(0)


def unix_time_millis(dt):
    return (dt - epoch).total_seconds()

def timestamp_millis(unix_ts):
    ts = datetime.utcfromtimestamp(unix_ts).strftime('%Y-%m-%d')
    return pd.to_datetime(ts)


def build_treemap(date, dataset, x, y, width, height):

    shapes = []
    counter = 0
    annotations = []

    month = timestamp_millis(date)

    if dataset == 'values':
        values = df_val_per_month.loc[month]
    else:
        values = df_ct_per_month.loc[month]

    cValues = [x + 0.0000001 for x in values]
    normed = squarify.normalize_sizes(cValues, width, height)
    rects = squarify.squarify(normed, x, y, width, height)

    for r in rects:
        shapes.append(
            dict(
                type='rect',
                x0=r['x'],
                y0=r['y'],
                x1=r['x']+r['dx'],
                y1=r['y']+r['dy'],
                line={'width':2,
                      'color':'#fff'},
                fillcolor=cList[counter]
            ),
        )

        counter = counter + 1
        if counter >= len(cList):
            counter = 0

    figure = {
        'data': [go.Scatter(
            x=[r['x']+(r['dx']/2) for r in rects],
            y=[r['y']+(r['dy']/2) for r in rects],
            text=[v + '\n' + '{:.2f}'.format(values.get(v)) + '%' for v in values.keys()],
            mode='text',
            hoverinfo='text',
            )
        ],

        'layout': go.Layout(
            height=500,
            width=500,
            xaxis={'showgrid': False,
                   'zeroline': False,
                   'showticklabels': False,
                   'ticks':''},
            yaxis={'showgrid': False,
                   'zeroline': False,
                   'showticklabels': False,
                   'ticks':''},
            shapes=shapes,

            hovermode='closest',
            hoverdistance=200,
        )
    }

    return figure

descetralizedStory = html.Div([

html.Div([
    html.H2(children='Are Bitcoins Decentralized?'),
    dcc.Markdown('Analyzing transaction data from [January 2009 to september 2018](https://cloud.google.com/blog/products/gcp/bitcoin-in-bigquery-blockchain-analytics-on-public-data).')
], className='row'),

html.Div([
    html.Div([
    dcc.Markdown('''
Bitcoins were supposed to be centralized, therefore not controlled by governments
or companies. However, the early distribution was [concentrated on a few early
adopters](https://blog.picks.co/bitcoins-distribution-was-fair-e2ef7bbbc892/)
and nowadays specialist suspects that trader companies have the wealthier
accounts.

The problem can be even worse, because most of the wealthier users hold more
than one account, improving his/her privacy at the same time that undermines the
coin distribution transparency. For the 22 million unique wallets, the estimative
is about roughly [5 million unique users](https://medium.com/@BambouClub/are-you-in-the-bitcoin-1-a-new-model-of-the-distribution-of-bitcoin-wealth-6adb0d4a6a95).

The upcoming boxes show the distribution of the users and the overall amount of
transactions over time. Use the slider in the bottom of the page to shift the
time window and hover over the boxes to see the distribution.\n

    '''),
        ], className='eight columns', style= {}),

    html.Div([
        html.Div([
            html.Img(id='wallet_count_viz', src='/assets/wallets_count.svg'),
        ]),
    ], className='four columns'),

], className='row'),
])

descetralizedviz = html.Div([

html.Div([
    html.H2(children='Are Bitcoins Decentralized?'),
], className='row'),



html.Div([
    html.Div([], className='two columns'),
    html.Div([
        html.Div([
                dcc.Graph(
                    id='cpm_treemap',
                    figure=build_treemap(unix_time_millis(df_ct_per_month.index[-1]),
                                         'count', tm_x, tm_y, tm_width, tm_height),
                    config={
                        'displayModeBar': False
                    }
                )
        ]),
    ], className='five columns'),
    html.Div([
        html.Div([
            dcc.Graph(
                id='vpm_treemap',
                figure=build_treemap(unix_time_millis(df_val_per_month.index[-1]),
                                     'values', tm_x, tm_y, tm_width, tm_height),
                config={
                    'displayModeBar': False
                }
            )
        ], style = {'width': '100%', 'display': 'block'}),
    ], className='five columns'),
],className='row'),

html.Div([
    html.Div([], className='one columns'),
    html.Div([
        dcc.Slider(
            id='date_slider',
            min=unix_time_millis(df_ct_per_month.index.min()),
            max=unix_time_millis(df_ct_per_month.index.max()),
            value=unix_time_millis(df_ct_per_month.index.max()),
            marks={int(unix_time_millis(d)): {'label': d.strftime('%B %Y'),
                                              'style': {  'transform': 'rotate(-45deg) translate(-45px, -10px)',
                                                        'text-align': 'right',
                                                        'white-space': 'nowrap'}} for d in df_ct_per_month.index[0:len(df_ct_per_month):5]},
            included=True,
            updatemode='mouseup'
        )
    ], className='ten columns'),
], className='row', style= {'width': '90%', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),


])

####################################################
### 			STORE VALUE VIZ CODE			 ###
####################################################

df_storevalue = pd.read_csv('crypto10-markets-am.csv')

storevalueviz = html.Div(children = [
    html.H1(children='How volatile are crypto prices?'),


    html.Div(children='''
        % Change in Prices by Day for Top 10 Cryptocurrencies by Market Cap (2013-2018)

        Hover over the data points to see more details.
        You can click on the currency names on the legends to add/eliminate them from the graph.
    '''),

    # graph 1
    dcc.Graph(
        id='change',
        config = {
            'displaylogo': False
        },
        figure={'data': [go.Scatter(
            x = df_storevalue[df_storevalue['name'] == i].date,
            y = df_storevalue[df_storevalue['name'] == i]['change%'],
            name=i
        )
        for i in df_storevalue.name.unique()],


                'layout': go.Layout(
				paper_bgcolor='#f7f9fb',
		    	plot_bgcolor='#f7f9fb',
                xaxis={'type': 'date', 'title': 'Date'},
                yaxis={'type': 'linear', 'title': '% Change in Day', 'tickformat': ',.000001%'},
                margin={'l': 100, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest')

        }
    )
])

####################################################
### 		FAST AND CHEAP VIZ CODE				 ###
####################################################

df_fees = pd.read_csv('avg_transaction_fee.csv')
df_times = pd.read_csv('block_times.csv')
df_fees['date'] = pd.to_datetime(df_fees['date'],format='%Y/%m/%d')
df_times['date'] = pd.to_datetime(df_times['date'],format='%Y/%m/%d')

min_date = min(df_fees.min()['date'],df_times.min()['date'])
max_date = max(df_fees.max()['date'],df_times.max()['date'])

cryptos = {'btc':{'color':'#e41a1c'},
           'eth':{'color':'#377eb8'},
           'bch':{'color':'#4daf4a'},
           'ltc':{'color':'#984ea3'},
           'xmr':{'color':'#ff7f00'},
           'dash':{'color':'#ffff33'},
           'zec':{'color':'#a65628'}}

def build_plots(height=600,width=1400,initial_date=None,end_date=None,zoom=False):
    traces = []
    if (initial_date is not None) and (end_date is not None):
        if (zoom):
            df_times_series = df_times[((df_times['date'] >= initial_date) & (df_times['date'] <= end_date))]
            df_fees_series = df_fees[((df_fees['date'] >= initial_date) & (df_fees['date'] <= end_date))]
        else:
            df_times_series = df_times
            df_fees_series = df_fees
        df_times_plot = df_times[((df_times['date'] >= initial_date) & (df_times['date'] <= end_date))]
        df_fees_plot = df_fees[((df_fees['date'] >= initial_date) & (df_fees['date'] <= end_date))]
    else:
        df_times_series = df_times
        df_fees_series = df_fees
        df_times_plot = df_times
        df_fees_plot = df_fees

    max_fee = 0
    max_time = 0
    for i in cryptos:
        mean_time = df_times_plot[i].mean()
        mean_fee = df_fees_plot[i].mean()
        if mean_time > max_time:
            max_time = mean_time
        if mean_fee > max_fee:
            max_fee = mean_fee
        traces.append(go.Scatter({'x':df_times_series['date'],
                             'y':df_times_series[i],
                             #'text':i.upper(),
                             'name':i.upper(),
                             'legendgroup':i.upper(),
                             'xaxis':'x1',
                             'yaxis':'y3',
                             'line':{'color':cryptos[i]['color']},
                             'showlegend':False}))
        traces.append(go.Scatter({'x':[mean_time],
                             'y':[mean_fee],
                             #'text':i.upper(),
                             'name':i.upper(),
                             'legendgroup':i.upper(),
                             'mode':'markers',
                             'opacity':1.0,
                             'marker':{'size':15,'color':cryptos[i]['color'],'line':{'width':0.5,'color':'black'}},
                             'xaxis':'x2',
                             'yaxis':'y2'}))
        traces.append(go.Scatter({'x':df_fees_series['date'],
                             'y':df_fees_series[i],
                             #'text':i.upper(),
                             'name':i.upper(),
                             'legendgroup':i.upper(),
                             'xaxis':'x1',
                             'yaxis':'y1',
                             'line':{'color':cryptos[i]['color']},
                             'showlegend':False}))

    range_y2 = max_fee*1.1
    range_x2 = max_time*1.1

    layout = go.Layout(
        #width=width,
        #height=height,
		autosize=True,
		margin=go.layout.Margin(
	        l=50,
	        r=10,
	        b=40,
	        t=20,
	        pad=4
    	),
        hovermode='closest',
        xaxis=dict(
            domain=[0, 0.45],
            anchor='y1',
            title='Date'
        ),
        yaxis=dict(
            domain=[0, 0.45],
            anchor='x1',
            title='Avg. Transaction Fees (USD)'
        ),
        xaxis2=dict(
            domain=[0.55, 1],
            range=[0,range_x2],
            anchor='y2',
            title='Average Block Times in Minutes'
        ),
        yaxis2=dict(
            domain=[0, 1],
            range=[0,range_y2],
            anchor='x2',
            title='Average Transaction Fees in USD'
        ),
        yaxis3=dict(
            domain=[0.55, 1],
            anchor='x1',
            title='Avg. Block Times (min)'
        ),
        images= [dict(
                  source= "/assets/fastcheap_back.png",
                  xref= "x2",
                  yref= "y2",
                  yanchor="bottom",
                  x= 0,
                  y= 0,
                  sizex=range_x2,
                  sizey=range_y2,
                  sizing= "fill",
                  opacity= 0.7,
                  layer= "below")],
		paper_bgcolor='#f7f9fb',
    	plot_bgcolor='#f7f9fb'
    )

    return go.Figure(data=traces,layout=layout)

initial_figure = build_plots()

fastcheapviz = html.Div([dcc.Markdown('''
#### Bitcoin Booms and Busts: Fast and Cheap Transactions Visualization

The visualization below displays data on the premise of cryptocurrencies being able to perform fast and cheap transactions. On the left side,
you can visualize time series on historical data for block times (the amount of time it takes for a transaction to show up on a block, thus
being confirmed) and the fee charged for that transaction. On the right side, you can view a scatterplot where the positioning of each
cryptocurrency is relative to the historical performance of that currency in both time and cost.
'''),
        # html.Div([dcc.DatePickerRange(
        #             id='date_range_picker',
        #             display_format='MMM Do, YYYY',
        #             min_date_allowed=min_date,
        #             max_date_allowed=max_date,
        #             initial_visible_month=max_date,
        #             start_date=min_date,
        #             end_date=max_date
        #         ),
        #         dcc.Graph(
        #             id='fastandcheap',
        #             figure=initial_figure,
        #             config={
        #                 'displayModeBar': False
        #             }
        #         ),
		# 		dcc.Input(
		# 			id='date',
		# 			type='date',
		# 			min=min_date,
		# 			max=max_date,
		# 			value=min_date
		# 		)])
		html.Div([html.Ul(className='flexblock',children=[
					html.Li([
						html.H6('Start Date'),
						dcc.Input(
		                    id='start_date_input',
							type='date',
		                    min=min_date,
		                    max=max_date,
							value=min_date
	                	)
					]),
					html.Li([
						html.H6('End Date'),
						dcc.Input(
				            id='end_date_input',
							type='date',
				            min=min_date,
				            max=max_date,
							value=max_date
			        	)
					])]
				),
                dcc.Graph(
                    id='fastandcheap',
                    figure=initial_figure,
                    config={
                        'displayModeBar': False
                    }
                )
			])
    ]
)

####################################################
### 			SLIDES NAVIGATION BAR			 ###
####################################################

# Defines the Navigation Bar to placed in specific slides
navbar = html.Header([
			html.Nav(role='navigation', className='navbar',children=[
				html.Ul([
						html.Li([html.A('Home',href='#slide=1')]),
						html.Li([html.A('Instructions',href='#slide-2')]),
						html.Li([html.A('Story',href='')]),
						html.Li([html.A('Store Value',href='')]),
						html.Li([html.A('Decentralization',href='')]),
						html.Li([html.A('Fast and Cheap',href='')])
				],style={'margin':0})
			])
		])

####################################################
### 				SLIDES CODE					 ###
####################################################

# This sets up the code for the slides

slides = []

## SLIDE 1: Title Slide`
slide1 = html.Section([
				html.Img(src='/static/bitcoin_logo.svg',width='10%',height='10%',className='aligncenter'),
				html.H1(html.Strong('Bitcoin Booms and Busts')),
				html.Hr(),
				html.H5('University of California, Berkeley'),
				html.H5('Master of Information and Data Science'),
				html.H5('W209 - Data Visualization'),
				html.Hr(),
				html.H6('Arnobio Morelix'),
				html.H6('Felipe Campos'),
				html.H6('Marcelo Queiroz')],
		  className='bg-apple aligncenter')

## SLIDE 2: Introduction Slide
slide2 = html.Section([navbar,
				html.Div(className='wrap',children=[
					html.H2('Instructions'),
					html.P('How to use and navigate this website',className='text-subtitle'),
					html.Hr(),
					html.Div(className='grid vertical-align',children=[
						html.Div(className='column',children=[
							html.H3('Story Mode'),
							html.P('To view the story, just keep scrolling! You can return to the beginning of the story by using the navigation bar above.')
						]),
						html.Div(className='column',children=[
							html.H3('Visualizations'),
							html.P('You can jump directly to the specific visualizations you are insterested in at any time using the navigation bar.')
						]),
						html.Div(className='column',children=[
							html.H3('Interact!'),
							html.P('You can interact with all visualizations. Drag on them to zoom in, double-click to zoom-out. Hover over points for more details. Click on items in the legend to make them disappear, or double-click to single them out!')
						])
					])
				])
			])

## SLIDE 3: Store value
slide3 = html.Section([navbar,storevalueviz])

## SLIDE 4: Fast and cheap
slide4 = html.Section([navbar,fastcheapviz])

slides.append(slide1)
slides.append(slide2)
slides.append(slide3)
slides.append(slide4)

####################################################
### 				DASH LAYOUT					 ###
####################################################

# Set the Dash layout using the slides designed above
app.layout = html.Div([html.Main(role='main',children=[
					   		html.Article(slides,id="webslides",className='vertical')]),
					   gdc.Import(src="/static/renderWebSlides.js")])

####################################################
### 			VISUALIZATION CALLBACKS			 ###
####################################################

################################
##  Descentralized Callbacks  ##
################################

@app.callback(
     dash.dependencies.Output('vpm_treemap', 'figure'),
     [dash.dependencies.Input('date_slider', 'value')])
def update_vpm_treemap(date):
    pos = bisect_left(unix_time_millis(df_val_per_month.index), date)
    if pos == 0:
        return build_treemap(unix_time_millis(df_val_per_month.index[0]),
                             'values', tm_x, tm_y, tm_width, tm_height)
    if pos == len(df_val_per_month.index):
        return build_treemap(unix_time_millis(df_val_per_month.index[-1]),
                             'values', tm_x, tm_y, tm_width, tm_height)
    before = unix_time_millis(df_val_per_month.index[pos - 1])
    after = unix_time_millis(df_val_per_month.index[pos])
    if after - date < date - before:
        return build_treemap(after,'values', tm_x, tm_y, tm_width, tm_height)
    else:
        return build_treemap(before,'values', tm_x, tm_y, tm_width, tm_height)


@app.callback(
     dash.dependencies.Output('cpm_treemap', 'figure'),
     [dash.dependencies.Input('date_slider', 'value')])
def update_vpm_treemap(date):
    cDate = timestamp_millis(date)
    pos = bisect_left(df_ct_per_month.index, cDate)
    if pos == 0:
        return build_treemap(df_ct_per_month.index[0],
                             'count', tm_x, tm_y, tm_width, tm_height)
    if pos == len(df_ct_per_month.index):
        return build_treemap(df_ct_per_month.index[-1],
                             'count', tm_x, tm_y, tm_width, tm_height)
    before = df_ct_per_month.index[pos - 1]
    after = df_ct_per_month.index[pos]
    if after - cDate < cDate - before:
        return build_treemap(unix_time_millis(after),'count', tm_x,
                             tm_y, tm_width, tm_height)
    else:
        return build_treemap(unix_time_millis(before),'count', tm_x,
                             tm_y, tm_width, tm_height)


################################
## Fast and Cheap Callbacks
################################

@app.callback(
    Output('fastandcheap', 'figure'),
    [Input('start_date_input', 'value'),
     Input('end_date_input', 'value')])
def display_selected_data(start_date,end_date):
	if (start_date == ''):
		start_date = min_date
	else:
		start_date = parse(start_date).date()
	if (end_date == ''):
		end_date = max_date
	else:
		end_date = parse(end_date).date()
	if ((start_date == str(min_date.date())) and (end_date == str(max_date.date()))):
		return initial_figure
	else:
		return build_plots(initial_date=start_date,end_date=end_date,zoom=True)

@app.callback(
    Output('start_date_input', 'value'),
    [Input('fastandcheap', 'relayoutData')])
def zoom_to_start_date(relayoutData):
    if (relayoutData is None):
        return min_date
    if ('xaxis.range[0]' in relayoutData):
        initial_date = parse(relayoutData['xaxis.range[0]'])
        return initial_date.date()
    else:
        return min_date

@app.callback(
    Output('end_date_input', 'value'),
    [Input('fastandcheap', 'relayoutData')])
def zoom_to_end_date(relayoutData):
    if (relayoutData is None):
        return max_date
    if ('xaxis.range[1]' in relayoutData):
        end_date = parse(relayoutData['xaxis.range[1]'])
        return end_date.date()
    else:
        return max_date


####################################################
### 			DASH INITIALIZATION				 ###
####################################################

# Fire up the Dash Server
if __name__ == '__main__':
    app.run_server(debug=True)