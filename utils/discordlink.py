# import discord
# from discord.ext import commands
# from os import path
# import os
# import datetime as dt
# import pandas as pd
# import _thread as thread
# import asyncio
# #import locale
# # import WatchlistHandler as watchlist_handler
# # import WatchlistDiscordHandler as watchlist_discord_handler

# #locale.setlocale(locale.LC_ALL, 'en_US')



# UTOPIA = 679921845671035034
# REQUEST = 679929147107180550

# DEV_BOT_TOKEN = 'NzUzMzg1MjE1MTAzMzM2NTg4.X1laqA.vKvoV8Gz9jBWDWvIaBGDC4xbLB4'
# BOT_TOKEN = 'NzU0MDAyMzEwNTM5MTE2NTQ0.X1uZXw.urRh3pgMuS8IAfD4jAMbJVdO8D4'
# CREDS = DEV_BOT_TOKEN

# class DiscordLink:
#     def __init__(self):
#         try:
#             intents = discord.Intents.default()
#             intents.members = True
#             self.client = commands.Bot(command_prefix = '.', case_insensitive=True,  intents=intents)
#         except:
#             try:
#                 self.client = commands.Bot(command_prefix = '.', case_insensitive=True)
#             except RuntimeError as ex:
#                 print(ex)
#                 if "There is no current event loop in thread" in str(ex):
#                     self.loop = asyncio.new_event_loop()
#                     asyncio.set_event_loop(self.loop)
#                     self.client = commands.Bot(command_prefix = '.', case_insensitive=True)

#         # @client.event
#         # async def on_ready():
#         #     print("Real Bot is Ready")

#         thread.start_new_thread(self.client.run, (CREDS,))

#     async def send_to_test(self, msg):
#         server = self.client.get_guild(UTOPIA)
#         channel = server.get_channel(REQUEST)
#         #asyncio.run_coroutine_threadsafe(channel.send(msg), self.loop)
#         await channel.send(msg)

