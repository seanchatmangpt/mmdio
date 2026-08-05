#!/bin/bash
cd lang
OUTDIR=grammar
rm -rf $OUTDIR
antlr4 -visitor -no-listener -Dlanguage=Python3 OPQL.g4 -o $OUTDIR
