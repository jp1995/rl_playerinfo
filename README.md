# rl_playerinfo

A Rocket League session info tool that condenses interesting tracker data for all players in the match.

![output](https://cdn.discordapp.com/attachments/533998516876607511/1091743564150603847/new3.png)

* Ranks are shown with division and winstreak.
* Games is a sum of ranked games played in the current season.
* Simple MMR tracker attached
* Responsive CSS (not extensively tested).

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

Has been tested on python 3.10.

If you do not have python or pip installed, [refer to this article](https://www.dataquest.io/blog/install-pip-windows/) or use google.

### Plugin
```bash
# Copy the plugin to your bakkesmod folder
$ copy Plugin/MatchDataScraper.dll %AppData%\bakkesmod\bakkesmod\plugins
```

Then enable the plugin in bakkesmod PluginManager (F2 > Plugins > Pluginmanager > tick the box).

## Instructions
After installing, simply run the script.

`python rlpi.py`

The client should then be available at http://127.0.0.1:5000/. It will fill once match data is received from the plugin. 

If you want to access the site from a separate device in your local network (like a phone), you need to replace the `127.0.0.1` part in the URL with the IP of the machine that is running the script.

## Wiki

![](https://cdn3.emoji.gg/emojis/2537-pepe-spell-book.gif)

[Go to wiki](https://github.com/jp1995/rl_playerinfo/wiki)

If you want to run this on Linux, [this part](https://github.com/jp1995/rl_playerinfo/wiki/Linux-info) is a mandatory read!


## API disclaimer

The tracker network API is technically public, but there are some ~~basic~~ measures against scraping.
This may change. There's no official support or guarantees for future access.
API availability is generally very good. There can be instability during peak times, this has previously been an issue for days.

## Functionality todo (maybe)

* Requests through a python library. Hit a wall on that.
* Some kind of caching system to not query the same players again during a casual match when someone leaves/joins. It would be good to not ping the API more than necessary.
* MMR storage and merge should really happen in script, in case of a game crash.