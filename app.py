import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import base64
from collections import Counter
from wordcloud import WordCloud
from pre_processing import PreProcessing
from io import BytesIO

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, 
    children=[
    html.H1(style={
            'textAlign': 'center',
            'color': colors['text']
            },
            children='Book Cloud'),

    html.Div(style={
        'textAlign': 'center',
        'color': colors['text']
    },
    children='''
        Create Word Clouds For Your Favorite Books
    '''),

    html.Div(id='input-div',
             children=[
                dcc.Input(id='word-count', value='100', type='text'),
                html.Button('Generate', id='generate')
    ]),

    html.Div(id='wordcloud-div', children=[html.Img(id="wordcloud-img")]),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5],
                    'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }
    )
])

def prepare_text():
    text = PreProcessing("books/Communist_Manifesto.txt")
    text.chop_gutenberg_metadata()
    text.clean_up_text()
    text.create_unigrams()
    return text

@app.callback(
    Output(component_id='wordcloud-img', component_property='src'),
    [Input(component_id='generate', component_property='n_clicks')]
)
def update_output(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        text = prepare_text()
        wc = WordCloud(width=1920, height=1080, max_words=100).fit_words(
                        frequencies=dict(Counter(text.unigrams)))
        img = BytesIO()
        wc.to_image().save(img, format='PNG')
        return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

if __name__ == '__main__':
    app.run_server(debug=True)
