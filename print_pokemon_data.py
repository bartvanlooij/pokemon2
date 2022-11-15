
import pandas as pd
import difflib
def get_pokemon_data(pokemon : str, df_stats : pd.DataFrame):
    if pokemon:
        pokemon = pokemon[0] + pokemon[1:].lower()
        pokemon = pokemon.strip()
        all_pokemon = df_stats["Name"].tolist()[:-1]
        pokemon = difflib.get_close_matches(pokemon, all_pokemon, 1,0.4)[0]
        df_current_pokemon = df_stats.loc[df_stats[df_stats["Name"] == pokemon].index[0]]
        return df_current_pokemon