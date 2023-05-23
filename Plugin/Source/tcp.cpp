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
    auto io_context = std::make_shared<boost::asio::io_context>();
    tcp::socket socket(*io_context);
    asyncConnect(socket, io_context, json_string);

    std::thread ioThread([&]() {
        io_context->run();
    });

    if (ioThread.joinable()) {
        ioThread.join();
    }
}

void MatchDataScraper::asyncConnect(tcp::socket& socket, std::shared_ptr<boost::asio::io_context> io_context, const std::string& json_string) {
    tcp::resolver resolver(*io_context);
    tcp::resolver::query query(MDS_S.script_device_ip, "8371");
    LOG("Connecting: {} - {}", MDS_S.script_device_ip, "8371");

    boost::asio::async_connect(socket, resolver.resolve(query),
        [&](const boost::system::error_code& error, const tcp::endpoint&) {
            if (!error) {
                // woop
                asyncWrite(socket, io_context, json_string);
            }
            else {
                LOG("Connection failed: {}", error.message());
            }
        });
}

void MatchDataScraper::asyncWrite(tcp::socket& socket, std::shared_ptr<boost::asio::io_context> io_context, const std::string& json_string) {
    boost::asio::async_write(socket, boost::asio::buffer(json_string),
        [&](const boost::system::error_code& error, std::size_t bytes_transferred) {
            if (!error) {
                // woop
                io_context->stop();
            }
            else {
                LOG("Write failed: {}", error.message());
            }
        });
}