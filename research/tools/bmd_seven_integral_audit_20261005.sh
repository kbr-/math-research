#!/bin/sh
# All algebraic validation runs inside the compiled Singular kernel.
set -eu
for input in research/results/bmd-lucas-full-profiles-20261005/integer-checks/*.sing
do
    Singular -q "$input"
done
