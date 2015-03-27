#!/bin/sh
rm -rf out
mkdir out
python ../../reference/cwltool/main.py build-doc.cwl build.json --outdir=$PWD/out
