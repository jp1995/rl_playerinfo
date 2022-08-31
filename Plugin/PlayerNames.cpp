#include "pch.h"
#include "PlayerNames.h"
#include <iostream>
#include <fstream>
#include <filesystem>
#include <nlohmann/json.hpp>

using namespace std;
using json = nlohmann::json;


BAKKESMOD_PLUGIN(PlayerNames, "Get Player names in lobbies", plugin_version, PLUGINTYPE_FREEPLAY)

std::shared_ptr<CVarManagerWrapper> _globalCvarManager;

void PlayerNames::LoadHooks() {
	gameWrapper->HookEvent("Function GameEvent_TA.Countdown.BeginState", std::bind(&PlayerNames::HandleGameStart, this, std::placeholders::_1));
	gameWrapper->HookEvent("Function TAGame.GameEvent_Soccar_TA.OnAllTeamsCreated", std::bind(&PlayerNames::HandleGameStart, this, std::placeholders::_1));
}


void PlayerNames::onLoad() {
	_globalCvarManager = cvarManager;
	cvarManager->log("PlayerNames loaded!");
	this->LoadHooks();

	std::string src = PlugDir();
	namespace fs = std::filesystem;
	if (!fs::is_directory(src) || !fs::exists(src)) {
		fs::create_directory(src);
	}
}


std::string PlayerNames::PlugDir() {
	std::string appdata = getenv("AppData");
	std::string src = appdata + "\\bakkesmod\\bakkesmod\\data\\PlayerNames";

	return src;
}


std::string PlayerNames::NamesFile() {
	std::string src = PlugDir();
	std::string fileContents;

	std::getline(std::ifstream(src + "\\names.txt"), fileContents);

	return fileContents;
}


json PlayerNames::getPnames() {
	json j;
	json empty;

	ServerWrapper server = gameWrapper->GetCurrentGameState();
	if (server) {
		std::string matchID = server.GetMatchGUID();
		//if (!matchID) return empty;
		j["Match"]["matchID"] = matchID;

		int maxp = server.GetMaxTeamSize() * 2;
		//if (!maxp) return empty;
		j["Match"]["maxPlayers"] = maxp;

		GameSettingPlaylistWrapper playlist = server.GetPlaylist();
		if (!playlist) return empty;
		int playlistID = playlist.GetPlaylistId();
		j["Match"]["playlist"] = playlistID;

		ArrayWrapper pris = server.GetPRIs();
		//if (!pris) return empty;
		cvarManager->log("Online server found");

		for (PriWrapper pri : pris) {
			if (!pri) return empty;

			UniqueIDWrapper uidW = pri.GetUniqueIdWrapper();
			//if (!uidW) return;	// Can't nullcheck this?

			TeamInfoWrapper team = pri.GetTeam();
			if (!team) return empty;

			int teamindex = team.GetTeamIndex();
			std::string name = pri.GetPlayerName().ToString();
			int platform = uidW.GetPlatform();
			auto uid = uidW.GetUID();

			std::string uidString = std::to_string(uid);

			if (platform == 1) {
				j["Match"]["players"][uidString]["team"] = teamindex;
				j["Match"]["players"][uidString]["platform"] = platform;
			}
			else {
				j["Match"]["players"][name]["team"] = teamindex;
				j["Match"]["players"][name]["platform"] = platform;
			}
			
		}
		cvarManager->log("All data saved");
	}
	cvarManager->log("Returning json object");
	return j;
}


void PlayerNames::HandleGameStart(std::string eventName) {
	json j = getPnames();
	if (j.is_null()) return;

	if (j["Match"]["matchID"] == "") return;
	std::string matchID = j["Match"]["matchID"];

	int num_players = j["Match"]["players"].size();
	int maxplayers = j["Match"]["maxPlayers"];

	std::string fileContents = NamesFile();
	json existing = json::parse(fileContents);

	std::string oldid = existing["Match"]["matchID"];

	if (matchID != oldid and num_players == maxplayers) {
		std::string jsonstr = j.dump();

		cvarManager->log("New match detected, writing into file...");

		std::string src = PlugDir();
		ofstream file(src + "\\names.txt", std::ofstream::out);

		if (file.is_open()) {

			file << jsonstr;

		}
		file.close();
	}
}


void PlayerNames::onUnload() {
	LOG("PlayerNames unloaded.");
}
