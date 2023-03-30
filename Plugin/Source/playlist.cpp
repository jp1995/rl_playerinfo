#include "pch.h"
#include "MatchDataScraper.h"
#include <fstream>

using namespace std;

int MatchDataScraper::getPlaylistID() {
	int menuID = 69;
	ServerWrapper server = gameWrapper->GetCurrentGameState();
	if (!server) return menuID;
	GameSettingPlaylistWrapper playlist = server.GetPlaylist();
	if (!playlist) return menuID;
	int playlistID = playlist.GetPlaylistId();
	return playlistID;
}

void MatchDataScraper::writePlaylistID(int id) {
	std::string src = pluginDataDir();

	ofstream file(src + "\\playlist.txt", std::ofstream::out);
	if (file.is_open()) {
		file << id;
	}
	file.close();

	json p;
	p["Playlist"] = id;
	sendData(p);

	LOG("Playlist id saved");
}