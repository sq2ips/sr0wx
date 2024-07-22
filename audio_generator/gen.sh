#!/bin/bash

rm -rf ogg/
mkdir ogg/
cd ogg/
ln -s ../../pl_google/samples/* .
cd ..
python audiogenerator.py
find ogg -maxdepth 1 -type l -delete