import numpy as np
import random
from matplotlib import pyplot as plt

class Match:
    '''
    Represents FRC match data
    Data should be treated as immutable
    '''
    def __init__(self, teams, score_r, score_b):
        self.teams = teams
        self.red_teams = teams[0:2]
        self.blue_teams = teams[3:5]
        self.sr = score_r
        self.sb = score_b
        self.sn = (score_r - score_b)/(score_r + score_b)

    def to_str(self):
        out = "Red: %s, %s, %s " %(self.teams[0],self.teams[1],self.teams[2])
        out += "(%s)\n" %self.sr
        out+= "Blue: %s, %s, %s " %(self.teams[3],self.teams[4],self.teams[5])
        out += "(%s)\n" %self.sb
        return out

def calc_cmr(matches, team_count):
    '''
    Core algorithm to determine each team's Contribution to Match Result (CMR)
    The sum of your alliance's CMR minus the sum of your opponents' CMRs
    produces a match prediction, with 1 as a win and -1 as a loss.
    
    Inputs:
    -matches: list of Match objects
    -team_count: number of teams in data
    Output:
    -cmr: np array of each team's Contribution to Match Result
    '''
    # Calculate match matrix
    mat_matches = np.zeros((team_count, len(matches)))
    for team in range(team_count):
        for match, num in zip(matches, range(len(matches))):
            if team in match.red_teams:
                val = 1
            elif team in match.blue_teams:
                val = -1
            else:
                val = 0
            mat_matches[team, num] = val
    # Calculate score matrix
    mat_scores = []
    for match in matches:
        mat_scores.append(match.sn)
    mat_scores = np.array(mat_scores)
    # Calculate CMR
    mat_matches = np.transpose(mat_matches)
    return np.linalg.lstsq(mat_matches, mat_scores, rcond=None)[0]

# Testing
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
        new_match = Match([match[0], match[1], match[2],
                          match[3], match[4], match[5] ],
                          red_score, blue_score)
        matches.append(new_match)
    return matches

def test(team_count, match_count, visual=True):
    '''
    Simulates matches for each team to demonstrate the CMR calculation
    
    Inputs:
    -team_count: int, number of teams simulated
    -match_count: int, number of matches simulated
    -visual: bool, whether or not data is shown printed and graphically
    Outputs:
    -cmrs
    '''
    oprs = np.linspace(0, 100, team_count)
    matches = make_matches(oprs, match_count)
    cmrs = calc_cmr(matches, team_count)
    if (visual):
        print("OPR\t  CMR")
        print("-------------")
        for opr, cmr in zip(oprs, cmrs):
            print("%s\t%s" %(round(opr, 2), round(cmr, 2)))
        plt.plot(oprs, cmrs, "bo")
        plt.show()
    return cmrs
