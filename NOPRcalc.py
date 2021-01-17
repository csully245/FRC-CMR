import tbapy
import numpy as np
from matplotlib import pyplot as plt
import json
import random
import time
from datetime import date

class Demi_Match:
    '''
    Represents FRC match data for one alliance
    Data should be treated as immutable
    '''
    def __init__(self, teams, score):
        self.teams = teams
        self.score = score

    def to_str(self):
        out = "Teams:"
        for team in self.teams:
            out += " " + str(team)
        out += "\nScore: " + str(self.score)
        return out

def sort_dict(d):
    out = {}
    for w in sorted(d, key=d.get, reverse=True):
        out.update({w: d[w]})
    return out
#-------------------------
# Core Algorithm
#-------------------------
def get_oprs(matches, team_keys):
    '''
    Determines each team's Offensive Power Rating (OPR)
    
    Inputs:
    -matches: list, Match objects
    -team_count: int, number of teams in data
    
    Output:
    -opr: dict, {team, Offensive Power Rating}
    '''
    # Calculate match matrix
    team_count = len(team_keys)
    mat_matches = np.zeros((team_count, len(matches)))
    for team, team_idx in zip(team_keys, range(len(team_keys))):
        for match, match_idx in zip(matches, range(len(matches))):
            if team in match.teams:
                if team == "frc1322":
                    print(match_idx)
                val = 1
            else:
                val = 0
            mat_matches[team_idx, match_idx] = val
    
    # Calculate score matrix
    mat_scores = []
    for match in matches:
        mat_scores.append(match.score)
    mat_scores = np.array(mat_scores)
    # Calculate OPR
    mat_matches = np.transpose(mat_matches)
    out = np.linalg.lstsq(mat_matches, mat_scores, rcond=None)[0]
    return out.tolist()

def normalize_opr(oprs):
    '''
    Determines each team's Normalized OPR.
    
    Inputs:
    -oprs: list, each team's OPR
    
    Output:
    -nopr: dict, {team, Normalized OPR}
    '''
    mean = np.mean(oprs)
    stdev = np.std(oprs)
    oprs = (oprs - mean) / stdev
    return oprs
    
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

def tba2demi(match):
    '''
    Converts from a TBA match (dict) to two Demi_Matches (obj)
    Input:
    -match: dict, tba match
    
    Output:
    -match: tuple, (Demo_Match, Demo_Match)
    '''
    red_teams = match["alliances"]["red"]["team_keys"]
    score_red = match["alliances"]["red"]["score"]
    red = Demi_Match(red_teams, score_red)
    blue_teams = match["alliances"]["blue"]["team_keys"]
    score_blue = match["alliances"]["blue"]["score"]
    blue = Demi_Match(blue_teams, score_blue)
    return (red, blue)

def output_data(noprs, teams, title, visual, verbose):
    # Output
    out = {}
    for team, nopr in zip(teams, noprs):
        out.update({team: nopr})
    out = sort_dict(out)
    if (verbose):
        print("Team\t  NOPR")
        print("-------------")
        for team, nopr in zip(out.keys(), out.values()):
            print("%s\t%s" %(team, round(nopr, 2)))
    if (visual):
        plt.hist(noprs, bins=15)
        plt.title(title)
        plt.xlabel("Normalized OPR")
        plt.ylabel("Frequency")
        plt.show()
    return out

#-------------------------
# User-Facing Application
#-------------------------
def get_event_results(event, visual=True, verbose=False):
    '''
    Returns the NOPR of each team with respect to particular event
    Input:
    -event: string, official event designation
    -visual: bool, whether or not a histogram is displayed
    -verbose: whether or not each team's data is printed
    
    Output:
    -out: dict, {team_key, NOPR}
    '''
    tba = get_tba_access()
    matches_tba = tba.event_matches(event, keys=True)
    matches = []
    for match_tba in matches_tba:
        match = get_tba_match(tba, match_tba)
        matches.append(tba2demi(match)[0])
        matches.append(tba2demi(match)[1])
    teams = tba.event_teams(event, keys=True)    
    oprs = get_oprs(matches, teams)
    noprs = normalize_opr(oprs)
    title = event + " Normalized OPRs"
    return output_data(noprs, teams, title, visual, verbose)
