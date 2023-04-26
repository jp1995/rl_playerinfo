#include <iostream>
#include <boost/asio.hpp>
#include <boost/asio/ip/tcp.hpp>
#include "nlohmann/json.hpp"
#include "pch.h"
#include "MatchDataScraper.h"
#include <thread>

using boost::asio::ip::tcp;
using json = nlohmann::json;
MatchDataScraper MDS_TCP;

void MatchDataScraper::sendData(const json& data) {
    std::string json_string = data.dump();
    boost::asio::io_context io_context;
    tcp::socket socket(io_context);

    asyncConnect(socket, io_context);
    asyncWrite(socket, json_string);
    runIoContext(io_context);
}

void MatchDataScraper::asyncConnect(tcp::socket& socket, boost::asio::io_context& io_context) {
    tcp::resolver resolver(io_context);
    tcp::resolver::query query(MDS_TCP.script_device_ip, "8371");

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

// timer based polling of the io_context, data is written when ready
void MatchDataScraper::runIoContext(boost::asio::io_context& io_context) {
    boost::asio::steady_timer timer(io_context, boost::asio::chrono::milliseconds(10)); // polling interval
    runTimer(timer, io_context);
}

void MatchDataScraper::runTimer(boost::asio::steady_timer& timer, boost::asio::io_context& io_context) {
    std::function<void(const boost::system::error_code&)> poll_handler = [&](const boost::system::error_code& ec) {
        if (!ec) {
            io_context.poll();
            timer.expires_at(timer.expiry() + boost::asio::chrono::milliseconds(10)); // timer is reset
            timer.async_wait(poll_handler); // schedule next check
        }
    };
    timer.async_wait(poll_handler);
}