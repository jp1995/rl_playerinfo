// API dead, Rocket League dead, project dead //

# rl_playerinfo

A Rocket League session info tool that condenses interesting tracker data for all players in the match.

![output](https://cdn.discordapp.com/attachments/533998516876607511/1299088378259832932/new4.png?ex=671bedd5&is=671a9c55&hm=5c35f5d3d33754e8c582a7674e711afd7c764659768174ca5e588e65e25ab335&)

* Ranks are shown with division and winstreak.
* Games is a sum of ranked games played in the current season.
* Simple MMR tracker attached
* Responsive-ish CSS, API response caching, match history, DB integration.

## API disclaimer

The TN API for Rocket League is *technically* public, but there are measures against access.

This is due to a Psyonix policy against the hosting of third party APIs.
The current solution(s) works because the TN devs have not tried hard enough.
All this may change, or not. If you stumble upon this repo, it may be wise to not spread the word too much :)


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

Has been tested on python 3.10, 3.11.

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

If you want to access the site from a separate device in your local network (like a phone), you need to use the local IP that the script provides you.

## Wiki

![](https://cdn3.emoji.gg/emojis/2537-pepe-spell-book.gif)

[Go to wiki](https://github.com/jp1995/rl_playerinfo/wiki)

The wiki contains some extra information, for example how to enable the database integration.

If you want to run this on Linux, [this part](https://github.com/jp1995/rl_playerinfo/wiki/Linux-info) is a mandatory read!

## Functionality todo (maybe)

* Requests through a python library. It should be possible, but hit a wall on that.
* The C++ TCP client implementation is not ideal, with a 10 millisecond blocking action / connect.
* Launch options for database push / other things?
* The css is a bit of a mess.
