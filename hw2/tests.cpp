#include <gtest/gtest.h>
#include <nlohmann/json.hpp>
#include <fstream>
#include <random>
#include <regex>
#include <iostream>
#include <iomanip>

#include "regex_lib.hpp"

using json = nlohmann::json;

class RegexEngineTest : public ::testing::Test {
protected:
    RegexEngine engine;
};

// ==========================================
// 1. JSON Data
// ==========================================

class JsonParamTest : public ::testing::TestWithParam<json> {
protected:
    RegexEngine engine;
};

TEST_P(JsonParamTest, CheckJsonCase) {
    json data = GetParam();
    std::string regex_str = data["regex"];
    
    Automaton dfa;
    try {
        dfa = engine.compile(regex_str);
    } catch (const std::exception& e) {
        FAIL() << "Compilation error: " << e.what();
    }

    for (const auto& input : data["should_accept"]) {
        EXPECT_TRUE(match(dfa, input)) << "Regex: " << regex_str << " Input: " << input;
    }
    for (const auto& input : data["should_reject"]) {
        EXPECT_FALSE(match(dfa, input)) << "Regex: " << regex_str << " Input: " << input;
    }
}

std::vector<json> LoadJsonTests() {
    std::ifstream f("test_data.json");
    if (!f.is_open()) return {};
    json j;
    f >> j;
    std::vector<json> cases;
    for (const auto& item : j) cases.push_back(item);
    return cases;
}

INSTANTIATE_TEST_SUITE_P(
    JsonTests,
    JsonParamTest,
    ::testing::ValuesIn(LoadJsonTests()),
    [](const testing::TestParamInfo<json>& info) {
        std::string name = info.param["name"];
        std::replace_if(name.begin(), name.end(), [](char c){ return !isalnum(c); }, '_');
        return name;
    }
);

// ==========================================
// 2. Stress
// ==========================================

class FuzzTest : public ::testing::Test {
protected:
    RegexEngine engine;
    std::mt19937 gen{std::random_device{}()};
    
    std::string generateRandomRegex(int depth = 0) {
        if (depth > 2) { 
            return std::string(1, "ab"[std::uniform_int_distribution<>(0, 1)(gen)]);
        }
        int op = std::uniform_int_distribution<>(0, 3)(gen);
        switch (op) {
            case 0: return std::string(1, "ab"[std::uniform_int_distribution<>(0, 1)(gen)]);
            case 1: return generateRandomRegex(depth + 1) + generateRandomRegex(depth + 1);
            case 2: return "(" + generateRandomRegex(depth + 1) + "|" + generateRandomRegex(depth + 1) + ")";
            case 3: return "(" + generateRandomRegex(depth + 1) + ")*";
        }
        return "a";
    }

    std::string generateRandomString(int len) {
        std::string s;
        std::uniform_int_distribution<> dist(0, 1);
        for(int i=0; i<len; ++i) s += "ab"[dist(gen)];
        return s;
    }
};

TEST_F(FuzzTest, CompareWithStdRegex) {
    const int NUM_ITERATIONS = 10000; 
    const int STR_CHECKS_PER_REGEX = 20;
    const int MAX_STR_LEN = 10; 

    for (int i = 0; i < NUM_ITERATIONS; ++i) {
        std::string regexPattern = generateRandomRegex();
        
        std::cout << "Iter " << i << ": " << regexPattern << "\033[K\r" << std::flush;
        
        std::regex stdReg;
        try {
            stdReg = std::regex(regexPattern);
        } catch (...) {
            continue; 
        }

        Automaton myDfa;
        try {
            myDfa = engine.compile(regexPattern);
        } catch (...) {
            std::cout << "\n[CRASH] " << regexPattern << "\n";
            FAIL();
        }

        for (int j = 0; j < STR_CHECKS_PER_REGEX; ++j) {
            std::string text = generateRandomString(std::uniform_int_distribution<>(0, MAX_STR_LEN)(gen));
            
            bool stdResult = std::regex_match(text, stdReg);
            bool myResult = match(myDfa, text);

            if (stdResult != myResult) {
                std::cout << "\n[MISMATCH] Regex: " << regexPattern << " Input: " << text << "\n";
                FAIL();
            }
        }
    }
    std::cout << "\nDone.\n";
}

// ==========================================
// 3. JSON
// ==========================================

class JsonExportTest : public ::testing::Test {
protected:
    RegexEngine engine;
};

TEST_F(JsonExportTest, JsonStructureIsValid) {
    std::string regex = "a|b";
    auto dfa = engine.compile(regex);
    std::string jsonStr = dfa.toJson();

    json j;
    ASSERT_NO_THROW({
        j = json::parse(jsonStr);
    }) << "неверный json";

    std::vector<std::string> required_keys = {
        "states", "letters", "transition_function", "start_states", "final_states"
    };

    for (const auto& key : required_keys) {
        EXPECT_TRUE(j.contains(key)) << "JSON missing key: " << key;
    }
}

TEST_F(JsonExportTest, JsonLogicCorrectness_SimpleRegex) {
    auto dfa = engine.compile("a");
    json j = json::parse(dfa.toJson());

    EXPECT_EQ(j["letters"].size(), 1);
    EXPECT_EQ(j["letters"][0], "a");

    EXPECT_GE(j["states"].size(), 2);

    EXPECT_EQ(j["start_states"].size(), 1);
    std::string startNode = j["start_states"][0];

    bool foundTransition = false;
    std::string targetNode;
    for (const auto& trans : j["transition_function"]) {
        if (trans[0] == startNode && trans[1] == "a") {
            foundTransition = true;
            targetNode = trans[2];
            break;
        }
    }
    EXPECT_TRUE(foundTransition) << "нет перехода с начального состояния на a";

    bool isFinal = false;
    for (const auto& f : j["final_states"]) {
        if (f == targetNode) {
            isFinal = true;
            break;
        }
    }
    EXPECT_TRUE(isFinal) << "нужное состояние для a не финальное";
}

TEST_F(JsonExportTest, StrictFormatCompliance) {
    auto dfa = engine.compile("a");
    std::string output = dfa.toJson();

    EXPECT_NE(output.find("\"states\": ["), std::string::npos);
    EXPECT_NE(output.find("\"letters\": ["), std::string::npos);
    
    std::regex transitionPattern(R"(\[\s*"Q\d+",\s*"a",\s*"Q\d+"\s*\])");
    EXPECT_TRUE(std::regex_search(output, transitionPattern)) 
        << "неверный формат переходов";
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}