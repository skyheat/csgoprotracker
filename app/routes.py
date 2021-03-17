import requests
import os

from app import app
from flask import render_template
from faceit_data import FaceitData
from flask import url_for
from flask import request
from flask import redirect

#Goes through every 'pro league hub', maybe look at esea later?

#apikey
apikey = os.getenv("API_KEY", "optional-default")
faceit_data = FaceitData(apikey)
#hub_details = faceit_data.hub_details("74caad23-077b-4ef3-8b1d-c6a2254dfa75")
match_details = faceit_data.match_details("1-7b3783a4-a7ca-40ae-97aa-c3153ee53ed9")
#FPL NA
#748cf78c-be73-4eb9-b131-21552f2f8b75
#FPL EU
#74caad23-077b-4ef3-8b1d-c6a2254dfa75

@app.route("/")
@app.route("/index")
def index():
    euhub_matches = faceit_data.hub_matches("74caad23-077b-4ef3-8b1d-c6a2254dfa75", "past", 0, 20)
    nahub_matches = faceit_data.hub_matches("748cf78c-be73-4eb9-b131-21552f2f8b75", "past", 0, 20)
    #print(match_details['match_id'])
    #print(match_details['teams']['faction1']['roster'][0]['nickname'])
    team1 = []
    team2 = []
    matches = []
    matchesNA = []
    teamNames = []
    teamNamesNA= []
    for i in euhub_matches['items']:
        #print(i['match_id'])
        if(i['status'] != "CANCELLED"): 
            teamname1 = i["teams"]["faction1"]["name"]
            teamname2 = i["teams"]["faction2"]["name"]
            temp = [teamname1, teamname2]
            teamNames.append(temp)
            matches.append(i['match_id'])
        else:
            continue
    for i in nahub_matches['items']:
        #print(i['match_id'])
        if(i['status'] != "CANCELLED"): 
            teamname1 = i["teams"]["faction1"]["name"]
            teamname2 = i["teams"]["faction2"]["name"]
            temp = [teamname1, teamname2]
            teamNamesNA.append(temp)
            matchesNA.append(i['match_id'])
        else:
            continue

    return render_template('index.html', title='Home', namesMatch=zip(teamNames, matches), namesMatchNA=zip(teamNamesNA, matchesNA))

@app.route("/search/", methods=["POST"])
def searchPlayer():
    playername = request.form['searchname']
    #print(playername)
    playerList = faceit_data.search_players(playername, 'csgo', None, 0, 5)
    #print(playerList)
    #print(faceit_data.search_players("GeT_RiGhT", 'csgo'))
    playerarray = []
    for i in playerList['items']:
        #print(i)
        playerarray.append(i)
        if(i['verified']):
            return redirect(url_for('player', playerid=i['player_id']))
    #print(playerarray)

    return render_template('search.html', title='Player Search', playername=playername, playerarray=playerarray)

@app.route("/match/<matchid>")
def match(matchid):
    #print(matchid)
    team1 = []
    team2 = []
    team1ids = []
    team2ids = []
    match_details = faceit_data.match_details(matchid)
    match_stats = faceit_data.match_stats(matchid)
    match_score = match_stats["rounds"][0]["round_stats"]["Score"]
    team1stats = []
    team2stats = []
    for i in match_details['teams']['faction1']['roster']:
        #print(i['nickname'])
        team1.append(i["nickname"])
        team1ids.append(i['player_id'])
    for i in match_details['teams']['faction2']['roster']:
        #print(i['nickname'])
        team2.append(i['nickname'])
        team2ids.append(i['player_id'])
    team1name = match_details['teams']['faction1']['name']
    team2name = match_details['teams']['faction2']['name']
    reordersample = ["Player", "Kills", "Assists", "Deaths", "K/R Ratio", "K/D Ratio", "Headshots", "Headshots %", "MVPs", "Triple Kills", "Quadro Kills", "Penta Kills"]
    team1len = len(match_stats['rounds'][0]['teams'][0]['players'])
    team2len = len(match_stats['rounds'][0]['teams'][1]['players'])
    count = 0
    count2 = 0
    for c in range(team1len):
        playerstats = match_stats['rounds'][0]['teams'][0]['players'][c]['player_stats']
       # print(playerstats)
        playerstats['Player'] = team1[count]
        #print(playerstats)
        reorderedstats = {k: playerstats[k] for k in reordersample}
        team1stats.append(reorderedstats)
        count = count+1
    for c in range(team2len):
        playerstats = match_stats['rounds'][0]['teams'][1]['players'][c]['player_stats']
        #print(playerstats)
        playerstats['Player'] = team2[count2]
        #print(playerstats)
        reorderedstats = {k: playerstats[k] for k in reordersample}
        #print(playerstats)
        team2stats.append(reorderedstats)
        count2 = count2 + 1
    team1stats = sorted(team1stats, key = lambda i: int(i['Kills']), reverse=True)
    team2stats = sorted(team2stats, key = lambda i: int(i['Kills']), reverse=True)
    #print(sorted(team2stats, key = lambda i: i['Kills'], reverse=True))

    #print(match_score)   
    #print(team1, team1stats)
    #print(team2, team2stats)
    demourl = match_details["demo_url"]
    #print(demourl[0])
    #reordered_dict = {k: sample_dict[k] for k in desired_order_list}
    #team1 = {'team1' : team1}
    #team2 = {'team2' : team2}
    #playername_stats1 = zip(team1, team1stats, team1ids), playername_stats2 = zip(team2, team2stats, team2ids)
    matchmap = match_details['voting']['map']['pick']
    matchmap = {"matchmap" : matchmap}
    

    return render_template("matchpage.html", title='Match Page', matchid=matchid, team1=team1, team2=team2, matchmap=matchmap, demourl=demourl, match_score=match_score,  playername_stats1 = zip(team1stats, team1ids), playername_stats2 = zip(team2stats, team2ids), team1name=team1name, team2name=team2name)

@app.route("/help")
def help():
    
    return render_template("help.html", title="Help")
    
@app.route("/player/<playerid>")
def player(playerid):
    #print(playerid)
    playername = faceit_data.player_id_details(playerid)['nickname']
    #print(playername)
    playermatches = faceit_data.player_matches(playerid, "csgo", None, None, 0, 20)
    #matchstats = faceit_data.match_stats()
    #playerstats = []
    matches = []
    matchmaps = []
    count = 0
    #print(playermatches)
    for i in playermatches['items']:
        if(i['competition_id'] == "74caad23-077b-4ef3-8b1d-c6a2254dfa75" or i['competition_id'] == "748cf78c-be73-4eb9-b131-21552f2f8b75"):
            try: 
                match_details = faceit_data.match_details(i['match_id'])
                matchmaps.append(match_details['voting']['map']['pick'])
                matches.append(i['match_id'])
                count = count + 1
            except KeyError:
                continue
    message = "User has no matches on FPL Pro Hubs"
    #print(matchmaps)
    #playerstats = {'playerstats' : playerstats}
    #playername = playerdetails['nickname']
    #playername = {'playername' : playername}
    #playerid = {'playerid' : playerid}
    #matches = {'matches' : matches}
    
    return render_template("playerpage.html", title='Player Page', playername=playername, match_map=zip(matches, matchmaps), message=message, count=count)
