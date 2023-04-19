import json
import csv
import os
import statistics

path = "./signup.csv"

user_pool = []
teams = {}

sideOne = []
sideTwo = []

convert = {
    "Silver I": 100,
    "Silver II": 200,
    "Silver III": 300,
    "Silver IV": 400,
    "Silver Elite": 500,
    "Silver Elite Master": 700,
    "Gold Nova I": 800,
    "Gold Nova II": 900,
    "Gold Nova III": 1000,
    "Gold Nova Master": 1050,
    "Master Guardian I": 1100,
    "Master Guardian II": 1150,
    "Master Guardian Elite": 1200,
    "Distinguished Master Guardian": 1250,
    "Legendary Eagle": 1300,
    "Legendary Eagle Master": 1350,
    "Supreme Master First Class": 1400,
    "The Global Elite": 1450
}


def main():
    read_csv()
    test = create_teams(user_pool)
    teams.update({"Team {}".format(test[i][0]['name']): test[i] for i in range(len(test))})
    teamNames = sort_teams(teams)
    matchups(teamNames)

    print(json.dumps(sideOne, indent=4))
    print(json.dumps(sideTwo, indent=4))

def read_csv():
    with open(path, 'r') as f:
        flag = 0
        reader = csv.reader(f)
        for row in reader:
            if flag:
                convert_row_to_user(row)
            flag = 1
    

def convert_row_to_user(row):
    flag = 0
    if row[3] == 'NULL':
        elo = convert.get(row[4])
    else:
        elo = row[3]

    if row[0] == '':
        user_pool.append({
            "name": row[2],
            "elo": elo
        })
    else:
        add_to_team(row[0], row[2], elo)

def add_to_team(team, name, elo):
    if team not in teams:
        teams[team] = []
    teams[team].append({
        "name": name,
        "elo": elo
    })


# optimally create teams of 5 users with the highest average elo and lowest deviation
def create_teams(users):
    teams = []
    while len(users) >= 5:
        users.sort(key=lambda x: int(x["elo"]), reverse=True)
        groups = [users[i:i+5] for i in range(0, len(users), 5)]
        avg_dev = [(statistics.mean([int(u["elo"]) for u in g]), statistics.stdev([int(u["elo"]) for u in g])) for g in groups]
        best_group = min(avg_dev, key=lambda x: x[1])[0]
        teams.append([u for u in groups[avg_dev.index((best_group, min([x[1] for x in avg_dev])))]])
        users = [u for u in users if u not in teams[-1]]
    
    return teams

#get the average elo of each team, and the standard deviation of each team and add those as keys to the team dictionary 
# then sort the teams by average elo
# 
#
def sort_teams(teams):
    ordered_teams = []
    for team in teams:
        teams[team].sort(key=lambda x: int(x["elo"]), reverse=True)
        teams[team].append({
            "average_elo": statistics.mean([int(u["elo"]) for u in teams[team]]),
            "standard_deviation": statistics.stdev([int(u["elo"]) for u in teams[team]])
        })
    teams = sorted(teams.items(), key=lambda x: x[1][-1]["average_elo"], reverse=True)
    for team in teams:
        ordered_teams.append(team)
    for i in range(len(teams)):
        teams[i][1].append({
            "rank": i+1
        })
    return ordered_teams


#take lowest rated team, and the highest rated team and pair them against eachother.  Then pop the teams off the list, and then alternate bracket side
def matchups(teamNames):
    i = 0
    while len(teamNames) > 1:
        if i % 2 == 0:
            sideOne.append([
                {
                    "team": teamNames[0],
                },
                {
                    "team": teamNames[-1],
                }
            ])
            teamNames.pop(0)
            teamNames.pop(-1)
        else:
            sideTwo.append([
                {
                    "team": teamNames[0],
                },
                {
                    "team": teamNames[-1],
                }
            ])
            teamNames.pop(0)
            teamNames.pop(-1)
        i += 1
    

if __name__ == '__main__':
    main()