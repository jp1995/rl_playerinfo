#pragma once

#include "bakkesmod/plugin/bakkesmodplugin.h"
#include "bakkesmod/plugin/pluginwindow.h"
#include "bakkesmod/plugin/PluginSettingsWindow.h"
#include "version.h"
#include <boost/asio.hpp>
#include <boost/asio/ip/tcp.hpp>
#include <nlohmann/json.hpp>
#include <iostream>

constexpr auto plugin_version = stringify(VERSION_MAJOR) "." stringify(VERSION_MINOR) "." stringify(VERSION_PATCH) "." stringify(VERSION_BUILD);
using json = nlohmann::json;
using boost::asio::ip::tcp;

class MatchDataScraper : public BakkesMod::Plugin::BakkesModPlugin
{
	//Boilerplate
	void loadHooks();
	virtual void onLoad();
	virtual void onUnload();
	void handleCountdownStart(std::string eventName);

	std::unique_ptr<MMRNotifierToken> notifierToken;
	std::unordered_map<std::string, json> mmrData;
	int pidStorage = 69;
	json matchStorage;

	json getMatchData();
	void writeMatchData(json jsonstr);
	int getPlaylistID();
	void writePlaylistID(int idstring);
	void getPlayerMMR(UniqueIDWrapper id);
	void calcPlayerMMR(float mmr, int& playlistID);
	void writePlayerMMR(const json& jMMR);
	json activeCheck(json& jMMR, const std::string& safePID);
	json calcStreak(json jMMR, const std::string& safePID, int delta_a, int delta_b);
	json getSavedPlayerMMR();
	void sendData(const json& data);
	void asyncConnect(tcp::socket& socket, boost::asio::io_context& io_context);
	void asyncWrite(tcp::socket& socket, const std::string& json_string);
	void runIoContext(boost::asio::io_context& io_context);
	void runTimer(boost::asio::steady_timer& timer, boost::asio::io_context& io_context);
};

