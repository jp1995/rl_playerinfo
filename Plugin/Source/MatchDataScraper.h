#pragma once

#include "bakkesmod/plugin/bakkesmodplugin.h"
#include "bakkesmod/plugin/pluginwindow.h"
#include "bakkesmod/plugin/PluginSettingsWindow.h"
#include "version.h"
#include <nlohmann/json.hpp>

constexpr auto plugin_version = stringify(VERSION_MAJOR) "." stringify(VERSION_MINOR) "." stringify(VERSION_PATCH) "." stringify(VERSION_BUILD);
using json = nlohmann::json;

class MatchDataScraper : public BakkesMod::Plugin::BakkesModPlugin
{
	//Boilerplate
	void loadHooks();
	public: std::string pluginDataDir();
	virtual void onLoad();
	virtual void onUnload();
	void handleCountdownStart(std::string eventName);

	std::unique_ptr<MMRNotifierToken> notifierToken;

	json getMatchData();
	void writeMatchData(json jsonstr);
	int getPlaylistID();
	void writePlaylistID(int idstring);
	void getPlayerMMR(UniqueIDWrapper id);
	int calculateStreak(json j, std::string safePID);
	void writePlayerMMR(float mmr, int& playlistID);
	json getSavedPlayerMMR();
};

