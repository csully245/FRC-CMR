import numpy as np
import random

class Match:
    '''
    Represents FRC match data
    Should be immutable
    '''
    def __init__(self, teams, score_r, score_b):
        self.teams = teams
        self.red_teams = teams[0:2]
        self.blue_teams = teams[3:5]
        self.sr = score_r
        self.sb = score_b
        if (score_r > score_b):
            self.sn = 1
        elif (score_r < score_b):
            self.sn = -1
        else:
            self.sn = 0
        #self.sn = (score_r - score_b) / score_r

    def to_str(self):
        out = "Red: %s, %s, %s " %(self.teams[0],self.teams[1],self.teams[2])
        out += "(%s)\n" %self.sr
        out+= "Blue: %s, %s, %s " %(self.teams[3],self.teams[4],self.teams[5])
        out += "(%s)\n" %self.sb
        return out

# Core Algorithm
def to_matrix(matches, team_count):
    '''
    Returns two matrices:
    - A logical matrix of which matches each team played
    - A matrix of the normalized score of each match
    '''
    # mat_matches
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
    # mat_scores
    mat_scores = []
    for match in matches:
        mat_scores.append(match.sn)
    mat_scores = np.array(mat_scores)

    return (np.transpose(mat_matches), mat_scores)

def algo(matches, scores):
    '''
    Returns the rating of each team
    Based on Least Squares solution
    https://blog.thebluealliance.com/2017/10/05/the-math-behind-opr-an-introduction/
    '''
    matches_t = np.transpose(matches)
    left_product = np.matmul(matches_t, matches)
    right_product = np.matmul(matches_t, scores)
    return np.linalg.solve(left_product, right_product)

# Testing
def make_matches(team_ratings, match_count):
    '''
    Returns a list of Matches, with randomized matchups and scores as the sum
    of team ratings.
    '''
    # Make matchups
    team_count = len(team_ratings)
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
        red_score = team_ratings[match[0]]
        red_score += team_ratings[match[1]]
        red_score += team_ratings[match[2]]
        blue_score = team_ratings[match[3]]
        blue_score += team_ratings[match[4]]
        blue_score += team_ratings[match[5]]
        new_match = Match([match[0], match[1], match[2],
                          match[3], match[4], match[5] ],
                          red_score, blue_score)
        matches.append(new_match)
    return np.transpose(matches)
        

def test(team_count=6, match_count=30):
    team_ratings = np.linspace(0, 100, team_count)
    matches = make_matches(team_ratings, match_count)
    mat_matches, mat_scores = to_matrix(matches, team_count)
    ratings = algo(mat_matches, mat_scores)
    print(ratings)
    for match in matches:
        print(match.to_str())

test(6, 10)
