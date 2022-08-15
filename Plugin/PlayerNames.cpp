#include "pch.h"
#include "PlayerNames.h"
#include <iostream>
#include <fstream>
#include <filesystem>
using namespace std;


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


std::map <std::string, int> PlayerNames::getPnames() {
	std::map <std::string, int> bindNames;
	std::map <std::string, int>::iterator pos;

	ServerWrapper server = gameWrapper->GetCurrentGameState();
	if (server) {
		ArrayWrapper pris = server.GetPRIs();

		for (PriWrapper pri : pris) {
			if (!pri) continue;

			UniqueIDWrapper uidW = pri.GetUniqueIdWrapper();
			//if (!uidW) { return; }	// Can't nullcheck this?

			std::string name = pri.GetPlayerName().ToString();
			int platform = uidW.GetPlatform();
			auto uid = uidW.GetUID();

			std::string uidString = std::to_string(uid); // Can't mix <string, int> and <int, int> in map

			if (platform == 1) {
				bindNames.insert(std::pair<std::string, int>(uidString, platform));
			}
			else {
				bindNames.insert(std::pair<std::string, int>(name, platform));
			}
		}
	}
	return bindNames;
}


void PlayerNames::HandleGameStart(std::string eventName) {
	std::map <std::string, int> bindNames = getPnames();
	std::string inputstr;
	for (std::pair<std::string, int>NamePlatPair : bindNames) {

		std::string name = NamePlatPair.first;
		int platform = NamePlatPair.second;
		std::string platString = std::to_string(platform);

		inputstr += name + ":" + platString + ",";

	}
	if (inputstr.length() > 0) {

		inputstr.erase(inputstr.length() - 1);
		std::string fileContents = NamesFile();

		if (fileContents != inputstr) {

			cvarManager->log("Old player names: " + fileContents);
			cvarManager->log("New player names: " + inputstr);
			cvarManager->log("Writing new values into file...");

			std::string src = PlugDir();
			ofstream file(src + "\\names.txt", std::ofstream::out);

			if (file.is_open()) {

				file << inputstr;

			}
			file.close();
		}
	}
}


void PlayerNames::onUnload() {
	LOG("PlayerNames unloaded.");
}
