#include "pch.h"
#include "MatchDataScraper.h"
#include <fstream>

using namespace std;
MatchDataScraper MDS;

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

    calcPlayerMMR(mmr, playlistID);
}

json MatchDataScraper::calcStreak(json jMMR, const std::string& safePID, int delta_a, int delta_b) {
    int wins = jMMR[safePID]["wins"];
    int losses = jMMR[safePID]["losses"];
    int streak = jMMR[safePID]["streak"];

    if (delta_b > delta_a) {
        wins++;
        if (streak >= 0) {
            streak++;
        }
        else {
            streak = 1;
        }
    }
    else if (delta_b < delta_a) {
        losses++;
        if (streak <= 0) {
            streak--;
        }
        else {
            streak = -1;
        }
    }

    jMMR[safePID]["wins"] = wins;
    jMMR[safePID]["losses"] = losses;
    jMMR[safePID]["streak"] = streak;

    return jMMR;
}

json MatchDataScraper::activeCheck(json& jMMR, const std::string& safePID) {
    for (auto& [key, value] : jMMR.items()) {
        if (key == safePID) {
            jMMR[key]["active"] = true;
        }
        else {
            jMMR[key]["active"] = false;
        }
    }
    return jMMR;
}

void MatchDataScraper::calcPlayerMMR(float mmr, int& playlistID) {
    std::string safePID = to_string(playlistID);
    json jMMR = getSavedPlayerMMR();

    if (jMMR[safePID].contains("start")) {
        jMMR[safePID]["end"] = mmr;

        float delta_a = jMMR[safePID]["delta"];
        float mmr_delta = jMMR[safePID]["end"].get<float>() - jMMR[safePID]["start"].get<float>();
        jMMR[safePID]["delta"] = mmr_delta;
        float delta_b = jMMR[safePID]["delta"];

        jMMR = calcStreak(jMMR, safePID, delta_a, delta_b);
    }
    else {
        jMMR[safePID]["start"] = mmr;
        jMMR[safePID]["end"] = mmr;
        jMMR[safePID]["delta"] = 0.0;
        jMMR[safePID]["wins"] = 0;
        jMMR[safePID]["losses"] = 0;
        jMMR[safePID]["streak"] = 0;
    }

    jMMR = activeCheck(jMMR, safePID);

    writePlayerMMR(jMMR);
}

void MatchDataScraper::writePlayerMMR(const json& jMMR) {

    if (mmrData["MMR"] != jMMR) {
        mmrData["MMR"] = jMMR;
        sendData(jMMR);
    }

    LOG("Player MMR saved");
}