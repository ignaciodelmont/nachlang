#!/usr/bin/env bash
# ==============================================================
# NachLang Benchmark Suite
#
# Runs each benchmark across every execution configuration and
# compares against the equivalent Python program.
#
# Usage:
#   ./run_benchmarks.sh          # full workload
#   QUICK=1 ./run_benchmarks.sh  # reduced workload, for a smoke run
#
# Requirements:
#   - nachlang installed (poetry install)
#   - python3
#   - opt / lli (brew install llvm@14 or newer)
#   - Boehm GC (brew install bdw-gc)
#
# Override NACHLANG_CMD / LIBGC_PATH / RUNS as needed.
# ==============================================================

set -uo pipefail

NACHLANG_CMD=${NACHLANG_CMD:-"poetry run nachlang"}
LIBGC_PATH=${LIBGC_PATH:-/opt/homebrew/lib/libgc.dylib}
RUNS=${RUNS:-5}
QUICK=${QUICK:-0}

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

read -r -a NACHLANG <<< "$NACHLANG_CMD"

# --------------------------------------------------------------
# Benchmark definitions
#
# Each entry:
#   label | source | literal to scale | full | quick | malloc_max | bytes/unit
#
# malloc_max is the largest workload parameter the malloc-only
# configurations can complete. Nothing is ever freed, so the resident set
# grows linearly with the work done -- measured at 128 bytes per loop
# iteration (four 32-byte NACHTYPEs), and ~850 MB for fib(32). Beyond
# malloc_max those configurations are skipped and reported, never silently
# dropped. bytes/unit of 0 means the footprint is not linear in the
# parameter, so no projection is quoted.
#
# bench_loop is listed twice on purpose: 50M is the largest size where the
# malloc configurations still fit in RAM, and 100M is the original target
# workload, which only the GC configurations can reach.
# --------------------------------------------------------------
BENCHMARKS=(
    "bench_fib|bench_fib|35|35|25|35|0"
    "bench_loop_50M|bench_loop|100000000|50000000|1000000|50000000|128"
    "bench_loop_100M|bench_loop|100000000|100000000|2000000|20000000|128"
    "bench_alloc|bench_alloc|10000000|10000000|1000000|10000000|0"
)

PASS=0
FAIL=0
SKIP=0

# --------------------------------------------------------------
# Helpers
# --------------------------------------------------------------

# NachLang prints every number through "%f"; Python prints integers.
# Compare on a canonical form so both runtimes can share one oracle.
normalize() {
    sed -e 's/[[:space:]]*$//' -e 's/\.0*$//' <<< "$1"
}

median() {
    printf '%s\n' "$@" | sort -n | awk '{v[NR]=$1} END {
        if (NR % 2) printf "%.3f", v[(NR+1)/2]
        else printf "%.3f", (v[NR/2] + v[NR/2+1]) / 2
    }'
}

fastest() {
    printf '%s\n' "$@" | sort -n | head -1
}

# Run a command RUNS times, verifying stdout against the oracle each time.
# Reports median and best wall-clock. A wrong answer is a hard failure -- a
# config that dies fast must never read as a fast config.
#
# Correctness is judged on stdout, not on the exit status: nachlang emits
# `define void @main`, so lli reports a junk exit code even on a clean run.
# The exit status is still captured and reported when the answer is wrong.
measure() {
    local label="$1" expected="$2"
    shift 2

    local times=() rc t got stderr
    local failures=0 first_error=""

    for ((run = 1; run <= RUNS; run++)); do
        /usr/bin/time -p "$@" > "$WORK_DIR/stdout.txt" 2> "$WORK_DIR/time.txt"
        rc=$?
        t=$(awk '/^real/ {print $2}' "$WORK_DIR/time.txt")
        got=$(normalize "$(tail -1 "$WORK_DIR/stdout.txt")")

        if [ "$got" != "$expected" ]; then
            failures=$((failures + 1))
            if [ -z "$first_error" ]; then
                stderr=$(grep -v -e '^real' -e '^user' -e '^sys' "$WORK_DIR/time.txt" | head -1)
                first_error="got '${got:-<no output>}', want '$expected' (exit $rc${stderr:+; $stderr})"
            fi
            continue
        fi

        times+=("$t")
    done

    if [ ${#times[@]} -eq 0 ]; then
        printf '  %-26s FAILED  (%s)\n' "$label" "$first_error"
        FAIL=$((FAIL + 1))
        return 1
    fi

    local note=""
    [ $failures -gt 0 ] && note="  [${failures}/${RUNS} runs failed: ${first_error}]"

    printf '  %-26s %8ss median   %8ss best%s\n' \
        "$label" "$(median "${times[@]}")" "$(fastest "${times[@]}")" "$note"
    PASS=$((PASS + 1))
}

skip() {
    printf '  %-26s SKIPPED (%s)\n' "$1" "$2"
    SKIP=$((SKIP + 1))
}

# Emit LLVM IR for a source file. --output-ll writes alongside the input
# rather than to stdout, so collect it from there.
emit_ir() {
    local src="$1" dest="$2"
    shift 2

    rm -f "${src}.ll"
    "${NACHLANG[@]}" "$src" --output-ll --compile-only "$@" > /dev/null 2>&1

    if [ ! -s "${src}.ll" ]; then
        return 1
    fi
    mv "${src}.ll" "$dest"
}

# --------------------------------------------------------------
# Environment
# --------------------------------------------------------------
echo "=============================================="
echo " NachLang Benchmark Suite"
echo " $(date)"
echo " Runs per configuration: $RUNS"
[ "$QUICK" = "1" ] && echo " QUICK mode: reduced workloads"
echo "=============================================="
echo ""

echo "--- Environment ---"
uname -sr
sysctl -n machdep.cpu.brand_string 2>/dev/null || true
echo "RAM:      $(sysctl -n hw.memsize 2>/dev/null | awk '{printf "%.0f GB", $1/1024/1024/1024}')"
echo "python:   $(python3 --version 2>&1)"
echo "nachlang: $NACHLANG_CMD"
echo "opt:      $(opt --version 2>/dev/null | awk '/LLVM version/ {print $NF}') ($(command -v opt))"
echo "lli:      $(lli --version 2>/dev/null | awk '/LLVM version/ {print $NF}') ($(command -v lli))"
if [ -f "$LIBGC_PATH" ]; then
    echo "libgc:    $LIBGC_PATH"
else
    echo "libgc:    MISSING at $LIBGC_PATH -- GC configurations will be skipped"
fi
echo ""

# --------------------------------------------------------------
# Fixed startup cost
#
# Every measurement below includes the startup cost of its runtime
# family. For NachLang that is Python interpreter startup plus IR
# generation plus the MCJIT compile, which is substantial relative to
# these workloads, so quote it rather than hide it.
# --------------------------------------------------------------
echo "--- Fixed startup cost (subtract to compare execution alone) ---"
echo 'print(1)' > "$WORK_DIR/noop.nach"
echo 'print(1)' > "$WORK_DIR/noop.py"
measure "NachLang JIT startup" "1" "${NACHLANG[@]}" "$WORK_DIR/noop.nach"
if emit_ir "$WORK_DIR/noop.nach" "$WORK_DIR/noop.ll"; then
    measure "lli startup" "1" lli "$WORK_DIR/noop.ll"
fi
measure "python3 startup" "1" python3 "$WORK_DIR/noop.py"
echo ""

# --------------------------------------------------------------
# Benchmarks
# --------------------------------------------------------------
for entry in "${BENCHMARKS[@]}"; do
    IFS='|' read -r label src literal full quick malloc_max bytes_per_unit <<< "$entry"

    param="$full"
    [ "$QUICK" = "1" ] && param="$quick"

    src_nach="$SCRIPT_DIR/${src}.nach"
    src_py="$SCRIPT_DIR/${src}.py"
    nach="$WORK_DIR/${label}.nach"
    py="$WORK_DIR/${label}.py"

    sed "s/${literal}/${param}/g" "$src_nach" > "$nach"
    sed "s/${literal}/${param}/g" "$src_py" > "$py"

    echo "=============================================="
    echo " $label  (workload parameter: $param)"
    echo "=============================================="

    # Python is both a benchmark subject and the correctness oracle.
    if ! python3 "$py" > "$WORK_DIR/oracle.txt" 2>&1; then
        echo "  Python reference failed -- skipping benchmark"
        echo "$(head -3 "$WORK_DIR/oracle.txt")"
        echo ""
        SKIP=$((SKIP + 1))
        continue
    fi
    expected=$(normalize "$(tail -1 "$WORK_DIR/oracle.txt")")
    echo "  expected result: $expected"
    echo ""

    measure "Python 3" "$expected" python3 "$py"

    # --- malloc configurations ---
    if [ "$param" -le "$malloc_max" ]; then
        measure "NachLang JIT (malloc)" "$expected" "${NACHLANG[@]}" "$nach"

        if emit_ir "$nach" "$WORK_DIR/${label}.malloc.ll"; then
            for level in 1 2 3; do
                if opt "-O${level}" -S "$WORK_DIR/${label}.malloc.ll" \
                       -o "$WORK_DIR/${label}.malloc.O${level}.ll" 2>/dev/null; then
                    measure "opt -O${level} + lli (malloc)" "$expected" \
                        lli "$WORK_DIR/${label}.malloc.O${level}.ll"
                else
                    skip "opt -O${level} + lli (malloc)" "opt failed"
                fi
            done
        else
            skip "opt -O* + lli (malloc)" "IR generation failed"
        fi
    else
        reason="malloc-only never frees; viable up to $malloc_max, asked for $param"
        if [ "$bytes_per_unit" -gt 0 ]; then
            reason="$reason (~$(awk -v p="$param" -v b="$bytes_per_unit" \
                'BEGIN {printf "%.1f", p * b / 1024 / 1024 / 1024}') GB)"
        fi
        skip "NachLang JIT (malloc)" "$reason"
        for level in 1 2 3; do
            skip "opt -O${level} + lli (malloc)" "$reason"
        done
    fi

    # --- GC configurations ---
    if [ -f "$LIBGC_PATH" ]; then
        measure "NachLang JIT + GC" "$expected" \
            "${NACHLANG[@]}" "$nach" --libgc-path "$LIBGC_PATH"

        if emit_ir "$nach" "$WORK_DIR/${label}.gc.ll" --libgc-path "$LIBGC_PATH"; then
            if opt -O3 -S "$WORK_DIR/${label}.gc.ll" -o "$WORK_DIR/${label}.gc.O3.ll" 2>/dev/null; then
                # GC IR references GC_malloc, so lli must load libgc.
                measure "opt -O3 + lli + GC" "$expected" \
                    lli -load "$LIBGC_PATH" "$WORK_DIR/${label}.gc.O3.ll"
            else
                skip "opt -O3 + lli + GC" "opt failed"
            fi
        else
            skip "opt -O3 + lli + GC" "IR generation failed"
        fi
    else
        skip "NachLang JIT + GC" "libgc not found"
        skip "opt -O3 + lli + GC" "libgc not found"
    fi

    echo ""
done

echo "=============================================="
echo " Done: $PASS measured, $FAIL failed, $SKIP skipped"
echo " $(date)"
echo "=============================================="

[ $FAIL -eq 0 ]
