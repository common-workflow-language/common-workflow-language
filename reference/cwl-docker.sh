#!/bin/sh
docker run --name=cwl-docker -v /var/lib/docker -i -t fedora-data true
docker run --privileged -ti --volume=$PWD:$PWD -w=$PWD commonworkflowlanguage/cwltool $*
