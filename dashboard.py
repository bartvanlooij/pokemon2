import time
import difflib
import pandas as pd
import numpy
import json
import ast
import pygetwindow as gw
from PIL import Image, ImageOps
from calibration import calibration, find_name_box
from main import check_for_battle, print_moves, print_typing
from compare_images import *
from battle_detection import *
import pytesseract
from print_pokemon_data import get_pokemon_data
from dash import Dash, dcc, html, Input, Output, State, dash_table
from io import BytesIO
import base64
import plotly.graph_objects as go
import itertools

df_pokemon = pd.read_csv('pokemon.csv')
df_pokemon['evolution'] = df_pokemon['evolution'].apply(ast.literal_eval)
df_typing = pd.read_csv('newtyping.csv', index_col=0)
with open("pokemon_moves.json", 'r') as filehandle:
    moves = json.load(filehandle)

battle_format = Image.open("test_fotos/battle_format.png")
battle_format = ImageOps.grayscale(battle_format)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
print_order = ["Name", "Type 1", "Type 2", "HP", "Attack",
               "Defense", "Sp. Atk", "Sp. Def", "Speed", "Total"]


class Window():

    def __init__(self, window_name: str, top_coords: tuple[int], bot_coords: tuple[int], box_coords: tuple[int]):
        self.window_name = window_name
        self.top_coords = top_coords
        self.bot_coords = bot_coords
        self.box_coords = box_coords
        self.pokemon_name = " "
        self.print_order = ["Name", "Type 1", "Type 2", "HP", "Attack",
                            "Defense", "Sp. Atk", "Sp. Def", "Speed", "Total"]

    def check_for_battle(self):
        screen = screenshot(self.window_name)
        bot_screen = screen.crop(self.bot_coords)
        if check_for_battle(bot_screen, self.battle_format) > 0.85:
            top_screen = screen.crop(self.top_coords)
            box_image = top_screen.crop(self.box_coords)
            box_image = ImageOps.grayscale(box_image)
            if pytesseract.image_to_string(box_image) != self.pokemon_name:
                self.pokemon_name = pytesseract.image_to_string(box_image)
                df_current_pokemon = get_pokemon_data(
                    self.pokemon_name, df_pokemon)
                if df_current_pokemon is not None:
                    print("\n---------------------------------------------\n")
                    for element in self.print_order:
                        print(f"{element}: {df_current_pokemon.loc[element]}")
                    print_typing(df_current_pokemon, df_typing)
                    print_moves(self.pokemon_name, moves, df_pokemon)
            else:
                time.sleep(2)

    def __str__(self):
        return f'Window with the following attributes:\n\nWindow name: {self.window_name}\nTop coordinates: {self.top_coords}\nBottom coordinates: {self.bot_coords}\nBox coordinates: {self.bot_coords}'


def startup():
    time.sleep(2)
    all_windows = gw.getAllTitles()
    name_desmume = [x for x in all_windows if "DeSmuME" in x][0]
    calibration_image = screenshot(name_desmume)
    top_coords, bot_coords = calibration(calibration_image)
    top_screen = calibration_image.crop(top_coords)
    bot_screen = calibration_image.crop(bot_coords)
    bot_now, test_screen = make_images_same_size(battle_format, bot_screen)
    bot_now = ImageOps.grayscale(bot_now)
    test_screen = ImageOps.grayscale(test_screen)
    box_coords = find_name_box(top_screen)
    window = Window(window_name=name_desmume, top_coords=top_coords,
                    bot_coords=bot_coords, box_coords=box_coords)
    return window


app = Dash(__name__, external_stylesheets=[
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
])

app.layout = html.Div([
    html.H2(id='calibration_instruction',
            children='Press button to calibrate'),
    html.Button('Calibrate', id='calibration_button', n_clicks=0),
    html.H1(id='current_pokemon', children='no pokemon'),
    dcc.Store(id='window'),
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(id='polarplot')], style={'padding': 10, 'flex': 1}), html.H1(id='test'),
        html.Div(children=[
            dash_table.DataTable(id='moves_table', style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            })
        ], style={'padding': 10, 'flex': 1})], style={'display': 'flex', 'flex-direction': 'row'}),
    dcc.Interval(id='interval-component', n_intervals=0)
])


@app.callback(
    Output('calibration_instruction', 'children'),
    Output('window', 'data'),
    Input('calibration_button', 'n_clicks'),
    prevent_initial_call=True
)
def calibration_button_click(n):
    window = startup()

    return "Calibration done", vars(window)


@app.callback(
    Output('polarplot', 'figure'),
    Output('moves_table', 'data'),
    Output('moves_table', 'columns'),
    Input('current_pokemon', 'children'),
    prevent_initial_call=True
)
def update_polar_plot(current_pokemon):
    df_current_pokemon = df_pokemon[df_pokemon['Name']
                                    == current_pokemon].index[0]
    df_current_pokemon = df_pokemon.loc[df_current_pokemon]
    graph_labels = ["HP", "Attack",
                    "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    lijst = df_current_pokemon[graph_labels].T.values
    lijst = [int(x) for x in lijst]

    lijst_labels = [f'{graph_labels[x]}: {lijst[x]}' for x in range(6)]
    figure = go.Figure(go.Scatterpolar(
        name=f"{current_pokemon} stats", r=lijst, theta=lijst_labels))
    figure.update_traces(fill='toself')

    data = moves[current_pokemon]
    columns = [{'name': 'Lvl.', 'id': 0}, {'name': 'Move', 'id': 1}]
    return figure, data, columns


@app.callback(
    Output('current_pokemon', 'children'),
    Input('interval-component', 'n_intervals'),
    State('calibration_instruction', 'children'),
    State('current_pokemon', 'children'),
    State('window', 'data'),
    prevent_initial_call=True
)
def check_pokemon_name(interval, calibration_state, current_pokemon, window):
    if calibration_state == "Calibration done":
        if bool(window):
            try:
                screen = screenshot(window['window_name'])
            except:
                return current_pokemon
            bot_screen = screen.crop(tuple(window['bot_coords']))

            if check_for_battle(bot_screen, battle_format) > 0.85:
                top_screen = screen.crop(tuple(window['top_coords']))
                box_image = top_screen.crop(tuple(window['box_coords']))
                box_image = ImageOps.grayscale(box_image)
                if pytesseract.image_to_string(box_image) != current_pokemon:

                    current_pokemon = pytesseract.image_to_string(box_image)
                    current_pokemon = current_pokemon[0].upper() + \
                        current_pokemon[1:].lower()
                    all_pokemon = df_pokemon["Name"].tolist()[:-1]
                    current_pokemon = difflib.get_close_matches(
                        current_pokemon, all_pokemon, 1, 0.4)[0]
                return current_pokemon


if __name__ == "__main__":

    app.run_server(debug=False)
