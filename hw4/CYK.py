from collections import defaultdict, deque

class Grammar:
    def __init__(self, rules):
        self.terminals = defaultdict(list)
        self.non_terminals = defaultdict(list)
        
        # G
        for lhs, rhs_list in rules.items(): 
            for rhs in rhs_list:
                if len(rhs) == 1:
                    self.terminals[rhs[0]].append(lhs)
                elif len(rhs) == 2:
                    self.non_terminals[tuple(rhs)].append(lhs)

    def get_by_term(self, term):
        return self.terminals.get(term, []) # 1

    def get_by_pair(self, left, right):
        return self.non_terminals.get((left, right), []) # 1

class CYKGraph:
    def __init__(self, grammar):
        self.grammar = grammar

    def solve(self, matrix):
        n = len(matrix)
        adj = defaultdict(list)
        rev_adj = defaultdict(list)
        queue = deque()
        added_edges = set() 

        # N^2 * V
        for i in range(n): # N
            for j in range(n): # N
                term = matrix[i][j]
                if term == '0':
                    continue
                for lhs in self.grammar.get_by_term(term): # V
                    edge = (i, j, lhs)
                    if edge not in added_edges:
                        added_edges.add(edge)
                        queue.append(edge)
                        adj[i].append((j, lhs))
                        rev_adj[j].append((i, lhs))

        # N^3 V^3 ?
        while queue: # N^2 * V?
            u, v, label_mid = queue.popleft()

            for w, label_left in rev_adj[u]: # N * V
                for lhs in self.grammar.get_by_pair(label_left, label_mid): # V 
                    new_edge = (w, v, lhs)
                    if new_edge not in added_edges:
                        added_edges.add(new_edge)
                        queue.append(new_edge)
                        adj[w].append((v, lhs))
                        rev_adj[v].append((w, lhs))

            for w, label_right in adj[v]: # N * V
                for lhs in self.grammar.get_by_pair(label_mid, label_right): # V 
                    new_edge = (u, w, lhs)
                    if new_edge not in added_edges:
                        added_edges.add(new_edge)
                        queue.append(new_edge)
                        adj[u].append((w, lhs))
                        rev_adj[w].append((u, lhs))

        return self._format_output(n, added_edges)

    def _format_output(self, n, edges):
        res = [[[] for _ in range(n)] for _ in range(n)]
        for u, v, label in edges:
            res[u][v].append(label)
        for row in res:
            for cell in row:
                cell.sort()
        return res

if __name__ == '__main__':
    G = {
        'A': [['a']], 
        'B': [['d']], 
        'C': [['c']],
        'D': [['A', 'B']], 
        'E': [['B', 'C']], 
        'S': [['D', 'E']]
    }
    grammar = Grammar(G)

    g_solver = CYKGraph(grammar)
    graph_input = [
        ['0', 'a', '0', '0'],
        ['0', '0', 'd', '0'],
        ['0', '0', '0', 'c'],
        ['0', '0', '0', '0']
    ]
    res_g = g_solver.solve(graph_input)
    print(f"0->3: {res_g[0][3]}")
    for row in res_g:
        print(row)
    
    graph_input = [
        ['0', 'a', '0', '0', '0'],
        ['0', '0', 'd', '0', '0'],
        ['0', '0', '0', 'd', '0'],
        ['0', '0', '0', '0', 'c'],
        ['0', '0', '0', '0', '0'],
    ]
    res_g = g_solver.solve(graph_input)
    print(f"0->4: {res_g[0][4]}")
    for row in res_g:
        print(row)