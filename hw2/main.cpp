#include <iostream>
#include "regex_lib.hpp"

int main() {
    std::string regex = ""; 
    std::cin >> regex;
    
    RegexEngine engine;
    Automaton dfa = engine.compile(regex);
    
    std::cout << dfa.toJson() << std::endl;
    
    return 0;
}