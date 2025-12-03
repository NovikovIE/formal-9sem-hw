%top{
#define YY_BUF_SIZE 262144
}

%option 8bit fast noyywrap align
%option reentrant
%option batch

%{
#include <iostream>
#include <vector>
#include <cstdint>
#include <cstdio>
#include <fcntl.h>

struct Stats {
    uint64_t lines = 0;
    uint64_t words = 0;
    uint64_t bytes = 0;
} stats;
%}

whitespace    [ \t]+
word          [^ \t\n]+
newlines      \n+

%%

{newlines} {
    stats.lines += yyleng;
    stats.bytes += yyleng;
}

{whitespace} {
    stats.bytes += yyleng;
}

{word} {
    stats.words++;
    stats.bytes += yyleng;
}

<<EOF>> {
    std::cout << stats.lines << " " 
              << stats.words << " " 
              << stats.bytes << "\n";
    return 0;
}

%%

int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false);
    
    yyscan_t scanner;
    yylex_init(&scanner);

    if (argc > 1) {
        FILE *in = fopen(argv[1], "rb");
        if (!in) {
            std::cerr << "Error " << argv[1] << "\n";
            return 1;
        }

        #ifdef __linux__
            int fd = fileno(in);
            posix_fadvise(fd, 0, 0, POSIX_FADV_SEQUENTIAL);
        #endif

        yyset_in(in, scanner);
    } else {
        yyset_in(stdin, scanner);
    }

    yylex(scanner);
    yylex_destroy(scanner);
    return 0;
}