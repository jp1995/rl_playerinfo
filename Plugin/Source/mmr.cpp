#include "pch.h"
#include "MatchDataScraper.h"
#include <fstream>

using namespace std;
MatchDataScraper MDS;
std::string src = MDS.pluginDataDir();

json MatchDataScraper::getSavedPlayerMMR() {
	std::string fileContents;
	json jsonContents;

	std::getline(std::ifstream(src + "\\MMR.txt"), fileContents);
	if (fileContents.empty()) {
		return jsonContents;
	}
	jsonContents = json::parse(fileContents);
	return jsonContents;
}

void MatchDataScraper::getPlayerMMR(UniqueIDWrapper id)
{
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

	auto& results = j["MMR"][safePID]["results"];
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
    json jMMR = getSavedPlayerMMR();
    std::string safePID = to_string(playlistID);

    if (jMMR["MMR"][safePID].contains("start")) {
        jMMR["MMR"][safePID]["end"] = mmr;

        if (jMMR["MMR"][safePID].contains("delta")) {
            float delta_a = jMMR["MMR"][safePID]["delta"];
            float mmr_delta = jMMR["MMR"][safePID]["end"].get<float>() - jMMR["MMR"][safePID]["start"].get<float>();
            jMMR["MMR"][safePID]["delta"] = mmr_delta;
            float delta_b = jMMR["MMR"][safePID]["delta"];

            if (!jMMR["MMR"][safePID].contains("results")) {
                jMMR["MMR"][safePID]["results"] = nlohmann::json::array();
            }

            if (delta_b > delta_a) {
                std::string result = "win";
                jMMR["MMR"][safePID]["results"].push_back(result);
            }
            else if (delta_b < delta_a) {
                std::string result = "loss";
                jMMR["MMR"][safePID]["results"].push_back(result);
            }

        }
        else {
            float mmr_delta = jMMR["MMR"][safePID]["end"].get<float>() - jMMR["MMR"][safePID]["start"].get<float>();
            jMMR["MMR"][safePID]["delta"] = mmr_delta;

            if (mmr_delta > 0) {
                std::string result = "win";
                jMMR["MMR"][safePID]["results"].push_back(result);
            }
            else if (mmr_delta < 0) {
                std::string result = "loss";
                jMMR["MMR"][safePID]["results"].push_back(result);
            }
        }
    }
    else {
        jMMR["MMR"][safePID]["start"] = mmr;
        jMMR["MMR"][safePID]["delta"] = 0.0;
        jMMR["MMR"][safePID]["results"] = nlohmann::json::array();
    }

    int streak = calculateStreak(jMMR, safePID);
    jMMR["MMR"][safePID]["streak"] = streak;
    

    for (auto& [key, value] : jMMR["MMR"].items()) {
        if (key == safePID) {
            jMMR["MMR"][key]["active"] = true;
        }
        else {
            jMMR["MMR"][key]["active"] = false;
        }
    }

    ofstream file(src + "\\MMR.txt", std::ofstream::out);
    if (file.is_open()) {
        file << jMMR;
    }
    file.close();
    
    sendData(jMMR);

    LOG("Player MMR saved");
}