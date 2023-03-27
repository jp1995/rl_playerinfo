#include "pch.h"
#include "MatchDataScraper.h"
#include <iostream>
#include <fstream>
#include <filesystem>
#include <nlohmann/json.hpp>

using namespace std;
using json = nlohmann::json;


BAKKESMOD_PLUGIN(MatchDataScraper, "Gather match data for rl_playerinfo", plugin_version, PLUGINTYPE_FREEPLAY)

std::shared_ptr<CVarManagerWrapper> _globalCvarManager;

void MatchDataScraper::loadHooks() {
	gameWrapper->HookEvent("Function GameEvent_TA.Countdown.BeginState", std::bind(&MatchDataScraper::handleCountdownStart, this, std::placeholders::_1));
	gameWrapper->HookEvent("Function TAGame.GFxData_MainMenu_TA.MainMenuAdded", std::bind(&MatchDataScraper::handleCountdownStart, this, std::placeholders::_1));}

std::string MatchDataScraper::pluginDataDir() {
	std::filesystem::path stream_src(gameWrapper->GetDataFolder() / "MatchDataScraper");
	std::string src_string = stream_src.generic_string();
	return src_string;
}

void MatchDataScraper::onLoad() {
	_globalCvarManager = cvarManager;
	cvarManager->log("Plugin loaded!");
	this->loadHooks();

	std::string src = pluginDataDir();
	namespace fs = std::filesystem;
	if (!fs::is_directory(src) || !fs::exists(src)) {
		fs::create_directory(src);
	}
	if (!fs::exists(src + "\\names.txt")) {
		std::ofstream file(src + "\\names.txt");
		file.close();
	}
	if (!fs::exists(src + "\\playlist.txt")) {
		std::ofstream file(src + "\\playlist.txt");
		file.close();
	}
	if (!fs::exists(src + "\\MMR.txt")) {
		std::ofstream file(src + "\\MMR.txt");
		file.close();
	}

	notifierToken = gameWrapper->GetMMRWrapper().RegisterMMRNotifier(
		[this](UniqueIDWrapper id) {
			getPlayerMMR(id);
		}
	);
}

void MatchDataScraper::onUnload() {
	std::string src = pluginDataDir();
	LOG("Unloading plugin.");
}

void MatchDataScraper::handleCountdownStart(std::string eventName) {
	LOG("Countdown start detected");

	int id = getPlaylistID();
	if (id) {
		writePlaylistID(id);
	}

	json j = getMatchData();
	if (j.is_null()) {
		return;
	}

	std::string matchID = j["Match"]["matchID"];
	int num_players = j["Match"]["players"].size();
	int maxplayers = j["Match"]["maxPlayers"];

	if (num_players == maxplayers) {
		writeMatchData(j);
	}
}
