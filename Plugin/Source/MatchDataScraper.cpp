#include "pch.h"
#include "MatchDataScraper.h"
#include <nlohmann/json.hpp>

using namespace std;
using json = nlohmann::json;

BAKKESMOD_PLUGIN(MatchDataScraper, "Gather match data for rl_playerinfo", plugin_version, PLUGINTYPE_FREEPLAY)
std::shared_ptr<CVarManagerWrapper> _globalCvarManager;


void MatchDataScraper::loadHooks() {
	gameWrapper->HookEvent("Function GameEvent_TA.Countdown.BeginState", std::bind(&MatchDataScraper::handleCountdownStart, this, std::placeholders::_1));
	gameWrapper->HookEvent("Function TAGame.GFxData_MainMenu_TA.MainMenuAdded", std::bind(&MatchDataScraper::handleCountdownStart, this, std::placeholders::_1));}

void MatchDataScraper::onLoad() {
	_globalCvarManager = cvarManager;
	cvarManager->log("Plugin loaded!");
	this->loadHooks();

	notifierToken = gameWrapper->GetMMRWrapper().RegisterMMRNotifier(
		[this](UniqueIDWrapper id) {
			getPlayerMMR(id);
		}
	);
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

	if (num_players == maxplayers and matchStorage != j) {
		matchStorage = j;
		writeMatchData(j);
	}
}
