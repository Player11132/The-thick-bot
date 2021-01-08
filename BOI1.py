import discord
import requests
import wikipedia
from discord.ext import commands

import youtube_dl

import datetime
import random
from collections import OrderedDict

bot_token = "Nzk2MDM1MzMwNjYyMjAzNDYy.X_SDrA.9Q-z1WT1c4VV8eeHTc_OqJc4_dQ"
creatorid = 569187596844924949

thickresponses = [" THICK , GG!" , " NOT THICK , thats sad." , " in between.." , " too skinny , not THICK..." , " DAMN BOIIIII HE THICK!!"]
responses = ["Good,you?", "I AM THICK BOIIIIIIIIIIIIIIIIIIIIIIIIII","I am bored","I am bad,you...?","I don't know what I am doing with my life anymore" , "UwU" , "OwO" , "¯\_(ツ)_/¯","༼ つ ◕_◕ ༽つ vibing..."]
cats = ["Cat1.jpg","Cat2.jpg","Cat3.jpg","cat4.jpg"]

apikeyyoutube = "AIzaSyDWiUq5Yf5Hx99XGmO5tS9CJvwa-BYW-Ps"
apikeyimdb = "1658b05b"

bot = commands.Bot(command_prefix='BOI ')
players = {}

memenumber = 0

debuggin = False

@bot.event
async def on_active(ctx:bot.event):
    print("Bot online")

@bot.command()
async def imdb(ctx : commands.Context, *, keyword : str):
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

@bot.command(brief="Sends you a photo of a cat (OLD)")
async def cat(ctx:commands.Context):
    await ctx.send(file=discord.File(random.choice(cats)))
    await ctx.send("ᓚᘏᗢ cute!")

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

@bot.command(brief="Makes bot ragequit")
async def quit (ctx:commands.Context):
    if(ctx.author.id == creatorid):
        await ctx.send("Bye , you all not thick anymore :sob:")
        await bot.quit()
    else:
       await ctx.send("YOU NOT MY DAD!,GET AWAY FROM ME!")
    

@bot.command(brief="well , YOU WILL GET RICKROLLED BY A BOT NOOOB")
async def rickrollthechannel(ctx:commands.Context):
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send('Not connected to a voice channel')
        return
    
    if ctx.voice_client.is_playing():
        await ctx.send('Audio already playing')
        return

    ctx.voice_client.play(discord.FFmpegPCMAudio("rickroll.mp3"))

@bot.command()
async def youtubesong(ctx : commands.Context):
    url = "https://youtu.be/DLzxrzFCyOs"
    with youtube_dl.YoutubeDL() as ydl:
        audio_url = ydl.extract_info(url, download=False)['formats'][0]['url']
        ctx.voice_client.play(discord.FFmpegPCMAudio(audio_url))


@bot.command(brief="it commits wikipedia")
async def wiki(ctx:commands.Context,*,keyword:str):
    page = wikipedia.search(keyword,1)
    if wikipedia.summary(page,5000)==None:
        await ctx.send(page)
        return
    await ctx.send(wikipedia.summary(page,5000))
    
bot.run(bot_token)