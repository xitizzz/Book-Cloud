from os import listdir
from base64 import b64encode
from io import BytesIO

from flask import Flask
from dash import Dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html

from wordcloud import WordCloud
from pre_processing import TextProcessor


# Initialization
server = Flask(__name__)
app = Dash(__name__, server=server)
app.title = 'Book Cloud'

books_options = [{"label": b.split(".")[0].replace(
    "_", " "),  "value":b} for b in listdir("./books")]

clicks = 0

# HTML Layout
app.layout = html.Div(style={'backgroundColor': '#000000'},
                      children=[
    html.Img(style={
             "max-width": "30%", "height": "auto", "display": "block", "margin-left": "auto", "margin-right": "auto"},
             src=app.get_asset_url('book-cloud.png')),

    html.Div(id='input-div', style={"width": "40%", "margin": "auto", "padding": "20px"},
             children=[
                 dcc.Dropdown(
                     id='book-dropdown',
                     style={"background-color": "black", "color": "black",
                            "display": "block", "width": "100%", "padding-bottom": "20px"},
                     options=books_options,
                     placeholder='Select A Book'
                 ),
                dcc.Input(id='word-count-input', placeholder='Number of words (default 100)',
                          type='number', style={"background-color": "black", "color": "white",
                                                "width": "240px", "float": "left"}),
                html.Button('Generate', id='generate', style={"display": "inline-block",
                                                              "width": "100px", "float": "right", "text-align": "center", "padding": "auto"})
    ]),

    html.Div(id='wordcloud-div', children=[dcc.Loading(children=[
        html.Img(id="wordcloud-img", style={
             "max-width": "80%", "height": "auto", "display": "block", 
             "margin-left": "auto", "margin-right": "auto", "padding-top": "20px"})
    ])]),
])

# Clean up text and other stuff


def prepare_text(book):
    text = TextProcessor(f"books/{book}")
    text.chop_gutenberg_metadata()
    text.clean_up_text()
    text.create_unigrams()
    return text

# Update WordCloud


@app.callback(
    Output(component_id='wordcloud-img', component_property='src'),
    [Input(component_id='generate', component_property='n_clicks'),
     Input(component_id='word-count-input', component_property='value'),
     Input(component_id='book-dropdown', component_property='value')])
def update_output(n_clicks, word_count, book):
    global clicks
    print(n_clicks, clicks)
    if n_clicks is None or n_clicks == clicks or book is None:
        raise PreventUpdate
    else:
        clicks = n_clicks
        text = prepare_text(book)
        wc = WordCloud(width=1200, height=700,
                       max_words=int(100 if word_count is None else word_count))\
            .fit_words(frequencies=text.compute_frequencies())
        img = BytesIO()
        wc.to_image().save(img, format='PNG')
        return 'data:image/png;base64,{}'.format(b64encode(img.getvalue()).decode())


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
