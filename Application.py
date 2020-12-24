import numpy as np
import random
from matplotlib import pyplot as plt
import tbapy
import json

import CMRcalc

# Application through The Blue Alliance

'''
Credit:

Powered by The Blue Alliance
https://www.thebluealliance.com/

Queries handled through tbapy, courtesy of FRC Team 1418
https://github.com/frc1418/tbapy
'''
# TBA Helpers
def get_tba_access():
    '''
    Returns a TBA object, used to access TBA API

    If there is not a valid key in 'tba_key.json', it asks the user for
    a key and stores that.
    '''
    filename = "tba_key.txt"
    try:
        file = open(filename, "r+")
    except:
        open(filename, "w")
        file = open(filename, "r+")
    key = file.read()
    if (key == ""):
        key = input("Enter a valid TBA authentication key\n")
        file.write(key)
    tba = tbapy.TBA(key)
    file.close()
    return tba
    
def get_tba_match(tba, match_name):
    '''
    Returns TBA data on a particular match. If the match is not in the
    local file, accesses from TBA API and stores data

    Inputs:
    -tba: TBA object, used to access TBA API
    -match_name: str, TBA match designation
    Output:
    -out: dict, output of tba.match()
    '''
    filename = "tba_data.json"
    try:
        with open(filename, "r") as read_file:
            data = json.load(read_file)
    except:
        data = {}
        with open(filename, "w") as write_file:
            json.dump(data, write_file)
    if not match_name in data.keys():
        match = tba.match(match_name)
        data.update({match_name: match})
        with open(filename, "w") as write_file:
            json.dump(data, write_file)
    else:
        match = data[match_name]
    return match
    
def tba2cmr(match):
    '''
    Converts from a TBA match (dict) to a CMR match (obj)

    Input:
    -match: dict, tba match

    Output:
    -match: Match
    '''
    reds = match["alliances"]["red"]["team_keys"]
    blues = match["alliances"]["blue"]["team_keys"]
    score_r = match["alliances"]["red"]["score"]
    score_b = match["alliances"]["blue"]["score"]
    teams = reds + blues
    return CMRcalc.Match(reds, blues, score_r, score_b)

def output_data(cmrs, teams, title, visual, verbose):
    # Output
    out = {}
    for team, cmr in zip(teams, cmrs):
        out.update({team: cmr})
    if (verbose):
        print("Team\t  CMR")
        print("-------------")
        for team, cmr in zip(teams, cmrs):
            print("%s\t%s" %(team, round(cmr, 2)))
    if (visual):
        plt.hist(cmrs, bins=10)
        plt.title(title)
        plt.xlabel("Contribution to Match Result")
        plt.ylabel("Frequency")
        plt.show()
    return out

# Top-level TBA access
def get_event_results(event, visual=True, verbose=False):
    '''
    Returns the CMR of each team at a particular event

    Input:
    -event: string, official event designation
    -visual: bool, whether or not a histogram is displayed
    -verbose: whether or not each team's data is printed
    
    Output:
    -out: dict, {team_key, cmr}
    '''
    tba = get_tba_access()
    matches_tba = tba.event_matches(event, keys=True)
    matches = []
    for match_tba in matches_tba:
        match = get_tba_match(tba, match_tba)
        matches.append(tba2cmr(match))
    teams = tba.event_teams(event, keys = True)    
    cmrs = CMRcalc.calc_cmr(matches, teams)
    title = event + " CMRs"
    return output_data(cmrs, teams, title, visual, verbose)

def get_season_results(tba_key, year, visual=True, verbose=True):
    '''
    Returns the CMR of each team in a particular season

    Input:
    -tba_key: string, your The Blue Alliance API authentication key
    -year: int, year to query. No usable TBA data prior to 2002.
    -visual: bool, whether or not a histogram is displayed
    -verbose: whether or not each team's data is printed
    
    Output:
    -out: dict, {team_key, cmr}
    '''
    tba = get_tba_access()
    matches_tba = []
    teams = []
    for event in tba.events(year, keys=True):
        matches_tba += tba.event_matches(event, keys=True)
        teams += tba.event_teams(event, keys = True)
    matches = []
    for match_tba in matches_tba:
        match = get_tba_match(tba, match_tba)
        matches.append(tba2cmr(match))
    cmrs = CMRcalc.calc_cmr(matches, teams)
    title = str(year) + " CMRs"
    return output_data(cmrs, teams, title, visual, verbose)
    
# Simulated testing
def make_matches(oprs, match_count):
    '''
    Inputs:
    -oprs: np 1-D array, each team's Offensive Power Rating
    -match_count: int, number of matches
    Output:
    -out: list of Matches, with randomized matchups and scores as the sum
    of team ratings.
    '''
    # Make matchups
    team_count = len(oprs)
    matchups = []
    for i in range(match_count):
        in_match = []
        while (len(in_match) < 6):
            new_team = random.randint(0, team_count-1)
            if (new_team not in in_match):
                in_match.append(new_team)
        matchups.append(in_match)
    # Simulate matches
    matches = []
    for match in matchups:
        red_score = oprs[match[0]]
        red_score += oprs[match[1]]
        red_score += oprs[match[2]]
        blue_score = oprs[match[3]]
        blue_score += oprs[match[4]]
        blue_score += oprs[match[5]]
        new_match = CMRcalc.Match([match[0], match[1], match[2]],
                          [match[3], match[4], match[5]],
                          red_score, blue_score)
        matches.append(new_match)
    return matches

def test(team_count, match_count, visual=True, verbose=False):
    '''
    Simulates matches for each team to demonstrate the CMR calculation
    
    Inputs:
    -team_count: int, number of teams simulated
    -match_count: int, number of matches simulated
    -visual: bool, whether or not data is plotted, OPR vs CMR
    -verbose: whether or not the visual data is printed directly
    
    Outputs:
    -cmrs
    '''
    oprs = np.linspace(0, 100, team_count)
    matches = make_matches(oprs, match_count)
    cmrs = CMRcalc.calc_cmr(matches, range(team_count))
    if (verbose):
        print("OPR\t  CMR")
        print("-------------")
        for opr, cmr in zip(oprs, cmrs):
            print("%s\t%s" %(round(opr, 2), round(cmr, 2)))
    if (visual):
        plt.plot(oprs, cmrs, "bo")
        plt.title(event + " CMR vs OPR")
        plt.xlabel("Offensive Power Rating")
        plt.ylabel("Contribution to Match Result")
        plt.show()
    return cmrs
