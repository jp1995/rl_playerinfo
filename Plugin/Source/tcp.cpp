#include <iostream>
#include <boost/asio.hpp>
#include <boost/asio/ip/tcp.hpp>
#include "nlohmann/json.hpp"
#include "pch.h"
#include "MatchDataScraper.h"
#include <thread>

using boost::asio::ip::tcp;
using json = nlohmann::json;
extern MatchDataScraper MDS_S;

void MatchDataScraper::sendData(const json& data) {
    std::string json_string = data.dump();
    boost::asio::io_context io_context;
    tcp::socket socket(io_context);

    asyncConnect(socket, io_context);

    boost::asio::steady_timer timer(io_context, std::chrono::milliseconds(10));
    // This is blocking, for less than 10ms. Unsure how to properly use io_context.poll(), 
    // which works on localhost but fails to connect over LAN.
    io_context.run_until(timer.expires_at());

    asyncWrite(socket, json_string);
}

void MatchDataScraper::asyncConnect(tcp::socket& socket, boost::asio::io_context& io_context) {
    tcp::resolver resolver(io_context);
    tcp::resolver::query query(MDS_S.script_device_ip, "8371");

    boost::asio::async_connect(socket, resolver.resolve(query),
        [&](const boost::system::error_code& error, const tcp::endpoint&) {
            if (!error) {
                // woop
            }
            else {
                LOG("Connection failed: {}", error.message());
            }
        });
}

void MatchDataScraper::asyncWrite(tcp::socket& socket, const std::string& json_string) {
    boost::asio::async_write(socket, boost::asio::buffer(json_string),
        [&](const boost::system::error_code& error, std::size_t bytes_transferred) {
            if (!error) {
                // woop
            }
            else {
                LOG("Write failed: {}", error.message());
            }
        });
}