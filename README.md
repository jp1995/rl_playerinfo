# rl_playerinfo

A rocket league session info tool that condenses interesting tracker data for all players in the match.

![output](https://cdn.discordapp.com/attachments/533998516876607511/1013614330308214814/unknown.png)

* Name is a link to the trackernetwork profile
* For every rank, the value after division is winstreak.
* Games is a sum of ranked games this season.
* IsInfluencer, IsPremium, IsSuspicious columns are hidden unless one of the players has a value of True.

## Installation

### Plugin
```
# Copy the plugin over the your bakkesmod folder
$ copy Plugin/PlayerNames.dll %AppData%\bakkesmod\bakkesmod\plugins

Then enable the plugin in bakkesmod PluginManager
```

### Script
Has been tested on python 3.10.

Currently needs chrome installed to run the webdriver (chromedriver).
```bash
# Clone the repo
$ git clone https://github.com/jp1995/rl_playerinfo

# Change your current directory to rl_playerinfo
$ cd rl_playerinfo

# Install required packages with pip
$ pip install -r requirements.txt
```

## Instructions
After installing, simply run the script.

`python main.py`

The client should then be available at http://127.0.0.1:5500/. It will fill once match data is received from the plugin.

#### Autorun

Alternatively, autorun the script when Rocket League is launched in Steam.
Add the following to launch options and modify accordingly.

`cmd /c start python "path_to_main.py" & cmd /c start /b "path_to_RocketLeague.exe" %command%`

Windows has some limitations when it comes to running things in parallel in a single cmd window (which is how %command% handles it). This solution can sometimes dump some *interesting* errors but everything appears to work nicely.

You could also run the script as a Windows service.

#### Database connection

If you want to save this data into your own database, configure `db_connect.py` to your liking and uncomment the relevant lines in the `main` function of `main.py`.

* The database push has a check to only do it for ranked game modes. This can be removed if you want to log casual games as well, but that can currently result in duplicate entries of players as one player leaves, a new player joins and all players are pushed into the database again. I could write more code to account for that, but I'm lazy and don't really care for casual logs.

## todo
The backend of this is pretty ape brained. 
* Ideally data would be passed from plugin to script over tcp, allowing the script to be run 24/7 on a RasPi or something
* Firefox webdriver support.
* Maybe another column for linked socials?
* Perhaps a session MMR tracker too?

