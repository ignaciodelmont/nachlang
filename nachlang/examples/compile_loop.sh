nachlang --output-ll --compile-only test_loop.nach

opt -O3 -S test_loop.nach.ll -o test_loop_O3.nach.ll
opt -O2 -S test_loop.nach.ll -o test_loop_O2.nach.ll
opt -O1 -S test_loop.nach.ll -o test_loop_O1.nach.ll
opt -O0 -S test_loop.nach.ll -o test_loop_O0.nach.ll

echo "--------------------------------"
echo  -e "Running O3 optimization"


time lli test_loop_O3.nach.ll




echo "--------------------------------"
echo -e "🐍 Python test"
time python test.py