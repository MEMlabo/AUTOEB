#!/bin/bash

cd $(dirname $0)
cd ../
singularity build --fakeroot package/autoeb.sif package/singularity.def
