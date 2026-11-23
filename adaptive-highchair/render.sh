#!/bin/sh
# Reproduce preview.png. Run from this directory.
set -e
openscad -o preview.png \
  --camera=0,0,350,65,0,35,3400 \
  --imgsize=1200,1000 \
  --colorscheme=Tomorrow \
  adaptive-highchair.scad
