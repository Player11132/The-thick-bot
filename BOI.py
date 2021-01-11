import discord
import requests
import wikipedia
import json
import asyncio
from discord.ext import commands

import youtube_dl

import time
import datetime
from datetime import datetime 
from datetime import datetime
import random


f = open("BOT/config.json","r")#if the bot doesnt run be sure the config.json is in the same folder or that it hase the same name
config = json.load(f)
f.close()
bot_token = config["BOT_TOKEN"] 

thickresponses = [" THICK , GG!" , " NOT THICK , thats sad." , " in between.." , " too skinny , not THICK..." , " DAMN BOIIIII HE THICK!!"]
responses = ["Good,you?", "I AM THICK BOIIIIIIIIIIIIIIIIIIIIIIIIII","I am bored","I am bad,you...?","I don't know what I am doing with my life anymore" , "UwU" , "OwO" , "¯\_(ツ)_/¯","༼ つ ◕_◕ ༽つ vibing..."]
cats = ["Cat1.jpg","Cat2.jpg","Cat3.jpg","cat4.jpg"]

hostid = config["HostID"]


apikeyyoutube = config["ytapikey"]
apikeyimdb = config["imdbapikey"]

bot = commands.Bot(command_prefix='test ')
players = {}


@bot.event
async def on_ready():
    print("Bot online")

@bot.command(brief="Sends you info about the movie you searched")
async def imdb(ctx : commands.Context, *, keyword : str):
    if keyword == None or keyword == "" or keyword == " ":
        await ctx.send("Please enter a keyword to search a movie")
        return
    r = requests.get(f"https://www.omdbapi.com/?t={keyword}&apikey={apikeyimdb}")
    data = r.json()
    data["Response"] = data["Response"] == "True"

    if not data["Response"]:        
        await ctx.send(f'There was a problem with your search. The error that occured has the following message `{data["Error"]}`.')
        return

    embed = discord.Embed(
        title=data['Title'], 
        colour=discord.Colour(0x29b97f), 
        url=f"http://imdb.com/title/{data['imdbID']}", 
        description=data['Plot']
    )

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
        timestamp=datetime.datetime.fromisoformat(video_data["snippet"]["publishTime"].replace('Z', '+00:00'))
    )

    embed.set_image(url=video_data["snippet"]["thumbnails"]["high"]["url"])
    embed.add_field(
        name="Channel name", 
        value=f"[{video_data['snippet']['channelTitle']}](https://www.youtube.com/channel/{video_data['snippet']['channelId']})"
    )

    return embed

@bot.command(brief="Plays audio from youtube video using the given url")
async def youtube_url(ctx : commands.Context, youtubeUrl : str):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send('Not connected to a voice channel')
        return
    
    if ctx.voice_client.is_playing():
        await ctx.send('Audio already running')
        return

    with youtube_dl.YoutubeDL({"quiet": True}) as ydl:
        audio_url = ydl.extract_info(youtubeUrl, download=False)['formats'][0]['url']
        ctx.voice_client.play(discord.FFmpegPCMAudio(audio_url))

@bot.command(brief="Sends info of a steam game using its id (UNDER CONSTRUCTION)")
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

@bot.command(brief="Plays the audio of the video you searched")
async def youtubeaudio(ctx : commands.Context, *, keyword : str):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send('Not connected to a voice channel')
        return
    
    if ctx.voice_client.is_playing():
        await ctx.send('Audio already playing')
        return

    with youtube_dl.YoutubeDL({"quiet": True}) as ydl:
        video_info = ydl.extract_info(f"ytsearch:{keyword}", download=False)
        if video_info["entries"]:
            audio_url = video_info["entries"][0]['formats'][0]['url']
            ctx.voice_client.play(discord.FFmpegPCMAudio(audio_url))
        else:
            await ctx.send('No results for the search')

@bot.command(brief="Search youtube videos")
async def youtube(ctx : commands.Context, *, keyword : str):
    r = requests.get(f"https://www.googleapis.com/youtube/v3/search?q={keyword}&part=snippet&maxResults=1&type=video&key={apikeyyoutube}")
    data = r.json()

    if "error" in data:
        await ctx.send(f'There was a problem with your search. The error that occured has code `{data["error"]["code"]}` and the following message `{data["error"]["message"]}`.')
        return
    
    if data["items"]:
        #await ctx.send(f'Top {len(data["items"])} results for your search:')
        for video_data in data["items"]:
            await ctx.send(embed = generate_youtube_embed(video_data))
    else:
        await ctx.send(f'I could not find any results for your search.')

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

@bot.command(brief="Bot joins your voice channel")
async def join(ctx : commands.Context):
    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.send('I am already connected')
        return

    channel = ctx.author.voice.channel
    if channel:
        await channel.connect()
    else:
        await ctx.send('You are not connected to a voice channel')


@bot.command()
async def stop(ctx : commands.Context):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send('Not in a voice channel')
        return
    ctx.voice_client.stop()


@bot.command()
async def pause(ctx : commands.Context):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send('Not in a voice channel')
        return
    ctx.voice_client.pause()

@bot.command()
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

@bot.command(brief="Says if you are thick or not")
async def amITHICK(ctx:commands.Context):
    await ctx.send(f"Hello {ctx.author.name} you are{random.choice(thickresponses)}")

@bot.command(brief="Says how i am")
async def howareyou (ctx:commands.Context):
    await ctx.send(f"{random.choice(responses)}")

creatorid = 569187596844924949
@bot.command(brief="Makes bot ragequit")
async def close (ctx:commands.Context):
    if(ctx.author.id == creatorid or ctx.author.id ==hostid):
        if ctx.voice_client and ctx.voice_client.is_connected():
            await ctx.voice_client.disconnect()
        await ctx.send("Bye , you all not thick anymore :sob:")
        await bot.logout()
    else:
       await ctx.send("YOU NOT MY DAD!,GET AWAY FROM ME!")
    

@bot.command(brief="well , its in the name")
async def rickrollthechannel(ctx:commands.Context):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send('Not connected to a voice channel')
        return
    
    if ctx.voice_client.is_playing():
        await ctx.send('Audio already playing')
        return

    ctx.voice_client.play(discord.FFmpegPCMAudio("BOT_RESOURCES/rickroll.mp3"))

@bot.command(brief="it commits wikipedia")
async def wiki(ctx:commands.Context,*,keyword:str):
    page = wikipedia.search(keyword,1)
    if wikipedia.summary(page,5000)==None:
        await ctx.send(page)
        return
    await ctx.send(wikipedia.summary(page,5000))
    
bot.run(bot_token)
