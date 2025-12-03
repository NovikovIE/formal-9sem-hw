python3 clone_file.py war_and_peace_1.txt war_and_peace_1_big.txt

flex -o opt_wc.c my_wc.l
flex -o opt_wc_2.c my_wc_2.l
flex -o naive_wc.c wc.l

g++ -std=c++20 -O3 opt_wc.c -o opt_wc 
g++ -std=c++20 -O3 opt_wc_2.c -o opt_wc_2
gcc -O3 naive_wc.c -o naive_wc

echo "--- System WC ---"
LC_ALL=C time wc war_and_peace_1_big.txt

echo "--- Naive Flex ---"
time ./naive_wc < war_and_peace_1_big.txt

echo "--- Optimized Flex ---"
time ./opt_wc war_and_peace_1_big.txt

echo "--- Optimized Flex 2 ---"
time ./opt_wc_2 < war_and_peace_1_big.txt
