# pzSSHDiscordUpdater
Allows a Discord bot to use an SSH connection to query a database and feed that info back to the bot; in this case, querying a project zomboid server for who's online.

NOTE: This bot will not work if you run it as-is. credentials.py must be changed to hold your login credentials and bot token, and the variables CHANNEL_ID_STRING, MESSAGE_ID_STRING and MODERATOR_ID_STRING must be changed to suit your needs. In theory you can just ignore the bot and use the return_active_players function for whatever it is you want to do with it!

