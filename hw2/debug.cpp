#include <iostream>
#include "regex_lib.hpp"

int main() {
    RegexEngine engine;
    
    std::string regex = "";
    std::cin >> regex;
    
    try {
        Automaton dfa = engine.compile(regex);
        std::cout << "--------------------------\nпабеда\n";
    } catch (const std::exception& e) {
        std::cout << "\n" << e.what() << "\n";
    }
    
    return 0;
}