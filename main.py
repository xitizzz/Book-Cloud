from os import listdir
from base64 import b64encode, b64decode
from io import BytesIO

from flask import Flask
from dash import Dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html

from wordcloud import WordCloud
from pre_processing import TextProcessor

DEBUG = False

# Initialization
server = Flask(__name__)
app = Dash(__name__, server=server)
app.title = 'Book Cloud'

books_options = [{"label": b.split(".")[0].replace(
    "_", " "),  "value":b} for b in listdir("./books")]

clicks = None

# HTML Layout
app.layout = html.Div(style={'backgroundColor': '#000000'}, 
    children=[
        html.Div(className="content", style={"min-height": "calc(100vh - 50px)"},
            children=[
                # Set style so that it is hidden!
                html.Div(id="size", style={
                         "position": "fixed", "top": 0, "left": 0} if DEBUG else {"display": "none"}),
                dcc.Location(id="url"),
                html.Img(style={"max-width": "500px", "height": "auto", "display": "block",
                                "margin-left": "auto", "margin-right": "auto"},
                         src=app.get_asset_url('book-cloud.png')),

                html.Div(id='input-div', style={"width": "700px", "margin": "auto", "padding": "10px"},
                         children=[
                    dcc.Dropdown(id='book-dropdown',
                                 style={"background-color": "black", "color": "black",
                                        "display": "block", "width": "100%", "padding-bottom": "10px"},
                                 options=books_options,
                                 placeholder='Select A Book'
                                 ),
                    html.Div(id='upload-div', children=[
                        dcc.Upload(
                            id='upload-text',
                            children=html.Div([
                                html.A('Upload'),
                                ' Your Own Book'

                            ]),
                            style={
                                'width': '100%',
                                'height': '30px',
                                'lineHeight': '30px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin-bottom': '10px'
                            },
                            multiple=False
                        ),
                    ]),
                    html.Div(id="word-count-slider", children=[
                        html.Div(children=["Word Count"], style={"width": "100px",
                                                                 "float": "left",
                                                                 "display": "inline-block",
                                                                 "color": "white"}),
                        dcc.Slider(id='word-count-input',
                                   min=10,
                                   max=200,
                                   step=5,
                                   value=100,
                                   tooltip={'always_visible': True, 'placement': 'topRight'})],
                             style={"width": "250px",
                                    "float": "left", "display": "inline-block"}),
                    html.Button('Generate', id='generate', style={"display": "inline-block",
                                                                  "width": "100px", "float": "right", "text-align": "center", "padding": "auto"})
                ]),

                html.Div(id='wordcloud-div', children=[dcc.Loading(children=[
                    html.Img(id="wordcloud-img", style={
                        "max-width": "80%", "height": "auto", "display": "block",
                        "margin-left": "auto", "margin-right": "auto"})
                ])]),
            ]
        ),
        
        html.Div(children=[html.P("Created with ❤️ and Python")], className="footer",
                    style={"text-align": "center", "height": "50px"
        }
        )
])

# Get screen resolution on client side
app.clientside_callback(
    """
    function(url) {
        return "".concat(window.innerWidth, "x", window.innerHeight);
    }
    """,
    Output('size', 'children'),
    [Input('url', 'href')]
)

# Update Upload Text
@app.callback(
    Output(component_id='upload-text', component_property='children'),
    [Input('upload-text', 'filename'),],
    [State('upload-text', 'last_modified')])
def update_upload(file_name, last_modified):
    if file_name is None:
        return html.Div([
            html.A('Upload'),
            ' Your Own Book'
        ])
    else:
        return html.Div([
            f'{file_name} Uploaded. ',
            html.A('Upload'),
            ' Again.'
            ])


# Reset Upload 
# When a selection is made from drop down uploaded file is cleared
@app.callback(
    Output(component_id='upload-text', component_property='filename'),
    [Input(component_id='book-dropdown', component_property='value'),])
def reset_upload(book):
    return None
    

# Update WordCloud
@app.callback(
    Output(component_id='wordcloud-img', component_property='src'),
    [Input(component_id='generate', component_property='n_clicks'),
     Input(component_id='word-count-input', component_property='value'),
     Input(component_id='book-dropdown', component_property='value'),
     Input('upload-text', 'contents'),
     Input('size', 'children')
     ],
    [State('upload-text', 'filename')])
def update_output(n_clicks, word_count, book, custom_text, size, file_name):
    global clicks
    print("Clicks:", n_clicks, clicks)
    wc_width, wc_height = get_word_cloud_size(size)
    if n_clicks == clicks or (book is None and custom_text is None):
        clicks = n_clicks
        raise PreventUpdate
    else:
        clicks = n_clicks
        if(file_name is not None and custom_text is not None):
            text = prepare_text(custom_text, "base64")
        else:
            text = prepare_text(book)
        wc = WordCloud(width=wc_width, height=wc_height,
                       max_words=int(100 if word_count is None else word_count))\
                        .fit_words(frequencies=text.compute_frequencies())
        img = BytesIO()
        wc.to_image().save(img, format='PNG')
        return 'data:image/png;base64,{}'.format(b64encode(img.getvalue()).decode())

# Clean up text and other stuff
def prepare_text(book, encoding=""):
    if (encoding == "base64"):
        text = TextProcessor(f"books/{book}", "base64")
    else:
        text = TextProcessor(f"books/{book}")
    text.chop_gutenberg_metadata()
    text.clean_up_text()
    text.create_unigrams()
    return text

def get_word_cloud_size(size):
    print(f"Resolution: {size}")
    width, height = int(size.split("x")[0]), int(size.split("x")[-1])
    if height > width:
        return 900, 900
    else:
        return 1200, 700

if __name__ == '__main__':
    app.run_server(debug=DEBUG, port=8080)
