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
	json p;
	p["Playlist"] = id;
	sendData(p);

	LOG("Playlist id saved");
}