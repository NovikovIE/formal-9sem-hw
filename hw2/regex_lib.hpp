#pragma once

#include <vector>
#include <string>
#include <stack>
#include <set>
#include <unordered_set>
#include <map>
#include <unordered_map>
#include <algorithm>
#include <queue>
#include <sstream>
#include <tuple>

struct Automaton {
    int startState = 0;
    int stateCount = 0;

    std::unordered_set<int> finalStates;

    std::vector<std::tuple<int, int, char>> transitions;
    std::vector<int> lookup;

    int addState() { 
        return stateCount++; 
    }
    void addTx(int u, int v, char c) { 
        transitions.emplace_back(u, v, c); 
    }

    void finalize() {
        lookup.assign(stateCount * 256, -1);
        for (const auto& [u, v, c] : transitions) {
            lookup[u * 256 + static_cast<unsigned char>(c)] = v;
        }
    }

    std::string toJson() const {
        std::stringstream ss;
        ss << "{\n  \"states\": [";
        
        for (int i = 0; i < stateCount; ++i) {
            ss << (i?",":"") << "\"Q" << i << "\"";
        }
        
        ss << "],\n  \"letters\": ["; 
        
        std::set<char> abc;
        for (const auto& [u,v,c] : transitions) {
            abc.insert(c);
        }
        
        int i = 0; 
        for (char c : abc) {
            ss << (i++?",":"") << "\"" << c << "\"";
        }
        ss << "],\n  \"transition_function\": [";

        for (size_t j = 0; j < transitions.size(); ++j) {
            auto [u,v,c] = transitions[j];
            ss << (j?",\n":"\n") << "    [\"Q" << u << "\", \"" << c << "\", \"Q" << v << "\"]";
        }
        ss << "\n  ],\n  \"start_states\": [\"Q" << startState << "\"],\n";
        ss << "  \"final_states\": [";
        
        i = 0; 
        for (int s : finalStates) {
            ss << (i++?",":"") << "\"Q" << s << "\"";
        }
        ss << "]\n}";

        return ss.str();
    }
};

bool match(const Automaton& dfa, const std::string& s) {
    int cur = dfa.startState;
    for (char c : s) {
        cur = dfa.lookup[cur * 256 + static_cast<unsigned char>(c)];
        if (cur == -1) {
            return false;
        }
    }

    return dfa.finalStates.contains(cur);
}

class RegexEngine {
    enum : char { 
        EPS = 0, 
        CONCAT = 1, 
        UNION = '|', 
        STAR = '*' 
    };

public:
    Automaton compile(const std::string& regex) {
        auto nfa = buildNFA(regex);
        auto dfa = toDFA(nfa);
        auto minDfa = minimizeDFA(dfa);
        minDfa.finalize();
        return minDfa;
    }

private:
    Automaton buildNFA(const std::string& regex) {
        std::string post = toPostfix(preprocess(regex));
        Automaton nfa;
        std::stack<std::pair<int, int>> st;

        auto push_frag = [&](char c) {
            int s = nfa.addState();
            int e = nfa.addState();
            nfa.addTx(s, e, c);
            st.push({s, e});
        };

        for (char c : post) {
            if (c == UNION) {
                auto [s2, e2] = st.top(); 
                st.pop();

                auto [s1, e1] = st.top(); 
                st.pop();

                int s = nfa.addState(); 
                int e = nfa.addState();

                nfa.addTx(s, s1, EPS); 
                nfa.addTx(s, s2, EPS);
                nfa.addTx(e1, e, EPS); 
                nfa.addTx(e2, e, EPS);
                
                st.push({s, e});
            } else if (c == CONCAT) {
                auto [s2, e2] = st.top(); 
                st.pop();

                auto [s1, e1] = st.top(); 
                st.pop();

                nfa.addTx(e1, s2, EPS);
                st.push({s1, e2});
            } else if (c == STAR) {
                auto [s1, e1] = st.top(); 
                st.pop();

                int s = nfa.addState();
                int e = nfa.addState();

                nfa.addTx(s, s1, EPS); 
                nfa.addTx(s, e, EPS);
                nfa.addTx(e1, s, EPS); 

                st.push({s, e});
            } else {
                push_frag(c);
            }
        }
        if (st.empty()) {
            return nfa;
        }

        nfa.startState = st.top().first;
        nfa.finalStates.insert(st.top().second);

        return nfa;
    }

    Automaton toDFA(const Automaton& nfa) {
        Automaton dfa;
        
        std::vector<std::vector<int>> adjEps(nfa.stateCount);
        std::vector<std::vector<std::pair<int, char>>> adjSym(nfa.stateCount);

        for (auto [u, v, c] : nfa.transitions) {
            if (c == EPS) {
                adjEps[u].push_back(v);
            } else {
                adjSym[u].push_back({v, c});
            }
        }
        
        auto getClosure = [&](std::vector<int> set) {
            std::vector<int> q = set;
            std::vector<bool> vis(nfa.stateCount, false);
            
            for (int x : set) {
                vis[x] = true;
            }

            size_t head = 0;
            
            while (head < q.size()) {
                int u = q[head++];
                for (int v : adjEps[u]) {
                    if (!vis[v]) { 
                        vis[v] = true; 
                        q.push_back(v); 
                    }
                }
            }
            
            std::sort(q.begin(), q.end());
            
            return q;
        };

        std::map<std::vector<int>, int> states;
        std::queue<std::vector<int>> q;

        auto addDFAState = [&](std::vector<int> s) {
            if (states.count(s)) {
                return states[s];
            }
            int id = dfa.addState();
            states[s] = id;
            q.push(s);
            for (int x : s) {
                if (nfa.finalStates.count(x)) {
                    dfa.finalStates.insert(id);
                }
            }
            return id;
        };

        dfa.startState = addDFAState(getClosure({nfa.startState}));

        while (!q.empty()) {
            auto u = q.front(); 
            q.pop();
            int u_id = states[u];
            std::map<char, std::vector<int>> moves;
            
            for(int x : u) {
                for(auto [v, c] : adjSym[x]) {
                    moves[c].push_back(v);
                }
            }
            
            for(auto& [c, targets] : moves) {
                int v_id = addDFAState(getClosure(targets));
                dfa.addTx(u_id, v_id, c);
            }
        }
        return dfa;
    }

    Automaton minimizeDFA(const Automaton& dfa) {
        std::vector<std::vector<int>> trans(dfa.stateCount, std::vector<int>(256, -1));
        std::set<char> abc;
        for (auto [u, v, c] : dfa.transitions) { 
            trans[u][static_cast<unsigned char>(c)] = v; 
            abc.insert(c); 
        }

        std::vector<int> group(dfa.stateCount);
        for (int s : dfa.finalStates) {
            group[s] = 1;
        }

        bool changed = true;
        while (changed) {
            changed = false;
            std::map<std::pair<int, std::vector<int>>, int> nextGroups;
            std::vector<int> nextGroup(dfa.stateCount);
            int gCount = 0;

            for (int i = 0; i < dfa.stateCount; ++i) {
                std::vector<int> sig;
                for (char c : abc) {
                    int t = trans[i][static_cast<unsigned char>(c)];
                    sig.push_back(t == -1 ? -1 : group[t]);
                }
                std::pair<int, std::vector<int>> key = {group[i], sig};
                if (!nextGroups.count(key)) {
                    nextGroups[key] = gCount++;
                }
                nextGroup[i] = nextGroups[key];
            }
            if (gCount > static_cast<int>(nextGroups.size())) {
                changed = true;
            }
            if (nextGroup != group) { 
                group = nextGroup; 
                changed = true; 
            }
        }

        Automaton minDfa;
        minDfa.stateCount = 0;
        std::map<int, int> mapG;
        for (int i = 0; i < dfa.stateCount; ++i) {
            if (!mapG.count(group[i])) {
                int id = minDfa.addState();
                mapG[group[i]] = id;
            }
        }
        minDfa.startState = mapG[group[dfa.startState]];
        for (int s : dfa.finalStates) {
            minDfa.finalStates.insert(mapG[group[s]]);
        }
        
        std::set<std::tuple<int, int, char>> uniq;
        for (auto [u, v, c] : dfa.transitions) {
            uniq.emplace(mapG[group[u]], mapG[group[v]], c);
        }
        for (auto [u, v, c] : uniq) {
            minDfa.addTx(u, v, c);
        }
        
        return minDfa;
    }

    std::string preprocess(const std::string& s) {
        std::string res;
        for (size_t i = 0; i < s.size(); ++i) {
            res += s[i];
            if (i + 1 < s.size()) {
                if (s[i] != '(' && s[i] != UNION && s[i + 1] != ')' && s[i + 1] != UNION && s[i + 1] != STAR) {
                    res += CONCAT;
                }
            }
        }
        // std::cout << "[preprocess] res: " << res << std::endl;
        return res;
    }

    std::string toPostfix(const std::string& s) {
        std::string res; 
        std::stack<char> op;
        std::map<char, int> p = {{UNION, 1}, {CONCAT, 2}, {STAR, 3}};
        for (char c : s) {
            if (c == '(') {
                op.push(c);
            } else if (c == ')') {
                while (op.top() != '(') { 
                    res += op.top(); 
                    op.pop(); 
                }
                op.pop();
            } else if (p.count(c)) {
                while (!op.empty() && op.top() != '(' && p[op.top()] >= p[c]) {
                    res += op.top(); 
                    op.pop(); 
                }
                op.push(c);
            } else {
                res += c;
            }
        }
        while (!op.empty()) { 
            res += op.top(); 
            op.pop(); 
        }
        // std::cout << "[toPostfix] res: " << res << std::endl;
        return res;
    }
};
