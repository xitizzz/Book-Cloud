import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import os
import base64
from collections import Counter
from wordcloud import WordCloud
from pre_processing import PreProcessing
from io import BytesIO

external_stylesheets = ['https://codepen.io/xitizzz/pen/XWmVjqo.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

books_options = [{"label": b.split(".")[0].replace("_", " "),  "value":b} for b in os.listdir("./books")]

clicks = 0

colors = {
    'background': '#000000',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, 
    children=[
    html.Img(style={
             "max-width": "30%", "height": "auto", "display": "block", "margin-left": "auto", "margin-right": "auto"},
             src=app.get_asset_url('book-cloud.png')),

    html.Div(id='input-div', style={"width": "40%", "margin": "auto", "padding":"20px"},
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
                                                "width": "240px", "float":"left"}),
                html.Button('Generate', id='generate', style={"display": "inline-block",
                            "width": "100px", "float": "right", "text-align":"center", "padding":"auto"})
    ]),

    html.Div(id='wordcloud-div', children=[html.Img(id="wordcloud-img", style={
             "max-width": "80%", "height": "auto", "display": "block", "margin-left": "auto", "margin-right": "auto", "padding-top": "20px"})]),

])


def prepare_text(book):
    text = PreProcessing(f"books/{book}")
    text.chop_gutenberg_metadata()
    text.clean_up_text()
    text.create_unigrams()
    return text


@app.callback(
    Output(component_id='wordcloud-img', component_property='src'),
    [Input(component_id='generate', component_property='n_clicks'),
     Input(component_id='word-count-input', component_property='value'),
     Input(component_id='book-dropdown', component_property='value')]
)
def update_output(n_clicks, word_count, book):
    global clicks
    print(n_clicks, clicks)
    if n_clicks is None or n_clicks==clicks or book is None:
        raise PreventUpdate
    else:
        clicks = n_clicks
        text = prepare_text(book)
        wc = WordCloud(width=1920, height=1080, 
                        max_words=int(100 if word_count is None else word_count))\
                    .fit_words(frequencies=dict(Counter(text.unigrams)))
        img = BytesIO()
        wc.to_image().save(img, format='PNG')
        return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())


if __name__ == '__main__':
    app.run_server(debug=True)
