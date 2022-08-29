# rl_playerinfo

A rocket league session info tool that shows interesting information about the players in your game.

![output](https://cdn.discordapp.com/attachments/533998516876607511/1013598626955665458/unknown.png)

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
Has been tested on python 3.10
```bash
# Clone the repo
$ git clone https://github.com/jp1995/rl_playerinfo

# Change your current directory to rl_playerinfo
$ cd rl_playerinfo

# Install required packages with pip
$ pip install -r requirements.txt
```

## Instructions
After installing, simply run the `main.py` script.

`python `

The client should then be available at http://127.0.0.1:5500/. It will fill out once in game.

If you want to save this data into your own database, configure `db_connect.py` to your liking.

# Todo
The backend of this is pretty ape brained. 

Needs a rewrite to pass data from plugin to script over tcp, in json format. This should help clean the python script up too.

Do proper team separation (currently it's random).

Get playlist, do not fill table until all players present.

Maybe another column for linked socials?

