import os
from os import listdir
from os.path import isfile, join
import re
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import requests

def game_already_exists(file_name, analytics_path):
    f = os.path.basename(file_name).split('/')[-1].replace('.slp', '.json')
    save_path = analytics_path + "/" + f
    if not os.path.exists(save_path):
        print(save_path, ' is new')
    return os.path.exists(save_path)

def write_game_json(game_path):
    command = 'node stats.js'
    os.system(command + ' ' + game_path)

def write_games_json(games_path, analytics_path):

    game_files = [games_path + '/' + f for f in listdir(games_path) if isfile(join(games_path, f))]
    # this took about an hour for 6000 games
    for file_name in game_files:

        if not game_already_exists(file_name, analytics_path):
            print(file_name)
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
            x['winner_connect_code'] = x["player_one_connect_code"]
            x['winning_character'] = x["player_one_character"]
            x['loser_id'] = player_two["userId"]
            x['loser_connect_code'] = x["player_two_connect_code"]
            x['losing_character'] = x["player_two_character"]
        else:
            x['winner'] = 1
            x['winner_id'] = player_two["userId"]
            x['winner_connect_code'] = x["player_two_connect_code"]
            x['winning_character'] = x["player_two_character"]
            x['loser_id'] = player_one["userId"]
            x['loser_connect_code'] = x["player_one_connect_code"]
            x['losing_character'] = x["player_one_character"]

        x['played_at'] = pd.to_datetime(df['metadata.startAt'])
        # x['overall'] = df['stats.overall']
        x['action_counts'] = df['stats.actionCounts']
        x['game_complete'] = df['stats.gameComplete']

        x['player_one_total_damage'] = df['stats.overall'][0][0]['totalDamage']
        x['player_two_total_damage'] = df['stats.overall'][0][1]['totalDamage']

        x['player_one_kill_count'] = df['stats.overall'][0][0]['killCount']
        x['player_two_kill_count'] = df['stats.overall'][0][1]['killCount']

        x['player_one_ipm'] = df['stats.overall'][0][0]['inputsPerMinute']['ratio']
        x['player_two_ipm'] = df['stats.overall'][0][1]['inputsPerMinute']['ratio']

        x['player_one_digital_ipm'] = df['stats.overall'][0][0]['digitalInputsPerMinute']['ratio']
        x['player_two_digital_ipm'] = df['stats.overall'][0][1]['digitalInputsPerMinute']['ratio']

        
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

        x['matchId'] = df['settings.matchInfo'][0]['matchId']
        
        games = pd.concat([games, x], ignore_index=True)
        return games
    else:
        print("No metadata for: ", game_file)
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
    return games.sort_values(by='played_at', ignore_index=True)

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

# opponent info

def convert_code_to_url(connect_code):
    return "http://slprank.com/rank/" + connect_code.replace("#", "-")

def find_connect_code(games, opponent):    # can use id or display name
    connect_code_pattern = re.compile("^[A-Z]+\#[0-9]+$")
    id_pattern = re.compile("^([A-Z]|[a-z]|[0-9]){28}$")
    if id_pattern.match(opponent):
        return [opponent]
    elif connect_code_pattern.match(opponent):
        return convert_code_to_url(opponent)    
    else:
        return find_connect_code_from_display_name(games, name)
    pass
    
def find_connect_code_from_id(games, id): # can use id or display name
    p1 = games.loc[(games['player_one_user_id'] == id)]['player_one_connect_code']
    p2 = games.loc[(games['player_two_user_id'] == id)]['player_two_connect_code']
    return pd.concat([p1, p2]).unique()

def find_connect_code_from_display_name(games, name): 
    p1 = games.loc[(games['player_one_display_name'] == name)]['player_one_connect_code']
    p2 = games.loc[(games['player_two_display_name'] == name)]['player_two_connect_code']
    return pd.concat([p1, p2]).unique()



# limitation: saves unranked people as silver 1 with 0W/0L and a rank of 1100
def find_opponent_info(connect_code):
    url = convert_code_to_url(connect_code)
    rank_text = requests.get(url).text
    info = defaultdict(lambda: "")
    info['connect_code'] = connect_code

    if re.compile(r"^(.*)\ \(").search(rank_text):
        info['rank'] = re.compile(r"^(.*)\ \(").search(rank_text).group(1)
        info['rating'] = re.compile(r"\((.*)\ \-").search(rank_text).group(1)
        info['wins'] = re.compile(r"\-\ ([0-9]+)W").search(rank_text).group(1)
        info['losses'] = re.compile(r"\/([0-9]+)L").search(rank_text).group(1)
    return info

def find_opponents_connect_codes(games, my_id):
    return [x for x in pd.concat([games[['player_one_connect_code']].rename(columns={"player_one_connect_code": "a"}),
                      games[['player_two_connect_code']].rename(columns={"player_two_connect_code": "a"})]).a.unique() if x]

# Don't run this too much about 35 minutes for 3144 connect_codes
def save_opponent_info(connect_code_arr):
    with open('player_info.csv', 'w', newline='') as csvfile:
        w = csv.writer(csvfile)
        w.writerow(['date', 'connect_code', 'rank', 'rating', 'wins', 'losses'])
        for connect_code in connect_code_arr:
            info = find_opponent_info(connect_code)
            # time.sleep(10)
            w.writerow([datetime.datetime.now(), 
                        info['connect_code'], 
                        info['rank'],
                        info['rating'],
                        info['wins'],
                        info['losses']])


def games_with_ranked_opponents(games, my_connect_code):
    df = pd.DataFrame(pd.read_csv("player_info.csv"))
    ranked = df[(df['rating'] != 1100.00) & 
    (df['rating'].notnull()) & 
    (df['connect_code'] != my_connect_code)]
    # ranked.sort_values(by=['rating'], ascending=False)
    opp1 = pd.merge(ranked.rename(columns={"connect_code": "player_one_connect_code"}), games, on=["player_one_connect_code"]).rename(columns={"player_one_connect_code": "connect_code"})
    opp2 = pd.merge(ranked.rename(columns={"connect_code": "player_two_connect_code"}), games, on=["player_two_connect_code"]).rename(columns={"player_two_connect_code": "connect_code"})
    opp = pd.concat([opp1, opp2])
    opp['opponent_char'] = np.where(opp['connect_code'] == opp['winner_connect_code'], opp['winning_character'], opp['losing_character'])
    opp['win'] = np.where(opp['connect_code'] == opp['winner_connect_code'], False, True)
    return opp

def win_rate_for_stage(games):
  games.groupby(['win', 'stage'])['rating'].mean()  
def win_rate_for_opponent_character(games):
  games.groupby(['win', 'opponent_char'])['rating'].mean()  
def win_rate_vs_ranked_players(games):
    print(games['win'].mean())


def stage_cat_viz(games):
    to_viz = games[['win', 'connect_code', 'winner_connect_code', 'rating', 'stage', 'opponent_char']].drop_duplicates().reset_index(drop=True)
    sns.catplot(data=to_viz, x="rating", y="stage", hue="win", jitter=False, s=8)

def opp_char_cat_viz(games):
    to_viz = games[['win', 'connect_code', 'winner_connect_code', 'rating', 'stage', 'opponent_char']].drop_duplicates().reset_index(drop=True)
    sns.catplot(data=to_viz, x="opponent_char", y="rating", hue="win", kind="swarm")

def opp_char_box_viz(games):
    to_viz = games[['win', 'connect_code', 'winner_connect_code', 'rating', 'stage', 'opponent_char']].drop_duplicates().reset_index(drop=True)
    sns.set(rc={"figure.figsize":(7, 15)})
    sns.boxplot(data=to_viz, x="rating", y="opponent_char", hue='win')

def stage_box_viz(games):
    to_viz = games[['win', 'connect_code', 'winner_connect_code', 'rating', 'stage', 'opponent_char']].drop_duplicates().reset_index(drop=True)
    sns.set(rc={"figure.figsize":(7, 15)})
    sns.boxplot(data=to_viz, x="rating", y="stage", hue='win')

