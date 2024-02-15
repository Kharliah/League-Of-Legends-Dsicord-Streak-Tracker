import requests
import datetime
import csv
import os
import discord
import time 
import asyncio
bearer_token = '<Riot Token'

headers = {
    'X-Riot-Token':  bearer_token,
    'Content-Type': 'application/json'  # Adjust content type as needed
}

def getUser(username):
    url = 'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/'+username+ '/<Your Region or Tag here>' #like OCE or US etc
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return (data['puuid'])
    else:
        print("Error:", response.status_code)

Users = ["Joe", "Bob", "Feltman", "Kenny"]
players = {
    'Joe': '<puuid>',
    'Bob': '<puuid> ',
    'Kenny': '<puuid>',

}
#if getting IDs for the first time or everytime
#players = {}
#for user in Users:
#    players[user]= getUser(user)
streaks = {
                "Joe": -1
               , "Bob": 3
               , "Kenny": 1
               }
while(True): 
    Users = ["Joe", "Bob", "Feltman", "Kenny"]
    def getMatches(puuid):
        url = "https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/"+puuid+"/ids?start=0&count=2"
        try:
            response = requests.get(url, headers=headers)
        except Exception as e:
            print("shit fucked up RIP - the recent matches")
            return ""
        if response.status_code == 200:
            data = response.json()
            if(data):
                return [data[0]]
            else:
                return ""
        else:
            print("Error:", response.status_code)

    recentMatchId = {}
    for player,puuid in players.items():
        matchID = getMatches(puuid)
        recentMatchId[player] = matchID

    print(recentMatchId)

    #OC1_607839571

    def getMatchResult(matchID, Player):
        url = "https://sea.api.riotgames.com/lol/match/v5/matches/" + matchID #replace sea with whatever you are - check riot docos
        try:
            response = requests.get(url, headers=headers)
            print(Player)

        except Exception as e:
            print("shit fucked up RIP - match results")
            return "JESUS FUCK"
        
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
                gameType = "Go find it yourself. The ID is " + str(allInfo["queueId"]) + " https://static.developer.riotgames.com/docs/lol/queues.json"
            #print("Did we make it here?")
            fuck = int(allInfo["gameEndTimestamp"])
            milliseconds_timestamp = fuck
            seconds_timestamp = milliseconds_timestamp / 1000
            NormTime = datetime.datetime.fromtimestamp(seconds_timestamp)
            
            
            local_datetime = datetime.datetime.strptime(str(NormTime), "%Y-%m-%d %H:%M:%S.%f")
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
            isThereResult = getMatchResult(matchID[0], player)
            #print(str(cunt))
            if isThereResult:
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
                if row[0] == matchResults[item][0] and matchResults[item][8] != "Ultra Rapid Fire":
                    if row[1] != matchResults[item][1]:
                        print(matchResults[item][1] + " " +  row[1])
                        changes.append(item)
                    #else:
                    #    print("No changes! " + matchResults[item][0] + " " + matchResults[item][1] )
                        

    
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
                        print(str(streaks[i]) + " one")
                    elif streaks[i] > 0:
                        streaks[i] = streaks[i] + 1
                        print(str(streaks[i]) + " two")
                if matchResults[index][2] == "Lost":
                    if streaks[i] >= 0:
                        streaks[i] = -1
                        print(str(streaks[i]) + " three")
                    elif streaks[i] < 0:
                        streaks[i] = streaks[i] -1
                        print(str(streaks[i]) + " four")
        print(streaks)


        async def main():
            channel_id = "<Discord Channel ID>"
            message = (matchResults[index][0] + " " +  matchResults[index][2] +
           " a " + matchResults[index][8] + " at " + matchResults[index][3] + ". KDA: " +
           str(matchResults[index][5]) + "/" + str(matchResults[index][6]) + "/" + str(matchResults[index][7]) +
           ". Champion: " + matchResults[index][4] + ". Streak: " + str(streaks[matchResults[index][0]]))
            token = "<Discord Token>"
            await send_message_to_channel(channel_id, message, token)
            
        asyncio.run(main())
        if changes:
            with open('data.csv', 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(matchResults)
    time.sleep(300) 
            
        


    

