#include "pch.h"
#include "MatchDataScraper.h"
#include <nlohmann/json.hpp>
#include <fstream>

using namespace std;
using json = nlohmann::json;
extern MatchDataScraper MDS_S;

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
	this->loadHooks();

	notifierToken = gameWrapper->GetMMRWrapper().RegisterMMRNotifier(
		[this](UniqueIDWrapper id) {
			getPlayerMMR(id);
		}
	);

	std::string src = pluginDataDir();
	namespace fs = std::filesystem;
	if (!fs::is_directory(src) || !fs::exists(src)) {
		fs::create_directory(src);
	}
	writeDefaultSettings();
	settingsIntoVars();
	LOG("Plugin loaded");
}

void MatchDataScraper::onUnload() {
	LOG("Unloading plugin.");
}

void MatchDataScraper::handleCountdownStart(std::string eventName) {
	LOG("Countdown start detected");

	int id = getPlaylistID();
	if (id) {
		writePlaylistID(id);
	}

	json j = getMatchData();
	if (j.is_null()) { return; }

	int num_players = j["Match"]["players"].size();
	int maxplayers = j["Match"]["maxPlayers"];

	if (num_players == maxplayers and matchStorage != j and num_players != 0) {
		matchStorage = j;
		writeMatchData(j);
	}
}
