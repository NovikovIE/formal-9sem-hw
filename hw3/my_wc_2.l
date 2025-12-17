ws    [ \t]
nonws [^ \t\n] 

%option 8bit fast main noyywrap
%option pointer
%%
        int cc = 0, wc = 0, lc = 0;

{nonws}+        cc += yyleng; ++wc;

{ws}+           cc += yyleng;

\n              ++lc; ++cc;

<<EOF>>         {
                printf( "%8d %8d %8d\n", lc, wc, cc );
                yyterminate();
                }
