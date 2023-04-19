# rl_playerinfo

A rocket league session info tool that condenses interesting tracker data for all players in the match.

![output](https://cdn.discordapp.com/attachments/533998516876607511/1091743564150603847/new3.png)

* For every rank, the second value is winstreak.
* Games is a sum of ranked games this season.
* Usernames link to the trackernetwork profile
* Comes with a simple MMR tracker


## Installation

### Script

```bash
# Clone the repo
$ git clone https://github.com/jp1995/rl_playerinfo # or Code > Download ZIP
    
# Change your current directory to rl_playerinfo
$ cd rl_playerinfo

# Install required packages with pip.
$ pip install -r requirements.txt
```

Has been tested on python 3.10. Chrome or Firefox needs to be installed.

If you do not have python or pip installed, [refer to this article](https://www.dataquest.io/blog/install-pip-windows/) or use google.

### Plugin
```bash
# Copy the plugin over the your bakkesmod folder
$ copy Plugin/PlayerNames.dll %AppData%\bakkesmod\bakkesmod\plugins
```

Then enable the plugin in bakkesmod PluginManager (F2 > Plugins > Pluginmanager > tick the box).

## Instructions
After installing, simply run the script.

`python main.py`

The client should then be available at http://127.0.0.1:5500/. It will fill once match data is received from the plugin.
<hr style="margin-top: -10px;margin-bottom: -5px;width: 200px">

#### Autorun

Alternatively, autorun the script when Rocket League is launched in Steam.
Add the following to launch options and modify accordingly.

`cmd /c start python "path_to_main.py" & cmd /c start /b "path_to_RocketLeague.exe" %command%`

Windows has some limitations when it comes to running things in parallel in a single cmd window (which is how %command% handles it). This solution can sometimes dump some *interesting* errors but everything appears to work nicely.

You could also run the script as a Windows service.
<hr style="margin-top: -10px;margin-bottom: -5px;width: 200px">

#### Database connection

If you want to save this data into your own database, configure `db_connect.py` to your liking and uncomment the relevant lines in the `main` function of `main.py`.

* The database push has a check to only do it for ranked game modes. This can be removed if you want to log casual games as well, but that can currently result in duplicate entries of players as one player leaves, a new player joins and all players are pushed into the database again. I could write more code to account for that, but I'm lazy and don't really care for casual logs.
<hr style="margin-top: -10px;margin-bottom: -5px;width: 200px">

#### API disclaimer

The tracker network API is public, but there are some basic measures against scraping.
This may change. There's no official support or guarantees for future access.
API availability is decent, but sometimes requests fail. There can be instability during peak times, this can last for days.

## Functionality todo (maybe)

* The time it takes to generate the match table is pretty slow and there's a lot to optimize
* Some kind of caching system to not query the same player again during one match. In casual games players leave and join, this would help if API is not doing well.
* Save previous matches, add ability to view them in the client.
* MMR storage and merge should really happen in script, in case of a game crash.