import tbapy
import numpy as np
from matplotlib import pyplot as plt
import json
import random
import time
from datetime import date

class Match:
    '''
    Represents FRC match data
    Data should be treated as immutable
    '''
    def __init__(self, reds, blues, score_r, score_b):
        self.teams = reds + blues
        self.red_teams = reds
        self.blue_teams = blues
        self.sr = score_r
        self.sb = score_b

    def to_str(self):
        out = "Red:"
        for team in self.red_teams:
            out += " " + str(team)
        out += "(%s)\n" %self.sr
        out+= "Blue:"
        for team in self.blue_teams:
            out += " " + str(team)
        out += "(%s)\n" %self.sb
        return out

#-------------------------
# Core Algorithm
#-------------------------
def calc_cmr(matches, team_keys):
    '''
    Determines each team's Contribution to Match Result (CMR)
    The sum of your alliance's CMR minus the sum of your opponents' CMRs
    produces a match prediction, with 1 as a win and -1 as a loss.
    
    Inputs:
    -matches: list, Match objects
    -team_count: int, number of teams in data
    
    Output:
    -cmr: dict, {team, Contribution to Match Result}
    '''
    # Calculate match matrix
    team_count = len(team_keys)
    mat_matches = np.zeros((team_count, len(matches)))
    for team, team_idx in zip(team_keys, range(len(team_keys))):
        for match, num in zip(matches, range(len(matches))):
            if team in match.red_teams:
                val = 1
            elif team in match.blue_teams:
                val = -1
            else:
                val = 0
            mat_matches[team_idx, num] = val
    # Calculate score matrix
    mat_scores = []
    for match in matches:
        if (match.sr > match.sb):
            score_norm = 1
        elif (match.sr < match.sb):
            score_norm = -1
        else:
            score_norm = 0
        #score_norm = (match.sr - match.sb)/(match.sr + match.sb)
        mat_scores.append(score_norm)
    mat_scores = np.array(mat_scores)
    # Calculate CMR
    mat_matches = np.transpose(mat_matches)
    out = np.linalg.lstsq(mat_matches, mat_scores, rcond=None)[0]
    out = 100*out
    return out.tolist()

#-------------------------
# Application Helpers
#-------------------------
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
    return Match(reds, blues, score_r, score_b)

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

#-------------------------
# User-Facing Application
#-------------------------
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
    cmrs = calc_cmr(matches, teams)
    title = event + " CMRs"
    return output_data(cmrs, teams, title, visual, verbose)

def get_season_results(year, visual=True, verbose=True):
    '''
    Returns the CMR of each team in a particular season

    Input:
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
    cmrs = calc_cmr(matches, teams)
    title = str(year) + " CMRs"
    return output_data(cmrs, teams, title, visual, verbose)

def get_historic_results(visual=True, verbose=True):
    '''
    Returns the CMR of each team to compete in FRC since 2002

    Input:
    -visual: bool, whether or not a histogram is displayed
    -verbose: whether or not each team's data is printed
    
    Output:
    -out: dict, {team_key, cmr}
    '''
    tba = get_tba_access()
    matches_tba = []
    today = date.today()
    years = range(2002, today.year+1)
    for year in years:
        for event in tba.events(year, keys=True):
            matches_tba += tba.event_matches(event, keys=True)
    matches = []
    for match_tba in matches_tba:
        match = get_tba_match(tba, match_tba)
        matches.append(tba2cmr(match))
    teams = tba.teams(keys=True)
    cmrs = calc_cmr(matches, teams)
    title = "Historic CMRs"
    return output_data(cmrs, teams, title, visual, verbose)


def get_all_tba(tba, show_time=True):
    '''
    Stores all TBA matches locally, 2002-present
    NOTE: Will take over an hour and a GB of data

    Inputs:
    -tba: TBA object, used to access TBA API
    -show_time: bool, whether to show the download time
    '''
    if show_time:
        start = time.perf_counter()
    today = date.today()
    years = range(2002, today.year+1)
    matches_tba = []
    for year in years:
        for event in tba.events(year, keys=True):
            matches_tba += tba.event_matches(event, keys=True)
    for match_tba in matches_tba:
        get_tba_match(tba, match_tba)
    if show_time:
        seconds = time.perf_counter - start
        print("Download time: " + str(seconds) + " seconds")

#-------------------------
# Simulated testing
#-------------------------
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
        new_match = Match([match[0], match[1], match[2]],
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
    cmrs = calc_cmr(matches, range(team_count))
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
