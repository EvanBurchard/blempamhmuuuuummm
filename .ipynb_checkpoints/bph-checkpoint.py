import os
from os import listdir
from os.path import isfile, join
import re
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt

def write_game_json(game_path):
    command = 'node stats.js'
    os.system(command + ' ' + game_path)

def write_games_json(games_path):
    game_files = [games_path + '/' + f for f in listdir(games_path) if isfile(join(games_path, f))]
    # this took about an hour for 6000 games
    for file_name in game_files:
        if not os.path.exists(file_name):
            write_game_json(file_name)

def load_single_game(game_file, games):
    with open(game_file) as f:
        d = json.load(f)
    with open("characters.json") as f:
        characters = json.load(f)
    with open("moves.json") as f:
        moves = json.load(f)
    with open("stages.json") as f:
        stages = json.load(f)
    
    df = pd.json_normalize(d, max_level=1)
    if d['metadata']:
        x = pd.DataFrame()
        x['game_length'] = df['stats.playableFrameCount'] / 60
        x['stage'] = df['settings.stageId'].astype(str).map(stages)
        player_one = df["settings.players"][0][0]
        player_two = df["settings.players"][0][1]
        x['player_one_display_name'] = player_one["displayName"]
        x['player_two_display_name'] = player_two["displayName"]
        x['player_one_connect_code'] = player_one["connectCode"]
        x['player_two_connect_code'] = player_two["connectCode"]
        x['player_one_user_id'] = player_one["userId"]
        x['player_two_user_id'] = player_two["userId"]
        x['player_one_character'] = characters[str(player_one["characterId"])]['name']
        x['player_two_character'] = characters[str(player_two["characterId"])]['name']
    
        # These won't work till default colors are added (prepended) to characters.json
        # x['player_one_character_color'] = characters[str(player_one["characterId"])]['colors'][player_one["characterColor"]]
        # x['player_two_character_color'] = characters[str(player_two["characterId"])]['colors'][player_two["characterColor"]]
    
        stock_lost_counter = [0, 0]
        stocks_lost = [stock['playerIndex'] for stock in df['stats.stocks'][0] if stock['endFrame']]
        for stock in stocks_lost:
            if stock == 0:
                stock_lost_counter[0] += 1
            else:
                stock_lost_counter[1] += 1
    
        x['player_one_lost_stocks'] = stock_lost_counter[0]
        x['player_two_lost_stocks'] = stock_lost_counter[1]
        if stock_lost_counter[0] == stock_lost_counter[1]:
            x['winner'] = None
            x['winner_id'] = None
        elif stock_lost_counter[0] < stock_lost_counter[1]:
            x['winner'] = 0
            x['winner_id'] = player_one["userId"]
            x['winning_character'] = x["player_one_character"]
            x['loser_id'] = player_two["userId"]
            x['losing_character'] = x["player_two_character"]
        else:
            x['winner'] = 1
            x['winner_id'] = player_two["userId"]
            x['winning_character'] = x["player_two_character"]
            x['loser_id'] = player_one["userId"]
            x['losing_character'] = x["player_one_character"]

        x['played_at'] = df['metadata.startAt']
        x['overall'] = df['stats.overall']
        x['action_counts'] = df['stats.actionCounts']
        x['game_complete'] = df['stats.gameComplete']

        # movement
        x['player_one_failed_l_cancels'] = df['stats.actionCounts'][0][0]['lCancelCount']['fail']
        x['player_one_successful_l_cancels'] = df['stats.actionCounts'][0][0]['lCancelCount']['success']
        x['player_two_failed_l_cancels'] = df['stats.actionCounts'][0][1]['lCancelCount']['fail']
        x['player_two_successful_l_cancels'] = df['stats.actionCounts'][0][1]['lCancelCount']['success']
        x['player_one_wavedash_count'] = df['stats.actionCounts'][0][0]['wavedashCount']
        x['player_one_waveland_count'] = df['stats.actionCounts'][0][0]['wavelandCount']
        x['player_two_wavedash_count'] = df['stats.actionCounts'][0][1]['wavedashCount']
        x['player_two_waveland_count'] = df['stats.actionCounts'][0][1]['wavelandCount']
        x['player_one_airdodge_count'] = df['stats.actionCounts'][0][0]['airDodgeCount']
        x['player_one_dashdance_count'] = df['stats.actionCounts'][0][0]['dashDanceCount']
        x['player_two_airdodge_count'] = df['stats.actionCounts'][0][1]['airDodgeCount']
        x['player_two_dashdance_count'] = df['stats.actionCounts'][0][1]['dashDanceCount']
        x['player_one_spotdodge_count'] = df['stats.actionCounts'][0][0]['spotDodgeCount']
        x['player_one_roll_count'] = df['stats.actionCounts'][0][0]['rollCount']
        x['player_two_spotdodge_count'] = df['stats.actionCounts'][0][1]['spotDodgeCount']
        x['player_two_roll_count'] = df['stats.actionCounts'][0][1]['rollCount']
        x['player_one_ledgegrab_count'] = df['stats.actionCounts'][0][0]['ledgegrabCount']
        x['player_two_ledgegrab_count'] = df['stats.actionCounts'][0][1]['ledgegrabCount']

        # attackCount
        # throwCount
        # grabCount
        # wallTechCount

        x['player_one_tech_away'] = df['stats.actionCounts'][0][0]['groundTechCount']['away']
        x['player_one_tech_in'] = df['stats.actionCounts'][0][0]['groundTechCount']['in']
        x['player_one_tech_neutral'] = df['stats.actionCounts'][0][0]['groundTechCount']['neutral']
        x['player_one_tech_fail'] = df['stats.actionCounts'][0][0]['groundTechCount']['fail']
        x['player_two_tech_away'] = df['stats.actionCounts'][0][1]['groundTechCount']['away']
        x['player_two_tech_in'] = df['stats.actionCounts'][0][1]['groundTechCount']['in']
        x['player_two_tech_neutral'] = df['stats.actionCounts'][0][1]['groundTechCount']['neutral']
        x['player_two_tech_fail'] = df['stats.actionCounts'][0][1]['groundTechCount']['fail']

        games = pd.concat([games, x], ignore_index=True)
        # print(games.shape)
        return games
    else:
        print("something went wrong with: ", game_file)
        # print(games.shape)
        return games

def load_multiple_games(analytics_path):
    analytics_files = [analytics_path + '/' + f for f in listdir(analytics_path) if isfile(join(analytics_path, f))]
    games = pd.DataFrame()
    for i, f in enumerate(analytics_files):
        try:
            games = load_single_game(f, games)
        except:
            print("An exception occurred for: ") 
            print(f)
    return games

def find_my_id(games):
    return games['player_one_user_id'].mode()[0]

# scoping
def finished_games(games):
    return games.loc[(games['winner_id'].notnull())]

def recent_games(games, n):
    return games.tail(n)

# win rates

def wins(games, my_id):
    return games.loc[(games['winner_id'] == my_id)]

def losses(games, my_id):
    return games.loc[(games['loser_id'] == my_id)]
    
def overall_win_rates(games, my_id):
    w = wins(games, my_id)
    l = losses(games, my_id)
    undetermined = games.loc[(games['winner_id'].isnull())]
    if w.shape[0] + l.shape[0] == 0:
        return w.shape[0], l.shape[0], 0
    return w.shape[0], l.shape[0], w.shape[0] / (w.shape[0] + l.shape[0])


def win_rates_by_character(games, my_id, my_character, their_character):
    w = wins(games, my_id)
    l = losses(games, my_id)    
    w = w.loc[(w['winning_character'] == my_character) & (w['losing_character'] == their_character)]
    l = l.loc[(l['winning_character'] == their_character) & (l['losing_character'] == my_character)]
    if w.shape[0] + l.shape[0] == 0:
        return w.shape[0], l.shape[0], 0
    return w.shape[0], l.shape[0], w.shape[0] / (w.shape[0] + l.shape[0])

def win_rates_by_stage(games, my_id, stage):
    w = wins(games, my_id)
    l = losses(games, my_id)
    w = w.loc[(w['stage'] == stage)]
    l = l.loc[(l['stage'] == stage)]
    if w.shape[0] + l.shape[0] == 0:
        return w.shape[0], l.shape[0], 0
    return w.shape[0], l.shape[0], w.shape[0] / (w.shape[0] + l.shape[0])

def win_rates_for_all_characters(games, my_id):
    char_names = ["Captain Falcon", "Donkey Kong", "Fox", "Mr. Game & Watch", "Kirby", "Bowser",
     "Link", "Luigi", "Mario", "Marth", "Mewtwo", "Ness", "Peach", "Pikachu", "Ice Climbers", 
     "Jigglypuff", "Samus", "Yoshi", "Zelda", "Sheik", "Falco", "Young Link", "Dr. Mario", "Roy", "Pichu", "Ganondorf"]
    win_rates = {}
    for char in char_names:
        char_wins = win_rates_by_character(games, my_id, "Yoshi", char)
        win_rates[char] = char_wins[2]
        # print("\nwin rate vs " + char + ":\n", char_wins[0], "\nlosses: ", char_wins[1], "\nwin rate: ", char_wins[2])
    return win_rates

def print_overall_win_rates(games, my_id):
    overall = overall_win_rates(games, my_id)
    print("wins: ", overall[0], "\nlosses: ", overall[1], "\nwin rate: ", overall[2])

def win_rates_for_all_stages(games, my_id):
    stages = ["Fountain of Dreams",
            "Pokémon Stadium",
            "Princess Peach's Castle",
            "Kongo Jungle",
            "Brinstar",
            "Corneria",
            "Yoshi's Story",
            "Onett",
            "Mute City",
            "Rainbow Cruise",
            "Jungle Japes",
            "Great Bay",
            "Hyrule Temple",
            "Brinstar Depths",
            "Yoshi's Island",
            "Green Greens",
            "Fourside",
            "Mushroom Kingdom I",
            "Mushroom Kingdom II"
            "Venom",
            "Poké Floats",
            "Big Blue",
            "Icicle Mountain",
            "Icetop",
            "Flat Zone",
            "Dream Land N64",
            "Yoshi's Island N64",
            "Kongo Jungle N64",
            "Battlefield",
            "Final Destination"]
    win_rates = {}
    for stage in stages:
        stage_wins = win_rates_by_stage(games, my_id, stage)
        win_rates[stage] = stage_wins[2]
        # print("\nwin rate vs " + char + ":\n", char_wins[0], "\nlosses: ", char_wins[1], "\nwin rate: ", char_wins[2])
    win_rates = {k: v for k, v in sorted(win_rates.items(), key=lambda item: item[1], reverse=True)}
    return win_rates

def get_character_win_rates(games, my_id):
    win_rates = win_rates_for_all_characters(games, my_id)
    return {k: v for k, v in sorted(win_rates.items(), key=lambda item: item[1])}

# Opponent

def get_opponent_history(games, opponent):
    connect_code_pattern = re.compile("^[A-Z]+\#[0-9]+$")
    id_pattern = re.compile("^([A-Z]|[a-z]|[0-9]){28}$")
    if id_pattern.match(opponent):
        return get_opponent_history_by_id(games, opponent)    
    elif connect_code_pattern.match(opponent):
        return get_opponent_history_by_connect_code(games, opponent)    
    else:
        return get_opponent_history_by_display_name(games, opponent)    

def get_opponent_history_by_id(games, opponent):
    return games.loc[(games["player_one_user_id"] == opponent) | (games["player_two_user_id"] == opponent)] 
def get_opponent_history_by_connect_code(games, opponent):
    return games.loc[(games["player_one_connect_code"] == opponent) | (games["player_two_connect_code"] == opponent)] 
def get_opponent_history_by_display_name(games, opponent):
    return games.loc[(games["player_one_display_name"] == opponent) | (games["player_two_display_name"] == opponent)] 

# encounters

def encounter_rates_by_character(games, my_id, their_character):
    a = games.loc[(games['winner_id'] == my_id) & (games['losing_character'] == their_character)]
    b = games.loc[(games['loser_id'] == my_id) & (games['winning_character'] == their_character)]
    c = pd.concat([a, b], ignore_index=True)
    wr = overall_win_rates(games, my_id)

    return c.shape[0] / (wr[0] + wr[1])

def encounter_rates_across_characters(games, my_id):
    char_names = ["Captain Falcon", "Donkey Kong", "Fox", "Mr. Game & Watch", "Kirby", "Bowser",
     "Link", "Luigi", "Mario", "Marth", "Mewtwo", "Ness", "Peach", "Pikachu", "Ice Climbers", 
     "Jigglypuff", "Samus", "Yoshi", "Zelda", "Sheik", "Falco", "Young Link", "Dr. Mario", "Roy", "Pichu", "Ganondorf"]
    
    encounter_rates = {}
    for char in char_names:
        char_encounters = encounter_rates_by_character(games, my_id, char)
        encounter_rates[char] = char_encounters
    return {k: v for k, v in sorted(encounter_rates.items(), key=lambda item: item[1], reverse=True)}

# L-Cancels

def l_cancel_rate(games, my_id, me=True):
    games = finished_games(games)
    if me:
        p1 = games.loc[(games['player_one_user_id'] == my_id)][['player_one_successful_l_cancels', 'player_one_failed_l_cancels']]
        p2 = games.loc[(games['player_two_user_id'] == my_id)][['player_two_successful_l_cancels', 'player_two_failed_l_cancels']]
    else:
        p1 = games.loc[(games['player_two_user_id'] == my_id)][['player_one_successful_l_cancels', 'player_one_failed_l_cancels']]
        p2 = games.loc[(games['player_one_user_id'] == my_id)][['player_two_successful_l_cancels', 'player_two_failed_l_cancels']]
    successful = p1[['player_one_successful_l_cancels']].sum().iloc[0] + p2[['player_two_successful_l_cancels']].sum().iloc[0]
    failed = p1[['player_one_failed_l_cancels']].sum().iloc[0] + p2[['player_two_failed_l_cancels']].sum().iloc[0]
    return successful / (successful + failed)

def l_cancel_ratio_over_time(games, my_id, batches, me=True):
    games = finished_games(games)
    if me:
        p1 = games.loc[(games['player_one_user_id'] == my_id)][['player_one_successful_l_cancels', 'player_one_failed_l_cancels']].rename(columns = {'player_one_successful_l_cancels':'success', 'player_one_failed_l_cancels':'failed'})
        p2 = games.loc[(games['player_two_user_id'] == my_id)][['player_two_successful_l_cancels', 'player_two_failed_l_cancels']].rename(columns = {'player_two_successful_l_cancels':'success', 'player_two_failed_l_cancels':'failed'})
    else:
        p1 = games.loc[(games['player_one_user_id'] == my_id)][['player_two_successful_l_cancels', 'player_two_failed_l_cancels']].rename(columns = {'player_two_successful_l_cancels':'success', 'player_two_failed_l_cancels':'failed'})
        p2 = games.loc[(games['player_two_user_id'] == my_id)][['player_one_successful_l_cancels', 'player_one_failed_l_cancels']].rename(columns = {'player_one_successful_l_cancels':'success', 'player_one_failed_l_cancels':'failed'})
        
    p = pd.concat([p1, p2]).sort_index().reset_index(drop=True)
    p['batch'] = (p.index) // (p.shape[0] // batches)
    # print(p)
    g1 = p.groupby('batch')['success'].sum()
    g2 = p.groupby('batch')['failed'].sum()
    return (g1 / (g1 + g2))

def show_l_cancel_rate_over_time(games, my_id, batches):
    x = np.linspace(0, 1, batches+1)
    y = l_cancel_rate_over_time(games, my_id, batches)    
    fig, ax = plt.subplots()
    ax.plot(x, y)
    plt.show()
# Tech Options

def tech_options(games, my_id, me=True):
    games = finished_games(games)
    if me:
        p1 = games.loc[(games['player_one_user_id'] == my_id)][['player_one_character', 'player_one_tech_away', 'player_one_tech_in', 'player_one_tech_neutral', 'player_one_tech_fail']]
        p2 = games.loc[(games['player_two_user_id'] == my_id)][['player_two_character', 'player_two_tech_away', 'player_two_tech_in', 'player_two_tech_neutral', 'player_two_tech_fail']]
    else:
        p1 = games.loc[(games['player_two_user_id'] == my_id)][['player_one_character', 'player_one_tech_away', 'player_one_tech_in', 'player_one_tech_neutral', 'player_one_tech_fail']]
        p2 = games.loc[(games['player_one_user_id'] == my_id)][['player_two_character', 'player_two_tech_away', 'player_two_tech_in', 'player_two_tech_neutral', 'player_two_tech_fail']]
    
    p1.rename(columns = {'player_one_tech_away': 'tech_away', 
                         'player_one_tech_in': 'tech_in',
                         'player_one_tech_neutral': 'tech_neutral',
                         'player_one_tech_fail': 'tech_fail',
                         'player_one_character': 'character'}, inplace=True)

    p2.rename(columns = {'player_two_tech_away': 'tech_away', 
                         'player_two_tech_in': 'tech_in',
                         'player_two_tech_neutral': 'tech_neutral',
                         'player_two_tech_fail': 'tech_fail',
                         'player_two_character': 'character'}, inplace=True)

    p = pd.concat([p1, p2]).sort_index().reset_index(drop=True)
    totals = p[['tech_away', 'tech_in', 'tech_fail', 'tech_neutral']].sum()
    total = totals.sum()
    return total, totals, totals/total

def tech_options_by_character(games, my_id, character):
    games = finished_games(games)

    p1 = games.loc[(games['player_two_user_id'] == my_id) & (games['player_one_character'] == character)][['player_one_character', 'player_one_tech_away', 'player_one_tech_in', 'player_one_tech_neutral', 'player_one_tech_fail']]
    p2 = games.loc[(games['player_one_user_id'] == my_id) & (games['player_two_character'] == character)][['player_two_character', 'player_two_tech_away', 'player_two_tech_in', 'player_two_tech_neutral', 'player_two_tech_fail']]
    p1.rename(columns = {'player_one_tech_away': 'tech_away', 
                         'player_one_tech_in': 'tech_in',
                         'player_one_tech_neutral': 'tech_neutral',
                         'player_one_tech_fail': 'tech_fail',
                         'player_one_character': 'character'}, inplace=True)
    p2.rename(columns = {'player_two_tech_away': 'tech_away', 
                         'player_two_tech_in': 'tech_in',
                         'player_two_tech_neutral': 'tech_neutral',
                         'player_two_tech_fail': 'tech_fail',
                         'player_two_character': 'character'}, inplace=True)
    p = pd.concat([p1, p2]).sort_index().reset_index(drop=True)
    return p


def all_character_tech_options(games, my_id):
    char_names = ["Captain Falcon", "Donkey Kong", "Fox", "Mr. Game & Watch", "Kirby", "Bowser",
         "Link", "Luigi", "Mario", "Marth", "Mewtwo", "Ness", "Peach", "Pikachu", "Ice Climbers", 
         "Jigglypuff", "Samus", "Yoshi", "Zelda", "Sheik", "Falco", "Young Link", "Dr. Mario", "Roy", "Pichu", "Ganondorf"]
    tech_stats = {}
    for char in char_names:
        tech_options_for_thee = tech_options_by_character(games, my_id, char)
        totals = tech_options_for_thee[['tech_away', 'tech_in', 'tech_fail', 'tech_neutral']].sum()
        total = totals.sum()
        tech_stats[char] = totals / total
    return tech_stats

# Shmoves

def shmove_counts(games, my_id, me=True):
    if me:
        p1 = games.loc[(games['player_one_user_id'] == my_id)][['player_one_character', 'player_one_wavedash_count', 'player_one_waveland_count', 'player_one_airdodge_count', 'player_one_dashdance_count', 'player_one_spotdodge_count', 'player_one_roll_count', 'player_one_ledgegrab_count']]
        p2 = games.loc[(games['player_two_user_id'] == my_id)][['player_two_character', 'player_two_wavedash_count', 'player_two_waveland_count', 'player_two_airdodge_count', 'player_two_dashdance_count', 'player_two_spotdodge_count', 'player_two_roll_count', 'player_two_ledgegrab_count']]
    else:
        p1 = games.loc[(games['player_two_user_id'] == my_id)][['player_one_character', 'player_one_wavedash_count', 'player_one_waveland_count', 'player_one_airdodge_count', 'player_one_dashdance_count', 'player_one_spotdodge_count', 'player_one_roll_count', 'player_one_ledgegrab_count']]
        p2 = games.loc[(games['player_one_user_id'] == my_id)][['player_two_character', 'player_two_wavedash_count', 'player_two_waveland_count', 'player_two_airdodge_count', 'player_two_dashdance_count', 'player_two_spotdodge_count', 'player_two_roll_count', 'player_two_ledgegrab_count']]
    p1.rename(columns = {'player_one_wavedash_count': 'wavedash_count', 
                         'player_one_waveland_count': 'waveland_count',
                         'player_one_airdodge_count': 'airdodge_count',
                         'player_one_dashdance_count': 'dashdance_count',
                         'player_one_spotdodge_count': 'spotdodge_count',
                         'player_one_roll_count': 'roll_count',
                         'player_one_ledgegrab_count': 'ledgegrab_count',
                         'player_one_character': 'character'}, inplace=True)

    p2.rename(columns = {'player_two_wavedash_count': 'wavedash_count', 
                         'player_two_waveland_count': 'waveland_count',
                         'player_two_airdodge_count': 'airdodge_count',
                         'player_two_dashdance_count': 'dashdance_count',
                         'player_two_spotdodge_count': 'spotdodge_count',
                         'player_two_roll_count': 'roll_count',
                         'player_two_ledgegrab_count': 'ledgegrab_count',
                         'player_two_character': 'character'}, inplace=True)
    p = pd.concat([p1, p2]).sort_index().reset_index(drop=True)
    # print(p)
    return p

def show_my_shmove_counts(games, my_id):
    shmoves = shmove_counts(games, my_id)    
    x = np.linspace(0, shmoves.shape[0], shmoves.shape[0])
    y = shmoves['roll_count']
    fig, ax = plt.subplots()
    ax.plot(x, y)
    plt.show()

def avg_shmove_counts(games, my_id, me=True):
    shmoves = shmove_counts(games, my_id, me)
    totals = shmoves[['wavedash_count', 'waveland_count', 'airdodge_count', 'dashdance_count', 'spotdodge_count', 'roll_count', 'ledgegrab_count']].sum() / shmoves.shape[0]
    return totals

