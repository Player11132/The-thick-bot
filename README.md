# The thick bot
 The thick bot its the amazing discord bot
 No need for admin permissions
 Open source
 FREE , wich ngl its A GREAT PRICE
 and made by Me aka Player11132
 Nice!
 But it would never be done without the help
 from dogerish, thank you!, dogerish.

## Python dependencies
 dependencies should be correctly listed in
 `require.txt` for easy installation with
 `pip3 install -r require.txt`

 In the case that this command finishes and
 BOI.py still has missing modules, please add it
 yourself and start a pull request or make an
 issue for it so we can.
 
## Bash script dependencies/notes
1. It's likely that these will only work on Linux.
2. Need `jq` installed for interpreting JSON files.
3. **Only for upload and logwatch**: Need `rclone` installed and set up with a google drive.
4. **Only for logwatch**: Need `inotify-tools` installed.

# Setup Workspace
 be sure there is a config.json file in the SAME folder with the bot
 it should look like this before you fill everything up:
 https://screenrec.com/share/lphzsiBS5T
 Now i suggest , for easy use to have Visual Studio Code 
 Get it here , it's free: https://code.visualstudio.com/
 Visual studio and Visual studio code IT'S NOT the same thing
 Now if you use visual studio code to open the folder go to :
 File>Open Folder or press Ctrl+K or Ctrl+O
 and open THE-THICK-BOT 
 Now we need to install some stuff 
 dont worry , no Web browser needed
 now we need to open a terminal
 if you are in Visual studio press Ctrl+` aka Ctrl+~ (its to the left from 1 on the keyboard)
 now wait for it to open
 good , now we need to type :
 pip install discord.py
 wait for it to install
 then another one
 pip install requests
 another one
 pip install youtube_dl
 and THE FINAL ONE , i think
 pip install wikipedia
 ok with all the magic stuff installed
 we can get to Setting up the bot`

# Setting up the bot:
 1. HOST ID
 To get your id got to : User Settings>Apearance>Avanced>DeveloperMode = ON
 Now that you have developer mode On you can get your ID by right clicking your avatar in a conversation or server list and select COPY ID , then paste it in the host ID
 replacing the old placeholder wich does not work
 2. IMDB API KEY
 Go to :
 https://www.omdbapi.com/apikey.aspx
 then select the FREE option
 fill the requiements
 you will get an email with the API key 
 It will look like this:
 https://screenrec.com/share/EnvuXowJke
 but first you must click on the Activate api key link
 After that just copy the api key from the Mail and paste it in
 the IMDB api key field in the config file
 Step 2 , done !
 3. Youtube API key
 Go to:
 https://console.developers.google.com/
 then click create new project
 after click enable apis and services
 after search for youtube data api V3 i think 
 and click add
 then on the left side there should be a panel
 click on credantials 
 and on top of the screen click create credantials 
 select api key and copy it
 after go in the config.json and paste the api key in the
 ytapikey field
 4.FFMPEG
 Go to this link to download ffmpeg
 https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z
 extract and in the bin folder should be FFMPEG.exe,
 copy that in the same folder as BOI
 5. The bot token 
 Go to:https://discord.com/developers/applications
 Click on new application name it customize it
 Then click on bot and add new bot and click on copy token
 And paste it in the bot token slot
 6. Adding the bot to a server
 On the same website(https://discord.com/developers/applications)
 click on OAuth2 go to the table and select the bot role and then
 click on copy under and paste it in the browser and thats is
 select the server and youre done with setting the bot up

 # Running the bot
 Well run the Bot , in visual studio
 there is a green arrow and click it
 and now add it to a server and say BOI help

 # Help and support
 you can either DM me or
 comment on the Github page 
 i will hopefully answer as soon as possible
 
 Thanks for using my bot
