#include "pch.h"
#include "MatchDataScraper.h"
#include <fstream>
#include <cctype>

using namespace std;

json MatchDataScraper::getMatchData() {
	json j;
	json empty;

	ServerWrapper server = gameWrapper->GetCurrentGameState();
	if (server) {
		LOG("Online server found");
		std::string matchID = server.GetMatchGUID();
		int maxp = server.GetMaxTeamSize() * 2;

		GameSettingPlaylistWrapper playlist = server.GetPlaylist();
		if (!playlist) return empty;
		int getbranked = playlist.GetbRanked();

		ArrayWrapper pris = server.GetPRIs();
		for (PriWrapper pri : pris) {
			if (!pri) return empty;
			UniqueIDWrapper uidW = pri.GetUniqueIdWrapper();
			TeamInfoWrapper team = pri.GetTeam();
			if (!team) return empty;

			int teamindex = team.GetTeamIndex();
			int platform = uidW.GetPlatform();
			auto uid = uidW.GetUID();

			std::string name = pri.GetPlayerName().ToString();
			std::string UIDstr = std::to_string(uid);
			std::string switchUIDstr = "";
			for (char c : UIDstr) {
				switchUIDstr += std::tolower(c);
			}

			if (platform == 1) {
				j["Match"]["players"][UIDstr]["team"] = teamindex;
				j["Match"]["players"][UIDstr]["platform"] = platform;
			}
			else if (platform == 7 or platform == 4) {
				j["Match"]["players"][switchUIDstr]["team"] = teamindex;
				j["Match"]["players"][switchUIDstr]["platform"] = platform;
			}
			else {
				j["Match"]["players"][name]["team"] = teamindex;
				j["Match"]["players"][name]["platform"] = platform;
			}
		}
		j["Match"]["matchID"] = matchID;
		j["Match"]["maxPlayers"] = maxp;
		j["Match"]["isRanked"] = getbranked;
	}
	LOG("Data gathered, returning json object");
	return j;
}

void MatchDataScraper::writeMatchData(json arr) {
	std::string jsonstr = arr.dump();

	sendData(arr);

	LOG("Match data saved");
}