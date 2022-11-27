import time
import pandas as pd
import json
import ast
import pygetwindow as gw
from PIL import Image, ImageOps
import PIL.Image
from calibration import calibration, find_name_box
from main import check_for_battle, print_moves, print_typing
from compare_images import *
from battle_detection import *
import pytesseract
from print_pokemon_data import get_pokemon_data
from dash import Dash, dcc, html, Input, Output, State
from io import BytesIO
import base64

df_pokemon = pd.read_csv('pokemon.csv')
df_pokemon['evolution'] = df_pokemon['evolution'].apply(ast.literal_eval)
df_typing = pd.read_csv('newtyping.csv', index_col=0)
with open("pokemon_moves.json") as filehandle:
    moves = json.load(filehandle)

battle_format = Image.open("test_fotos/battle_format.png")
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


class Window():

    def __init__(self, window_name: str, top_coords: tuple[int], bot_coords: tuple[int], box_coords: tuple[int]):
        self.window_name = window_name
        self.top_coords = top_coords
        self.bot_coords = bot_coords
        self.box_coords = box_coords
        self.battle_format = Image.open("test_fotos/battle_format.png")
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


app = Dash(__name__)

app.layout = html.Div([
    html.H2(id='calibration_instruction',
            children='Press button to calibrate'),
    html.Button('Calibrate', id='calibration_button', n_clicks=0),
    dcc.Store(id='window')
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


if __name__ == "__main__":
    window = startup()
    print(vars(window))
    app.run_server(debug=True)
