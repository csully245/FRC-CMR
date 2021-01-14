# CMRcalc
Python module for calculating the Contribution to Match Result for *FIRST* Robotics Competition teams.
Chief Delphi post: https://www.chiefdelphi.com/t/analyzing-robot-performance-across-years/389981/1

Powered by TheBlueAlliance

https://www.thebluealliance.com/

## Setup
Non-native dependencies:
* tbapy
* numpy
* matplotlib

## Understanding CMR values
The purpose of CMRcalc is to provide a method of comparing robots across competitions and seasons, so that teams can directly compare their performance from year to year or measure themselves against other teams.
The core of the CMRcalc algorithm is to determine values for each team, so that if you add your alliance's CMR values and subtract your opponents', the result will be 100 (you win) or -100 (your opponent wins).
Due to the nature of this scoring system, half of all teams will have a negative CMR value. This does not mean those teams do not contribute to their alliance. It simply means that substituting that team with an "average" team within the context of the calculation would result in a more competitive alliance. What really matters is the comparison from one robot to another, not the true CMR value.

## Using CMRcalc
Each of the following functions calculate the CMRs of teams in a particular context. They return a dictionary with key `team####` and value CMR.
* `get_event_results(event, [visual], [verbose])` - Returns the CMR of each team with respect to a particular event
* `get_season_results(year, [visual], [verbose])` - Returns the CMR of each team with respect to a particular season
* `get_historic_results([visual], [verbose])` - Returns the CMR of all teams, with respect to all matches since 2002

To reduce the runtime, matches that have been requested in the past are stored locally and accessed directly, rather than requesting through the internet. If you want to download all the data, you can use the following function. Be warned that it may take a long time and a lot of space.
* `download_all_matches([show_time])` - Stores all TBA matches locally, 2002-present. If `[show_time]` is true, the download time in seconds will be printed

### Example:
Calculating FRC Team 245's result at the Troy District Event 2013
```
>>> import CMRcalc
>>> cmrs = CMRcalc.get_event_results("2013mitry", visual=False, verbose=False)
>>> cmrs["frc245"]
65.10150506649707
```

## Author
This software was created by Cate Sullivan.

https://www.linkedin.com/in/catherine-sullivan-7b2aa1156/
