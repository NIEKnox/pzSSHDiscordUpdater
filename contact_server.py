### Code written by NIEKnox on github, uploaded ~20:00 on 20th Nov 2024

### import packages
import discord
from ftplib import FTP
from credentials import ftp_port, ftp_address, ftp_password, ftp_username, log_channel_id, bot_token
from io import BytesIO
from datetime import datetime
from discord.ext import commands, tasks

### define functions
# get number of active players on server
def return_active_players(address, port, username, password):
    ### connect to server
    server = FTP(timeout = 3000)
    server.connect(address, port)
    server.login(username, password)

    # go to logs directory
    server.cwd("default/Logs/")
    # get list of files in Logs dir
    files_list = server.nlst()
    # find correct file by iterating through
    for file in files_list:
        if "user.txt" in file:
            file_name = file

    # read file
    r = BytesIO()
    server.retrbinary('RETR ' + file_name, r.write)
    loglines = r.getvalue().decode('utf-8')
    # get individual lines
    loglines = loglines.split(sep='\n')
    # filter for entry and exit queries
    entry_log = 'fully connected'
    exit_log = 'disconnected player'

    # get dicts of
    players_entered = {}
    players_left = {}
    for line in loglines:
        if entry_log in line:
            splitline = line.split("\"")
            player = str(splitline[1])
            if player not in players_entered:
                players_entered[player] = 1
            else:
                players_entered[player] += 1
        elif exit_log in line:
            splitline = line.split("\"")
            player = str(splitline[1])
            if player not in players_left:
                players_left[player] = 1
            else:
                players_left[player] += 1

    currently_on_server = []
    for player in players_entered:
        # if player hasn't left, player must still be online!
        if player not in players_left:
            currently_on_server.append(player)
        # if number of entering events greater than number of leaving events, player must be online
        elif players_entered[player] > players_left[player]:
            currently_on_server.append(player)
    return currently_on_server


# define intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)



print("Starting bot")

# run on startup
@bot.event
async def on_ready():  # do this when bot goes live
    print("on_ready just happened!")  # print statement
    log_channel = bot.get_channel(log_channel_id)  # get bot actions channel
    await log_channel.send("Kentuckybot is live!")  # tells bot actions channel that bot is live
    update_online.start()

current_players = None
current_time = None

# every minute, check who's online and update a given discord message with that info
@tasks.loop(minutes=1)
async def update_online():
    current_time = datetime.now().strftime('%H:%M')
    current_players = return_active_players(ftp_address, ftp_port, ftp_username, ftp_password)
    print(current_players)
    newcontent = "## Players online:\n"
    if len(current_players) == 0:
        newcontent += "None\n"
    else:
        for player in current_players:
            newcontent += player + "\n"
    newcontent += "\n**Last updated: **" + str(current_time) + " GMT "
    send_channel = bot.get_channel(CHANNEL_ID_STRING)  # channel id where the message from sendmsg exists
    message = await send_channel.fetch_message(MESSAGE_ID_STRING)  # message id of the message the bot sent after executing sendmsg
    await message.edit(content = newcontent)

# A command to get a bot to send a message; this will be important for the looping task
@bot.command(name='sendmsg', help='Initializes status message')
async def sendmsg(ctx):
    log_channel = bot.get_channel(log_channel_id)  # get bot actions channel
    send_channel = bot.get_channel(CHANNEL_ID_STRING)  # get send channel
    print(send_channel)
    user = ctx.author  # get user executing command
    user_id = user.id  # get user id of user executing command
    # if not admin then do not allow
    if user_id != MODERATOR_ID_STRING:
        await log_channel.send(str(user) + " executed the command !sendmsg.")
    else:
        await send_channel.send("Initializing status message...")

print(return_active_players(ftp_address, ftp_port, ftp_username, ftp_password))

bot.run(bot_token)
