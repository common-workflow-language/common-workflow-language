FROM debian:8
RUN apt-get update && apt-get install -qq nodejs
ADD node-expr-engine/cwlNodeEngine.js /usr/local/bin/
