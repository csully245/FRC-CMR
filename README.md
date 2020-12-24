# CMRcalc

## Using CMRcalc
Each of the following functions calculate the CMRs of teams in a particular context. They return a dictionary with key `team####` and value CMR.
* `get_event_results(event, [visual], [verbose])` - Returns the CMR of each team with respect to a particular event
* `get_season_results(year, [visual], [verbose])` - Returns the CMR of each team with respect to a particular season
* `get_historic_results([visual], [verbose])` - Returns the CMR of all teams, with respect to all matches since 2002

###Example:
Calculating FRC Team 245's result at the Troy District Event 2013
`
import CMRcalc
>>> cmrs = CMRcalc.get_event_results("2013mitry")
>>> cmrs["frc245"]
65.10150506649707
`
To reduce the runtime, matches that have been requested in the past are stored locally and accessed directly, rather than requesting through the internet. If you want to download all the data, you can use the following function. Be warned that it may take a long time and a lot of space.
* `download_all_matches([show_time])` - Stores all TBA matches locally, 2002-present. If `[show_time]` is true, will print download time in seconds

