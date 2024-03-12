import requests
import datetime
import csv
import os
import discord
import time 
import asyncio
bearer_token = '<token>
headers = {
    'X-Riot-Token':  bearer_token,
    'Content-Type': 'application/json'  # Adjust content type as needed
}

def getUser(username):
    url = 'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/'+username+'/OCE'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return (data['puuid'])
    else:
        print("Error:", response.status_code)

Users = ["John", "Joe", "Jimothy", "James"]
players = {
    'John': 'b',
    'Joe': 'n',
    'Jimothy': 'M',
    'James': '4'

}
#if getting IDs for the first time or everytime
#players = {}
#for user in Users:
#    players[user]= getUser(user)
streaks = {
                "John": 0
               , "Joe": 0
               , "Jimothy": 0
               , "James": 0
               }
while(True): 
    Users = ["John", "Joe", "Jimothy", "James"] #this is needed later because I cant be bothered explaining why
    def getMatches(puuid):
        url = "https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/"+puuid+"/ids?start=0&count=2&type=ranked" #only get ranked games
        try:
            response = requests.get(url, headers=headers)
        except Exception as e:
            print("RIP - the recent matches")
            return ""
        if response.status_code == 200:
            data = response.json()
            if(data):
                return [data[0]]
            else:
                return ""
        else:
            return ""

    recentMatchId = {}
    for player,puuid in players.items():
        matchID = getMatches(puuid)
        recentMatchId[player] = matchID

    print(recentMatchId)

    #OC1_607839571

    def getMatchResult(matchID, Player):
        url = "https://sea.api.riotgames.com/lol/match/v5/matches/" + matchID
        try:
            response = requests.get(url, headers=headers)
            #print(Player)

        except Exception as e:
            print("RIP - match results")
            return ""
        
        if response.status_code == 200:
            # Process the response data
            data = response.json()
            allInfo = data["info"]
            if allInfo["queueId"] == 400:
                gameType = "Draft Pick"
            elif allInfo["queueId"] == 420:
                gameType = "Ranked Solo"
            elif allInfo["queueId"] == 430:
                gameType = "Blind Pick"
            elif allInfo["queueId"] == 440:
                gameType = "Ranked Flex"
            elif allInfo["queueId"] == 450:
                gameType = "ARAM"
            elif allInfo["queueId"] == 1900:
                gameType = "Ultra Rapid Fire"
            else:
                gameType = "Not found - The ID is " + str(allInfo["queueId"]) + " https://static.developer.riotgames.com/docs/lol/queues.json"
            #print("Did we make it here?")
            swearWord = int(allInfo["gameEndTimestamp"])
            milliseconds_timestamp = swearWord
            seconds_timestamp = milliseconds_timestamp / 1000
            shiza = datetime.datetime.fromtimestamp(seconds_timestamp)
            
            
            local_datetime = datetime.datetime.strptime(str(shiza), "%Y-%m-%d %H:%M:%S.%f")
            formatted_datetime = local_datetime.strftime("%d/%m/%Y %H:%M")
            participants = allInfo["participants"]

            
            for x in participants:
                for user in Users:
                    if x["riotIdGameName"] == Player:
                        #print("USER WAS: " +Player)
                        #Users.remove(user)
                        if x["win"]:
                            result = "Won"
                        else:
                            result = "Lost"
                        #print( x["riotIdGameName"] + " " + result + " at " +  str(local_datetime))
                        return ([x["riotIdGameName"], matchID, result, str(formatted_datetime), x["championName"], x["kills"], x["deaths"], x["assists"], gameType])
                    #print("Player: " + x["riotIdGameName"] + " Champion: " + x["championName"] + " Result: " + str(x["win"]))

            else:
                # If the request was unsuccessful, print the error code
                print("Error:", response.status_code)

    matchResults = []
    for player,matchID in recentMatchId.items():
        #print(player + " " + matchID[0])
        if matchID:
            brochacho = getMatchResult(matchID[0], player)
            if brochacho:
                matchResults.append(getMatchResult(matchID[0], player))


    #print(matchResults)
    if not os.path.exists('data.csv'):
        with open('data.csv', 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(matchResults)

    changes = []

    with open('data.csv', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        # Loop through each row in the CSV file
        for row in csv_reader:
            # Loop through each item in the list
            for item in range(len(matchResults)):
                # Check if the first and second columns match
                if matchResults[item][0]:
                    if row[0] == matchResults[item][0]:
                        if row[1] != matchResults[item][1]:
                            print(matchResults[item][1] + " " +  row[1])
                            changes.append(item)
                        

    
    async def send_message_to_channel(channel_id, message, token):
        intents = discord.Intents.default()
        typing = False  # Disable typing events for simplicity

        # Create a client instance with the specified intents
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            print(f'We have logged in as {client.user}')
            channel = client.get_channel(channel_id)
            await channel.send(message)
            await client.close()

        await client.start(token)
    
    for index in changes:

        for i in streaks.keys():
            #print(i)
            #print(matchResults[index][0])
            if i == matchResults[index][0]:
                print("Current streak is: " + str(streaks[i]))
                if matchResults[index][2] == "Won":
                    if streaks[i] <= 0:
                        streaks[i] = 1
                    elif streaks[i] > 0:
                        streaks[i] = streaks[i] + 1
                if matchResults[index][2] == "Lost":
                    if streaks[i] >= 0:
                        streaks[i] = -1
                    elif streaks[i] < 0:
                        streaks[i] = streaks[i] -1
        print(streaks)


        async def main():
            channel_id = CHANNEL_ID
            message = (matchResults[index][0] + " " +  matchResults[index][2] +
           " a " + matchResults[index][8] + " at " + matchResults[index][3] + ". KDA: " +
           str(matchResults[index][5]) + "/" + str(matchResults[index][6]) + "/" + str(matchResults[index][7]) +
           ". Champion: " + matchResults[index][4] + ". Streak: " + str(streaks[matchResults[index][0]]))
            token = "<Token>"
            await send_message_to_channel(channel_id, message, token)
            
        asyncio.run(main())
        if changes:
            with open('data.csv', 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(matchResults)
                    
    time.sleep(300) #Run every 5 minutes
