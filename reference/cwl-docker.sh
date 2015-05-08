#!/bin/sh
docker run --privileged -ti --volume=$PWD:/tmp/workdir -w=/tmp/workdir cwltool $*
