from __future__ import unicode_literals
#Libraries
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

# if the bot doesn't run be sure the config.json is in the resources folder named config and with the .json extension
with open("Resources/config.json","r") as f:
    config = json.load(f)
bot_token = config["BOT_TOKEN"] 

#Variables
hostid = config["HostID"]

url = ''

path = []
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
    page = wikipedia.search(keyword,1)
    if not len(page): await ctx.send(f"No results for `{keyword}`")
    else:
        # try to send the summary, if there is an ambiguous case, pick the first page
        try:
            await ctx.send(wikipedia.summary(page))
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
    embed.add_field(name="Hey,psst!Do you want Boi?", value="Go to: player11132.github.io",inline=False)
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
        await ctx.send("enter valid ID,make sure there are only numbers")

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

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    
}   

#  --Audio commands and logic

@bot.command(brief="Plays the audio of the video you searched,supports link")
async def play(ctx : commands.Context, *, keyword : str):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send('Not connected to a voice channel,connecting...')
        if ctx.voice_client and ctx.voice_client.is_connected():
            await ctx.send('I am already connected')

        channel = ctx.author.voice.channel
        if channel:
            await channel.connect()
        else:
            await ctx.send('You are not connected to a voice channel')
            return
    
    if ctx.voice_client.is_playing():
        await ctx.send('Song already playing, adding song to the queue')
        if(youtubelinkgen(keyword)!=False):
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                file = ydl.extract_info(url, download=True)
                path.append(str(file['title']) + "-" + str(file['id'] + ".mp3"))
                await ctx.send('Song successfully added to the queue')
                print(path)
        else:
            await ctx.send("The search returned no results.")
    else:
        with youtube_dl.YoutubeDL({"quiet": True}) as ydl:
            if(youtubelinkgen(keyword)!=False):
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    file = ydl.extract_info(url, download=True)
                    path.append(str(file['title']) + "-" + str(file['id'] + ".mp3"))
                    global name
                    name = str(file['title']) + "-" + str(file['id'] + ".mp3")

                await ctx.send('Now playing:'+path[0].rstrip('.mp3'))
                ctx.voice_client.play(discord.FFmpegPCMAudio(path[0]))
                print(path)
                


@bot.command(brief="If the music stopped use this command")
async def playnext(ctx:commands.Context):
    if len(path)!=0:
        if ctx.voice_client.is_playing():
            await ctx.send("Already playing! \n Use BOI skip to skip this song.")
        else:
            temp = path[0]
            path.pop(0)
            ctx.voice_client.play(discord.FFmpegPCMAudio(path[0]))
            await ctx.send('Now playing:'+path[0].rstrip('.mp3'))
            os.remove(temp)
    else:
        await ctx.send("Queue empty, add songs using the BOI play command")

@bot.command(brief="Pauses currently playing song")
async def pause(ctx : commands.Context):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send('Not in a voice channel')
        return
    ctx.voice_client.pause()

@bot.command(brief="Skips current song")
async def skip(ctx: commands.Context):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send('Not in a voice channel')
        return
    ctx.voice_client.stop()
    if(len(path)!=0):
        temp = path[0]
        path.pop(0)
        ctx.voice_client.play(discord.FFmpegPCMAudio(path[0]))
        await ctx.send("Skipped!")
        await ctx.send('Now playing:'+path[0].rstrip('.mp3'))
        os.remove(temp)
    else:
        await ctx.send("Queue empty")

@bot.command(brief="Shows queue")
async def queue(ctx : commands.Context):
    if(len(path)!=0):
        for i in range(len(path)):
            await ctx.send(str(i+1)+" "+str(path[i].rstrip('.mp3')))
    else:
        await ctx.send("Queue empty")

@bot.command(brief="Resumes the last downloaded song")
async def resume(ctx : commands.Context):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send('Not in a voice channel')
        return
    ctx.voice_client.resume()

@bot.command(brief="Leaves voice channel you are in , if its in it")
async def leave(ctx : commands.Context):
    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.voice_client.disconnect()
    else:
        await ctx.send('I am not connected to a voice channel')

#Shhhhhhhhh!
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
