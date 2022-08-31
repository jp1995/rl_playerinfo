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

Currently needs chrome installed to run the webdriver.
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

The client should then be available at http://127.0.0.1:5500/. It will fill out once in game.

If you want to save this data into your own database, configure `db_connect.py` to your liking and uncomment the relevant line in the `main` function of `main.py`.

## todo
The backend of this is pretty ape brained. 
* Needs a rewrite to pass data from plugin to script over tcp.
* Firefox webdriver support.
* Maybe another column for linked socials?

Once the backend has been properly unfucked, could add a session MMR tracker too.

