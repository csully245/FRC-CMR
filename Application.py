import numpy as np
import random
from matplotlib import pyplot as plt
import tbapy

import CMRcalc

# Application through The Blue Alliance

'''
Credit:

Powered by The Blue Alliance
https://www.thebluealliance.com/

Queries handled through tbapy, courtesy of FRC Team 1418
https://github.com/frc1418/tbapy
'''

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
    teams = reds[0:2] + blues[0:2]
    return CMRcalc.Match(teams, score_r, score_b)

def get_event_results(tba_key, event, visual=True, verbose=False):
    '''
    Returns the CMR of each team at a particular event

    Input:
    -event: string, official event designation
    -visual: bool, whether or not a histogram is displayed
    -verbose: whether or not each team's data is printed
    
    Output:
    -out: dict, {team_key, cmr}
    '''

    # Query and calculation
    tba = tbapy.TBA(tba_key)
    matches_tba = tba.event_matches(event, keys =True)
    matches = []
    for match_tba in matches_tba:
        match = tba.match(match_tba)
        matches.append(tba2cmr(match))
    teams = tba.event_teams(event, keys = True)
    cmrs = CMRcalc.calc_cmr(matches, len(teams))

    # Output
    out = {}
    for team, cmr in zip(teams, cmrs):
        out.update({team, cmr})
    if (verbose):
        print("Team\t  CMR")
        print("-------------")
        for team, cmr in zip(teams, cmrs):
            print("%s\t%s" %(team, round(cmr, 2)))

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
        new_match = CMRcalc.Match([match[0], match[1], match[2],
                          match[3], match[4], match[5] ],
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
    cmrs = CMRcalc.calc_cmr(matches, team_count)
    if (verbose):
        print("OPR\t  CMR")
        print("-------------")
        for opr, cmr in zip(oprs, cmrs):
            print("%s\t%s" %(round(opr, 2), round(cmr, 2)))
    if (visual):
        plt.plot(oprs, cmrs, "bo")
        plt.show()
    return cmrs
