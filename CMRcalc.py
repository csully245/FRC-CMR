import numpy as np

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

def calc_cmr(matches, team_keys):
    '''
    Core algorithm to determine each team's Contribution to Match Result (CMR)
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
