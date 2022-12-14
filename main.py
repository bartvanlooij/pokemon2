import time
from battle_detection import *
from calibration import calibration, find_name_box
import pygetwindow as gw
from PIL import Image, ImageFilter, ImageOps
from compare_images import *
import pytesseract
from print_pokemon_data import get_pokemon_data
import pandas as pd
import ast
import json
import difflib
import math
import numpy as np
import keyboard
def check_for_battle(bot : PIL.Image.Image, test_screen : PIL.Image.Image):
    bot, test_screen = make_images_same_size(test_screen, bot)
    bot = ImageOps.grayscale(bot)
    test_screen = ImageOps.grayscale(test_screen)
    similairity = similarity(bot, test_screen)
    return similairity

def evolution_walk(evolution):
    if not evolution:
        return ""
    else:
        evolution_walk(evolution)
        if evolution[1] == 'level-up':
            return f'---  Lvl. {evolution[2]}  --->  {evolution[0]}'
        if evolution[1] == 'use-item':
            return f'---  {evolution[2][0].upper()}{evolution[2][1:]}  --->  {evolution[0]}'
        if evolution[1] == "---  trade  ---> ":
            return f'---  Trade  ---> {evolution[2]}'
def print_evolution_order(df_current_pokemon):
    return_string = ""
    evolution_possibilities = ['level-up', 'use-item', 'trade']
    evolutions = df_current_pokemon.loc['evolution']
    for x in evolutions:
        return_string = return_string + f"\n\n{df_current_pokemon.loc['Name']}"
        return_string = return_string + evolution_walk(x)



    return return_string

def print_moves(pokemon : str, moves : dict, df_pokemon : pd.DataFrame):
    print("\nMoves:")
    all_pokemon = df_pokemon["Name"].tolist()[:-1]
    pokemon = pokemon[0] + pokemon[1:].lower()
    pokemon = difflib.get_close_matches(pokemon, all_pokemon, 1, 0.4)[0]
    for x in moves[pokemon.strip()]:
        print(f"Lvl. {x[0]}: {x[1]}")

def print_typing(df_current_pokemon : pd.DataFrame, df_typing : pd.DataFrame):
    type1 = df_current_pokemon.loc['Type 1']
    type2 = df_current_pokemon.loc['Type 2']
    type_combinations = {}
    for i in df_typing.index:
        type_combinations[i] = float(df_typing.loc[i, type1])
        if isinstance(type2, str):

            type_combinations[i] = type_combinations[i] * float(df_typing.loc[i, type2])
    string_weak = "2x damaged by: "
    string_resist = "1/2 damaged by: "
    string_immune = "Immune: "
    string_double_resist = "1/4x damaged by: "
    string_double_weak = "4x damaged by: "
    print(type_combinations)
    for key in type_combinations.keys():
        if type_combinations[key] == 0:
            string_immune += key + ", "
        if type_combinations[key] == 2:
            string_weak += key + ", "
        if type_combinations[key] == 4:
            string_double_weak += key + ", "
        if type_combinations[key] == 0.25:
            string_double_resist += key + ", "
        if type_combinations[key] == 0.5:
            string_resist += key + ", "

    print("\nType effectiveness: ")
    if not string_double_weak.endswith(': '):
        print(string_double_weak[:-2])
    if not string_weak.endswith(': '):
        print(string_weak[:-2])
    if not string_resist.endswith(': '):
        print(string_resist[:-2])
    if not string_double_resist.endswith(': '):
        print(string_double_resist[:-2])
    if not string_immune.endswith(': '):
        print(string_immune[:-2])




def main():
    with open("pokemon_moves.json") as filehandle:
        moves = json.load(filehandle)
    df_typing = pd.read_csv("newtyping.csv", index_col=0)
    calibrated = False
    print_order = ["Name", "Type 1", "Type 2", "HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed", "Total"]
    global df_pokemon
    df_pokemon = pd.read_csv("pokemon.csv", index_col=0)
    df_pokemon['evolution'] = df_pokemon['evolution'].apply(ast.literal_eval)
    df_all_moves = pd.read_csv("df_all_moves.csv", index_col=0)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
    all_windows = gw.getAllTitles()
    name_desmume = [x for x in all_windows if "DeSmuME" in x][0]
    calibration_image = screenshot(name_desmume)
    top_coords, bot_coords = calibration(calibration_image)
    top_screen = calibration_image.crop(top_coords)
    bot_screen = calibration_image.crop(bot_coords)
    battle_format = Image.open("test_fotos/battle_format.png")
    bot_now, test_screen = make_images_same_size(battle_format, bot_screen)
    bot_now = ImageOps.grayscale(bot_now)
    test_screen = ImageOps.grayscale(test_screen)
    box_coords = find_name_box(top_screen)
    calibrated = True
    pokemon_name = "pickacu"
    print("Calibration done")
    while calibrated:
        if keyboard.is_pressed("F7"):
            sys.exit()
        try:
            screen = screenshot(name_desmume)
            focus = True
        except:
            time.sleep(0.5)
            if focus:
                print("Screen out of focus")
                focus = False
        if focus:
            bot_screen = screen.crop(bot_coords)
            if (check_for_battle(bot_screen, test_screen) > 0.85):
                currently_in_battle = True
            else:
                currently_in_battle = False


            if currently_in_battle:

                top_screen = screen.crop(top_coords)
                box_image = top_screen.crop(box_coords)
                box_image = ImageOps.grayscale(box_image)
                if pytesseract.image_to_string(box_image) != pokemon_name:
                    pokemon_name = pytesseract.image_to_string(box_image)
                    df_current_pokemon = get_pokemon_data(pokemon_name, df_pokemon)
                    if df_current_pokemon is not None:
                        print("\n---------------------------------------------\n")
                        for element in print_order:
                            print(f"{element}: {df_current_pokemon.loc[element]}")
                        print_typing(df_current_pokemon, df_typing)
                        print_moves(pokemon_name, moves, df_pokemon)
                    # print(print_evolution_order(df_current_pokemon))





if __name__ == "__main__":
    main()