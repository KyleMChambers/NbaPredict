"""
Created on Sat Jul 13 15:04:35 2019
Webscraping NBA Data from Basketball Reference and determining previous wins and homestreaks
"""
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
import pandas as pd
import numpy as np
from collections import defaultdict

url = 'https://www.basketball-reference.com/leagues/NBA_2021_games.html'

#old method
# response = requests.get(url)
# soup = BeautifulSoup(response.text, 'html.parser')
# table = soup.findAll('table')[0]

table_sched = pd.read_html(url, match='December Schedule')
#print(f'Total tables: {len(table_sched)}')
df = table_sched[0]

#Data cleanup - remove unnamed, rename away/homepts and create homewin
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df = df.rename(columns={"PTS":"VisitorPTS"})
df = df.rename(columns={"PTS.1":"HomePTS"})
df = df.rename(columns={"Home/Neutral":"HomeTeam"})
df = df.rename(columns={"Visitor/Neutral":"VisitorTeam"})

df["HomeWin"] = df["VisitorPTS"] < df["HomePTS"]
y_true = df["HomeWin"].values

#What's the baseline
n_games = df["HomeWin"].count()
n_homewins = df["HomeWin"].sum()
win_percentage = round(n_homewins / n_games, 3)
print(f"Home Win Percentage : {win_percentage}")

df["HomeLastWin"] = False
df["VisitorLastWin"] = False

from collections import defaultdict
won_last = defaultdict(int)

for index, row in df.iterrows():
    home_team = row["HomeTeam"]
    visitor_team = row["VisitorTeam"]
    row["HomeLastWin"] = won_last[home_team]
    row["VisitorLastWin"] = won_last[visitor_team]
    df.loc[index] = row
    #Set current win
    won_last[home_team] = row["HomeWin"]
    won_last[visitor_team] = not row["HomeWin"]

#Win streaks  -------------------------------------------------------  
df["HomeWinStreak"] = 0
df["VisitorWinStreak"] = 0

#Did the home and visitor teams win their last game
win_streak = defaultdict(int)

for index, row in df.iterrows():
    home_team = row["HomeTeam"]
    visitor_team = row["VisitorTeam"]
    row["HomeWinStreak"] = win_streak[home_team]
    row["VisitorWinStreak"] = win_streak[visitor_team]
    df.loc[index] = row
    #Set current win
    if row["HomeWin"]:
        win_streak[home_team] += 1
        win_streak[visitor_team] = 0
    else:
        win_streak[home_team] = 0
        win_streak[visitor_team] += 1


#DO NOT DELETE
#predictions using previous win--------------------------------------------------------
# from sklearn.tree import DecisionTreeClassifier
# clf = DecisionTreeClassifier(random_state=14)
# from sklearn.model_selection import cross_val_score
# X_previouswins = df[["HomeLastWin", "VisitorLastWin"]].values
# scores = cross_val_score(clf, X_previouswins, y_true, scoring = 'accuracy')
# print("Feature 1 Counting Previous Win: {0:.4}".format(np.mean(scores)))


#predictions using previous winstreak--------------------------------------------------
from sklearn.tree import DecisionTreeClassifier
clf = DecisionTreeClassifier(random_state=14)
from sklearn.model_selection import cross_val_score
X_winstreak = df[["HomeLastWin", "VisitorLastWin", "HomeWinStreak", "VisitorWinStreak"]].values
scores = cross_val_score(clf, X_winstreak, y_true, scoring = 'accuracy')
print("Feature 2- Counting WinStreaks: {0:.4f}".format(np.mean(scores)))

print(df.tail(10))