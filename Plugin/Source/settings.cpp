#include "pch.h"
#include "MatchDataScraper.h"
#include <nlohmann/json.hpp>
#include <fstream>

MatchDataScraper MDS_S;
using json = nlohmann::json;
using namespace std;

void MatchDataScraper::writeDefaultSettings() {
    std::string src = pluginDataDir();
    json j;
    if (!std::filesystem::exists(src + "\\settings.txt")) {
        std::ofstream file(src + "\\settings.txt");
        j["script_device_ip"] = "localhost";
        file << j << std::endl;
        file.close();
    }
}

json MatchDataScraper::readSettings() {
    json j;
    std::string jstr;
    std::string src = pluginDataDir();
    std::ifstream file(src + "\\settings.txt");

    if (!file.is_open()) {
        LOG("Failed to open file: {}", src + "\\settings.txt");
        return j;
    }
    std::getline(std::ifstream(src + "\\settings.txt"), jstr);
    file.close();

    if (jstr.empty()) {
        return j;
    }
    j = json::parse(jstr);
    return j;
}

void MatchDataScraper::settingsIntoVars() {
    json j = readSettings();
    if (j.is_object() and !j.empty()) {
        MDS_S.script_device_ip = j["script_device_ip"];
        settingsIntoVarsDone = true;
    }
}

void MatchDataScraper::writeSettings(json j) {
    std::string src = pluginDataDir();
    if (std::filesystem::exists(src + "\\settings.txt")) {
        std::ofstream file(src + "\\settings.txt");
        file << j << std::endl;
        file.close();
    }
}

void MatchDataScraper::RenderSettings() {
    if (settingsIntoVarsDone == false) {
        settingsIntoVars();
    }

    ImGui::Spacing();
    ImGui::TextWrapped("Modify to run the script on an external machine. Port is static - *Bane voice* for now.");
    ImGui::Spacing();

    ImGui::Text("IP:");
    ImGui::SetCursorPosX(ImGui::GetCursorPosX() + 20);
    ImGui::SetCursorPosY(ImGui::GetCursorPosY() - 20);
    ImGui::PushItemWidth(200);

    static std::vector<char> buffer(MDS_S.script_device_ip.begin(), MDS_S.script_device_ip.end());
    buffer.resize(45);
    std::string inputText;
    ImGui::InputText("", buffer.data(), buffer.size(), ImGuiInputTextFlags_EnterReturnsTrue);

    ImGui::SetCursorPosX(ImGui::GetCursorPosX() + 230);
    ImGui::SetCursorPosY(ImGui::GetCursorPosY() - 24);
    static bool ipChanged = false;
    static float successMessageTimer = 0.0f;
    const float successMessageDuration = 3.0f;

    if (ImGui::Button("Enter")) {
        inputText = std::string(buffer.data());
        MDS_S.script_device_ip = inputText;
        json j = readSettings();

        if (j.is_object() and !j.empty()) {
            if (j["script_device_ip"] != MDS_S.script_device_ip) {
                LOG("New IP setting: {}", MDS_S.script_device_ip);
                j["script_device_ip"] = MDS_S.script_device_ip;
                writeSettings(j);
                settingsIntoVarsDone = false;
                ipChanged = true;
                successMessageTimer = ImGui::GetTime();
            }
        }
    }

    if (ipChanged) {
        ImGui::Text("Success!");
        if (ImGui::GetTime() - successMessageTimer > successMessageDuration) {
            ipChanged = false;
        }
    }
}