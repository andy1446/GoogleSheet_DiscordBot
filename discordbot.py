from distutils.log import error
import discord
from discord.ext import commands
from pprint import pprint
import httplib2
import os
from apiclient import discovery
import random
import asyncio
TOKEN = os.environ['TOKEN']
APIKey = os.environ['APIKEY']
SpreadsheetId = os.environ['SHEET_ID']
ReplySheetName = os.environ['REPLY_SHEET']
RoleSheetName = os.environ['ROLE_SHEET']
guildid = os.environ['GUILD_ID']
rolemessageid = os.environ['ROLE_MESSAGE_ID']

#Google API
discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
service = discovery.build(
    'sheets',
    'v4',
    http=httplib2.Http(),
    discoveryServiceUrl=discoveryUrl,
    developerKey=APIKey)

reactRange = RoleSheetName + '!A2:B'
rangeName = ReplySheetName + '!A2:D'

intent=discord.Intents.all()
client = commands.Bot(command_prefix = "!",intents=intent)




# 起動時呼叫
@client.event
async def on_ready():
    print('成功登入')

#添加身分組
@client.event
async def on_raw_reaction_add(payload):
    if str(payload.message_id) == rolemessageid:
        guild = client.get_guild(int(guildid))
        result = service.spreadsheets().values().get(
        spreadsheetId=SpreadsheetId, range=reactRange).execute()
        values = result.get('values', [])
        if not values:
            return
        for row in values:
            if payload.emoji.name == row[0]:
                role = discord.utils.get(guild.roles, name=row[1])
                if not role == None:
                    await payload.member.add_roles(role)

#移除身分組
@client.event
async def on_raw_reaction_remove(payload):
    if str(payload.message_id) == rolemessageid:
        guild = client.get_guild(int(guildid))
        result = service.spreadsheets().values().get(
        spreadsheetId=SpreadsheetId, range=reactRange).execute()
        values = result.get('values', [])
        if not values:
            return
        for row in values:
            if payload.emoji.name == row[0]:
                role = discord.utils.get(guild.roles, name=row[1])
                member = discord.utils.get(guild.members, id=payload.user_id)
                if not role == None:
                    await member.remove_roles(role)



# 收到訊息時呼叫
@client.event
async def on_message(message):
    
    # 送信者為Bot時無視
    if message.author.bot:
        return
    await client.process_commands(message)
    #私訊
    if message.guild == None:
        return
    result = service.spreadsheets().values().get(
    spreadsheetId=SpreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    if not values:
        return
    else:
        for row in values:
            if (message.channel.name == row[0] or row[0] == ''):
                keywords = row[1].split()
                check = True
                for keyword in keywords:
                    if not keyword in message.content:
                        check = False
                        break
                if check:
                    if message.author.nick == None:
                        username = message.author.name
                    else:
                            username = message.author.nick
                    if '<ban>' in row[2]:
                        await message.author.ban()
                    else:
                        if '<kick>' in row[2]:
                            await message.author.kick()
                        if '<delete>' in row[2]:
                            await message.delete()
                        else:
                            if '<reply>' in row[2]:
                                await message.reply(row[3].replace('<username>',username))
                            if '<replyrandom>' in row[2]:
                                msgs = row[3].split('|')
                                if len(msgs) != 0:
                                    index = random.randint(0, len(msgs)-1)
                                    await message.reply(msgs[index].replace('<username>',username))
                    if '<send>' in row[2]:
                        await message.channel.send(row[3].replace('<username>',username))
                    if '<sendrandom>' in row[2]:
                        msgs = row[3].split('|')
                        if len(msgs) != 0:
                            index = random.randint(0, len(msgs)-1)
                            await message.channel.send(msgs[index].replace('<username>',username))
                    return
 
#Game
    if message.content.startswith("!play"): #the play command to start the guessing game.
        channel = message.channel
        await channel.send("Choose a number between 1-10. Enter numerical values only.") #message that tells about the start of the game

        # generates a random number and turns it into a string
        number1 = random.randint(1,10)        
        number2 = str(number1)

        def check(m):
            return m.content == number2 and m.channel == channel 
        """
          The check function, first it checks if the message is the correct number.
          Then it checks if the channel is the same channel as the channel that the play command was sent in.
          If both is true, then it returns true. Else it returns false.
        """

        msg = await client.wait_for('message', check=check) #waits for the check function to return true
        await channel.send("Correct answer {.author}" .format(msg)) #sends the correct answer message
        return
              
  
# Bot起動
client.run(TOKEN)
