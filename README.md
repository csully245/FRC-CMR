# FRC-Team-Analysis
Experimenting with new ways to analyze FIRST Robotics Competition teams

The goal of this project is to find a better way to analyze the performance of a team,
for the purpose of a key performance indicator (KPI) of on-field performance. An ideal
measure would have the following properties:

-Comparisons valid between different FRC games

-Comparisons valid between different teams

-Improvements in team ability are directly reflected in score

The current method for doing this is Caleb Sykes' modification to the Elo rating system.
However, this has a fatal flaw for my purposes. Each team starts each season with a
score based on their previous seasons. This means that two teams that perform identically
in a given year will have different scores, meaning the measure is not ideal for answering
the question, "How did we do this year?" One solution to this could be to start each team
off with the same score each season. This could work, but it has the unfortunate effect of
devaluing the early matches. If you beat a good team in your first match, it's still scored
as if you were equals. If you beat them once their score better reflects their ability, it's
worth more points. This means that teams are incorrectly valued at the beginning of the
season, and as a result, the scores throughout the season are slightly off.

A better algorithm would have some way of measuring the successes of a team based off the
final performance of the teams they played with and against. To do this, the algorithm
would need to be simultaneous, rather than iterated after each match. Linear algebra is
a natural solution. I referenced the following TBA article for the linear algebra basics:
https://blog.thebluealliance.com/2017/10/05/the-math-behind-opr-an-introduction/

My solution is based off the idea that each team contributes to the final result. In the
Offensive Power Rating (OPR) calculation, the contribution is measured by a direct score
for that particular game. This algorithm is very similar, but instead of calculating a 
contribution to a score, it calculates a contribution to whether the match was a win or
a loss. Future versions may instead calculate contributions based on the percent winning
margin. The advantage of this method is that wins and losses are universal between seasons
(with the potential exception of 2015), so a team's contribution to match result should
be directly comparable across seasons.
