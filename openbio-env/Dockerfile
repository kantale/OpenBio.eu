FROM ubuntu:18.04

RUN apt-get update -y
RUN apt-get install -y curl

RUN mkdir -p /openbio/work /openbio/tools /openbio/data

ENV OBC_WORK_PATH=/openbio/work
ENV OBC_TOOL_PATH=/openbio/tools
ENV OBC_DATA_PATH=/openbio/data

WORKDIR /root
