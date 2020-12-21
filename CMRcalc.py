import numpy as np

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
    -matches: list, Match objects
    -team_count: int, number of teams in data
    
    Output:
    -cmr: dict, {team, Contribution to Match Result}
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
        score_norm = (match.sr - match.sb)/(match.sr + match.sb)
        mat_scores.append(score_norm)
    mat_scores = np.array(mat_scores)
    # Calculate CMR
    mat_matches = np.transpose(mat_matches)
    out = np.linalg.lstsq(mat_matches, mat_scores, rcond=None)[0]
    return out.tolist()
