#include "pch.h"
#include "MatchDataScraper.h"
#include <fstream>

using namespace std;
MatchDataScraper MDS;
std::string src = MDS.pluginDataDir();

json MatchDataScraper::getSavedPlayerMMR() {

    if (mmrData.empty()) {
        return json(); 
    }
    auto it = mmrData.find("MMR");
    if (it != mmrData.end()) {
        json mmr = it->second;
        return mmr;
    }

}

void MatchDataScraper::getPlayerMMR(UniqueIDWrapper id) {
	ServerWrapper server = gameWrapper->GetCurrentGameState();
	if (!server) return;
	GameSettingPlaylistWrapper playlist = server.GetPlaylist();
	if (!playlist) return;
	PlayerControllerWrapper pc = gameWrapper->GetPlayerController();
	if (!pc) { return; }
	PriWrapper pri = pc.GetPRI();
	if (!pri) { return; }

	int playlistID = playlist.GetPlaylistId();
	UniqueIDWrapper primaryID = pri.GetUniqueIdWrapper();

	float mmr = gameWrapper->GetMMRWrapper().GetPlayerMMR(primaryID, playlistID);

	writePlayerMMR(mmr, playlistID);
}

int MatchDataScraper::calculateStreak(json j, std::string safePID) {
	int streak = 0;
	bool lastResultWasWin = true;

	auto& results = j[safePID]["results"];
	if (results.size() > 0) {
		lastResultWasWin = (results[results.size() - 1] == "win");
	}

	for (int i = results.size() - 1; i >= 0; i--) {
		if ((results[i] == "win" && lastResultWasWin) || (results[i] == "loss" && !lastResultWasWin)) {
			streak++;
		}
		else {
			break;
		}
		lastResultWasWin = (results[i] == "win");
	}

	if (results.size() > 0) {
		if (results[results.size() - 1] == "loss" && !lastResultWasWin) {
			streak = -streak;
		}
		else if (results[results.size() - 1] == "win" && lastResultWasWin) {
			streak = +streak;
		}
	}

	return streak;
}

void MatchDataScraper::writePlayerMMR(float mmr, int& playlistID) {
    std::string safePID = to_string(playlistID);
    json jMMR = getSavedPlayerMMR();  

    if (jMMR[safePID].contains("start")) {
        jMMR[safePID]["end"] = mmr;

        if (jMMR[safePID].contains("delta")) {
            float delta_a = jMMR[safePID]["delta"];
            float mmr_delta = jMMR[safePID]["end"].get<float>() - jMMR[safePID]["start"].get<float>();
            jMMR[safePID]["delta"] = mmr_delta;
            float delta_b = jMMR[safePID]["delta"];

            if (!jMMR[safePID].contains("results")) {
                jMMR[safePID]["results"] = nlohmann::json::array();
            }
            if (delta_b > delta_a) {
                std::string result = "win";
                jMMR[safePID]["results"].push_back(result);
            }
            else if (delta_b < delta_a) {
                std::string result = "loss";
                jMMR[safePID]["results"].push_back(result);
            }
        }
        else {
            float mmr_delta = jMMR[safePID]["end"].get<float>() - jMMR[safePID]["start"].get<float>();
            jMMR[safePID]["delta"] = mmr_delta;

            if (mmr_delta > 0) {
                std::string result = "win";
                jMMR[safePID]["results"].push_back(result);
            }
            else if (mmr_delta < 0) {
                std::string result = "loss";
                jMMR[safePID]["results"].push_back(result);
            }
        }
    }
    else {
        jMMR[safePID]["start"] = mmr;
        jMMR[safePID]["delta"] = 0.0;
        jMMR[safePID]["results"] = nlohmann::json::array();
    }

    int streak = calculateStreak(jMMR, safePID);
    jMMR[safePID]["streak"] = streak;
    
    for (auto& [key, value] : jMMR.items()) {
        if (key == safePID) {
            jMMR[key]["active"] = true;
        }
        else {
            jMMR[key]["active"] = false;
        }
    }

    mmrData["MMR"] = jMMR;
    sendData(jMMR);

    LOG("Player MMR saved");
}