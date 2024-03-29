from __future__ import unicode_literals
#Libraries
from discord.ext.commands import Bot
import discord
import requests
import wikipedia
import json
from discord.ext import commands
import youtube_dl
import time
from datetime import datetime 
import random
import os
import ffmpeg
from discord.utils import get 
from discord import FFmpegPCMAudio
import asyncio
from difflib import SequenceMatcher

# if the bot doesn't run be sure the config.json is in the resources folder named config and with the .json extension
with open("Resources/config.json","r") as f:
    config = json.load(f)
bot_token = config["BOT_TOKEN"] 

#Variables
hostid = config["HostID"]

url = ''

urls = []
index = 0
name = ''

apikeyyoutube = config["ytapikey"]
apikeyimdb = config["imdbapikey"]

bot = commands.Bot(command_prefix=config["BotPrefix"])

#Debug stuff

#Says when the bot is online
@bot.event
async def on_ready():
    print("Bot online")

# standardized error handling
@bot.event
async def on_command_error(ctx, err):
    # format and send basic error message
    e = lambda s, c='': ctx.send(":x: {0}{1}".format(s, f" `{c}`" if c else ''))
    t = type(err)
    if t == commands.CommandNotFound:
        return await e("Unknown Command", ctx.invoked_with)
    elif t == commands.BadArgument:
        return await e("Invalid argument", err.param)
    elif t == commands.TooManyArguments:
        return await e("Too many arguments")
    elif t == commands.MissingRequiredArgument:
        return await e("Missing argument(s)", err.param)
    else: raise err

# basic ping command mainly for testing purposes
@bot.command(brief="Send response time in milliseconds, mainly for testing purposes, for Debugging purposes")
async def ping(ctx):
    return await ctx.send("{0}ms".format(
        round((
            datetime.utcnow()
            - ctx.message.created_at
        ).total_seconds() * 1000))
    )

#Info and api stuff

@bot.command(brief="Sends you info about the movie you searched")
async def imdb(ctx : commands.Context, *, keyword : str):
    #checks if you said a keyword
    if keyword == None or keyword == "" or keyword == " ":
        await ctx.send("Please enter a keyword to search a movie")
        return
    #requests data from imdb
    r = requests.get(f"https://www.omdbapi.com/?t={keyword}&apikey={apikeyimdb}")
    data = r.json()
    data["Response"] = data["Response"] == "True"

    #if it didn't get a response quit
    if not data["Response"]:        
        await ctx.send(f'There was a problem with your search. The error that occurred has the following message `{data["Error"]}`.')
        return

    #makes the embed
    embed = discord.Embed(
        title=data['Title'], 
        colour=discord.Colour(0x29b97f), 
        url=f"http://imdb.com/title/{data['imdbID']}", 
        description=data['Plot']
    )

    #assigns values to embed
    if "Poster" in data:
        embed.set_image(url=data['Poster'])
    embed.set_footer(text="- Data from OMDBApi")

    embed.add_field(name="Genres", value=data['Genre'])
    embed.add_field(name="Actors", value=data['Actors'])
    embed.add_field(name="Rating", value=f"{data['imdbRating']} :star:", inline=True)
    embed.add_field(name="Country", value=data['Country'], inline=True)
    embed.add_field(name="Language", value=data['Language'], inline=True)
    embed.add_field(name="Release Date", value=data['Released'], inline=True)
    embed.add_field(name="Runtime", value=data['Runtime'], inline=True)

    await ctx.send(embed=embed)

def generate_youtube_embed(video_data : dict):
    embed = discord.Embed(
        title=video_data['snippet']['title'], 
        colour=discord.Colour(0xd0021b), 
        url=f'https://youtu.be/{video_data["id"]["videoId"]}', 
        description=video_data["snippet"]["description"], 
        timestamp=datetime.fromisoformat(video_data["snippet"]["publishTime"].replace('Z', '+00:00'))
    )

    embed.set_image(url=video_data["snippet"]["thumbnails"]["high"]["url"])
    embed.add_field(
        name="Channel name", 
        value=f"[{video_data['snippet']['channelTitle']}](https://www.youtube.com/channel/{video_data['snippet']['channelId']})"
    )

    return embed

@bot.command(brief="it commits wikipedia")
async def wiki(ctx:commands.Context,*,keyword:str):
    search = keyword
    suggestion = wikipedia.suggest(keyword)
    if SequenceMatcher(None, keyword, suggestion).ratio()>0.5 and not suggestion==None:
        search = suggestion
        print("Suggestion more acurate")
    else:
        search = wikipedia.search(search,1)

    print(suggestion,search,keyword,wikipedia.search(search,1))

 # try to send the summary, if there is an ambiguous case, pick the first page
    try:
        if len(wikipedia.summary(search))<=2000:
            await ctx.send(wikipedia.summary(search))
        else:
            await ctx.send(wikipedia.summary(search,10))
            await ctx.send(f"For more information visit:\n{wikipedia.page(search).url}")
    except wikipedia.exceptions.DisambiguationError as e:
        await ctx.send(wikipedia.page(e.options[0]).summary)

@bot.command(brief="Credits")
async def Credits(ctx:commands.Context):
    embed = discord.Embed(title="Credits:", colour=discord.Colour(0xc72f3), description="The Creators of BOI", timestamp=datetime.utcfromtimestamp(1614665256))

    embed.set_image(url="https://media.discordapp.net/attachments/781470236548792330/786876795278196766/Thanks.gif?format=png&width=400&height=200")
    embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/725050767102443632/d065f33326a70bdcc274c178228bb0ba.png?size=128")
    embed.set_author(name="Player11132", icon_url="https://cdn.discordapp.com/avatars/569187596844924949/43f1d6dc57521dd71576bc445cd32b68.png?size=128")
    embed.set_footer(text="Player11132 2021 all right reserved lol", icon_url="https://cdn.discordapp.com/avatars/796035330662203462/5f47b9fcaa61e5d16df6b4da7d1527c5.png?size=128")

    embed.add_field(name="Player11132#7328", value="Programmer of the bot itself",inline=False)
    embed.add_field(name="dogerish#1469", value="Absolute chad ,host of the Bot and helper\n(couldn't do it without him)",inline=False)
    embed.add_field(name="Thank you for using", value="BOI the amazing discord bot", inline=False)
    await ctx.send(embed=embed)

@bot.command(brief="Sends info of a steam game using its id")
async def steam_info_id(ctx : commands.Context, id : str):
    if(id.isdigit()):
        id = int(id)
        r = requests.get(f"https://store.steampowered.com/api/appdetails?appids={id}")
        game_data = r.json()[str(id)]
        if not game_data['success']:
            await ctx.send(f'Searched game does not exist')
            return
        
        game_data = game_data["data"]

        price = "Free"

        if not game_data['is_free']:
            price = game_data["price_overview"]["final_formatted"]
            if game_data['price_overview']['initial_formatted'] != "":
                price = f"~~{game_data['price_overview']['initial_formatted']}~~ {price}"

        embed = discord.Embed(
            title=game_data["name"], 
            colour=discord.Colour(0x5176b), 
            url=f"https://store.steampowered.com/app/{game_data['steam_appid']}/", 
            description=game_data["short_description"]
        )
    else:
        await ctx.send("Enter valid ID,make sure there are only numbers")

    embed.set_image(url=game_data["header_image"])
    embed.set_footer(text="Steam API", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/200px-Steam_icon_logo.svg.png")

    embed.add_field(name="Price", value=price, inline=True)
    embed.add_field(name="Category", value=game_data["categories"][0]["description"], inline=True)

    await ctx.send(embed=embed)

@bot.command(brief="Search youtube videos")
async def youtube(ctx : commands.Context, *, keyword : str):
    r = requests.get(f"https://www.googleapis.com/youtube/v3/search?q={keyword}&part=snippet&maxResults=1&type=video&key={apikeyyoutube}")
    data = r.json()

    if "error" in data:
        await ctx.send(f'There was a problem with your search. The error that occurred has code `{data["error"]["code"]}` and the following message `{data["error"]["message"]}`.')
        return
    
    if data["items"]:
        for video_data in data["items"]:
            await ctx.send(embed = generate_youtube_embed(video_data))

@bot.command(brief="Sends random picture of a cat(NEW)")
async def catplz(ctx:commands.Context):
    data = requests.get("http://aws.random.cat/meow").json()

    embed = discord.Embed(title="ᓚᘏᗢ cute!")
    embed.set_image(url=data['file'])
    embed.set_footer(text="Do you like it?")

    await ctx.send(embed=embed)
    
@bot.command(brief="Sends random picture of dog")
async def dogplz(ctx:commands.Context):
        data = requests.get("https://random.dog/woof.json").json()
        embed = discord.Embed(title="Woof! Woof!")
        embed.set_image(url=data['url'])
        embed.set_footer(text="Do you like it?")

        await ctx.send(embed=embed)

#Audio stuff

#   --Audio utils

def is_supported(urls):
    extractors = youtube_dl.extractor.gen_extractors()
    for e in extractors:
        if e.suitable(urls) and e.IE_NAME != 'generic':
            return True
    return False

def youtubelinkgen(keyword):
    r = requests.get(f"https://www.googleapis.com/youtube/v3/search?q={keyword}&part=snippet&maxResults=1&type=video&key={apikeyyoutube}")
    data = r.json()
    
    if data["items"]:
        for video_data in data["items"]:
            global url
            url=f'https://youtu.be/{video_data["id"]["videoId"]}'
            return(True)
    else:
        return(False)

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'} 

FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

#  --Audio commands and logic

async def play_next(ctx):
    print(len(urls))
    voice = get(bot.voice_clients, guild=ctx.guild)
    urls.pop(0)
    print(len(urls))
    if len(urls) > 0:
        await playsong(ctx)
    else:
        await ctx.send("Queue ended")
        await voice.disconnect()
    
async def playsong(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    await ctx.send(f"Playing:{urls[0]['title']}")
    voice.play(FFmpegPCMAudio(urls[0]['url'], **FFMPEG_OPTIONS),after= lambda e:bot.loop.create_task(play_next(ctx)))

@bot.command(brief="Plays requested song")
async def play(ctx:commands.Context,*,keyword:str):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send("Connecting to voice channel...")
        if(ctx.message.author.voice is not None):
            channel = ctx.message.author.voice.channel
            voice = get(bot.voice_clients, guild=ctx.guild)
            if voice and voice.is_connected():
                await voice.move_to(channel)
            else:
                voice = await channel.connect()
        else:
            await ctx.send("You must be connected to a voice channel in order to use the play command")
            return

    if ctx.voice_client.is_playing():
        await ctx.send("Already playing, adding song to the queue")
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            if(youtubelinkgen(keyword)!=False):
                info = ydl.extract_info(url, download=False)
                if info not in urls:
                    urls.append(info)
                    await ctx.send(f"Song {info['title']} was succsessfully added to the queue \n {url}")
                else:
                    await ctx.send(f"Song {info['title']} is already in the queue")
            else:
                await ctx.send("Couldn't find song, try another keyword")
            return
    else:
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            if(youtubelinkgen(keyword)!=False):
                info = ydl.extract_info(url, download=False)
                urls.append(info)
            else:
                await ctx.send("Couldn't find song, try another keyword")
                return
        await playsong(ctx)

@bot.command  (brief="Plays next song in queue")
async def playnext(ctx:commands.Context):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    bot.loop.create_task(play_next(ctx))

#@bot.command()
#async def did_you_pay_your_taxes(ctx:commands.Context):
#    await ctx.send("Taxes, what taxes?")



#@bot.command()
#async def you_are_commiting_taxfraud(ctx:commands.Context):
#    await ctx.send("What is tax- \n THUMP THUMP THUMP \n Wtf? \n FBI OPEN UP \n AH FUCK THEY FOUND ME! \n PUT YO HAND IN THE AIR! \n NO FUCK YOU! \n YOU WILL NEVER TAKE ME ALIVE! \n *jumps from window and fucking dies*")

@bot.command(brief="Shows queue")
async def queue(ctx:commands.Context):
    if len(urls)-1==0:
        await ctx.send("Queue empty")
        await ctx.voice_client.disconnect()
        return

    for i in range(len(urls)):
        if i==0:
            await ctx.send(f"Playing now: {urls[i]['title']} \n In queue: \n")
        else:
            await ctx.send(str(i) + f". {urls[i]['title']}")

@bot.command(brief="Leaves voice chat")
async def leave(ctx:commands.Context):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send("Not in any voice chat")
        return
    await ctx.send("Leaving voice chat")
    voice = get(bot.voice_clients, guild=ctx.guild)
    await voice.disconnect()
    urls = []

@bot.command(brief="Pauses music")
async def pause(ctx:commands.Context):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send("Not in voice chat")
        return
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send("Music Paused")
    else:
        await ctx.send("Not playing any music")

@bot.command(breif="Resumes music")
async def resume(ctx:commands.Context):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send("Not in voice chat")
        return
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        await ctx.send("Alredy playing music")
    else:
        voice.resume()
        await ctx.send("Music resumed")

@bot.command(brief="well , its in the name")
async def rickroll(ctx:commands.Context):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        channel = ctx.author.voice.channel
        if channel:
            await channel.connect()
        else:
            await ctx.send('You are not connected to a voice channel')
    
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    ctx.voice_client.play(discord.FFmpegPCMAudio("Resources/rickroll.mp3"))

#IDK anymore section
@bot.command(brief="Says whenever you are thick or not")
async def amITHICK(ctx:commands.Context):
    await ctx.send(f"Hello {ctx.author.name} you are{random.choice(config['thickresponses'])}")

@bot.command(brief="Says how BOI feels")
async def howareyou (ctx:commands.Context):
    await ctx.send(f"{random.choice(config['responses'])}")

creatorid = 569187596844924949
@bot.command(brief="Makes bot ragequit")
async def shutdown (ctx:commands.Context):
    if(ctx.author.id == creatorid or ctx.author.id ==hostid):
        await ctx.send("Shutting down.")
        if ctx.voice_client or ctx.voice_client.is_connected():
            await ctx.voice_client.disconnect()
        for i in range(len(path)):
            os.remove(path[i])
        await bot.logout()
    else:
       await ctx.send("Only the creators and the host can shut me down.")

bot.run(bot_token)
