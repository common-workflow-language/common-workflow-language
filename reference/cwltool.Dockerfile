FROM commonworkflowlanguage/cwltool_module
MAINTAINER peter.amstutz@curoverse.com

VOLUME /var/lib/docker
ENTRYPOINT ["wrapdocker", "cwltool"]
