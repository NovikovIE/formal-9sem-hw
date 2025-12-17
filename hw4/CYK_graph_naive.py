import copy

G={
    'A':[['a']],
    'B':[['d']],
    'C':[['c']],
    'D':[['A','B']],
    'E':[['B','C']],
    'S':[['D','E']]
 }


def search_lhs_non_terminal_rule(first, second): # G
    res = []
    for k,v in G.items():
        for item in v:
            if [first,second] == item:
                res.append(k)
                # print("==rule found:", first, second,"<-",k)
    return res


def search_lhs_terminal_rule(term=None): # G
    if not term:
        return []
    res = []
    for k,v in G.items():
        for rhs_item in v:
            if len(rhs_item) == 1:
                if term == rhs_item[0]:
                    res.append(k)
    return res


def logM(M, prefix_msg=None, postfix_msg=None):
    if prefix_msg:
        print(prefix_msg)
    for i in M:
        print(i)
    return


def matrCmp(M1, M2): # O(N^2 * V)
    for i,row in enumerate(M1):
        for j in range(len(row)):
            if not M1[i][j] == M2[i][j]:
                return False
    return True


def CYK_graph(M, G = None, log=True):
    M1 = copy.deepcopy(M) # O(N^2 * V)
    
    # O(N^2 * G)
    for i,row in enumerate(M): # N
        for j in range(len(row)): # N
            nonterm_list = search_lhs_terminal_rule(M[i][j]) # G
            M[i][j] = nonterm_list

    if log == True:
        logM(M, "After 1st step:")

    n = len(M)
    # динамика для 2 шага и далее:
    # N^2 * V * (N^2 + N^2 * V + N^3 * V^2 * G) = 
    # N^4 * V + N^4 * V^2 * G + N^5 * V^3 * G = 
    # N^5 * V^3 * G
    while not matrCmp(M1, M): # N^2
        M1 = copy.deepcopy(M) # N^2 * V
        for k in range(n): # N
            for i in range(n): # N
                for j in range(n): # N
                    first_non_term_set = M[i][k]
                    second_non_term_set = M[k][j]

                    for lhr in first_non_term_set: # V
                        for rhr in second_non_term_set: # V
                            ntr = search_lhs_non_terminal_rule(lhr, rhr) # G
                            if len(ntr) > 0:

                                try:
                                    M[i][j] += search_lhs_non_terminal_rule(lhr, rhr) # G
                                except TypeError:
                                    M[i][j] = search_lhs_non_terminal_rule(lhr, rhr) # G
                                M[i][j]=list(set(M[i][j]))

        if log:
            logM(M, prefix_msg="M after current pass:")


if __name__ == '__main__':
    print("==========Test 1===========")
    graph1 = [
        ['0', 'a', '0', '0', '0'],
        ['0', '0', 'd', '0', '0'],
        ['0', '0', '0', 'd', '0'],
        ['0', '0', '0', '0', 'c'],
        ['0', '0', '0', '0', '0'],
    ]

    CYK_graph(graph1, G)
    print("==========Test 2===========")
    graph2 = [
        ['0', 'a', '0', '0', '0'],
        ['0', '0', 'd', '0', '0'],
        ['0', '0', '0', 'd', '0'],
        ['0', '0', '0', 'c', 'c'],
        ['0', '0', '0', '0', '0']
    ]

    CYK_graph(graph2, G)
    