FROM ubuntu:22.04

# basic setting
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ >/etc/timezone

ENV SRC=/src
RUN mkdir -p $SRC

ENV BUILD=/tmp/build.sh

# Sparrow
ENV SMAKE_DIR=/patron-artifact/smake
ENV SMAKE_BIN=$SMAKE_DIR/smake

# for debian package build
ENV DEB_BUILD_OPTIONS="nocheck notest"
RUN sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y make git gcc tzdata bear dpkg-dev libtinfo5 wget vim tmux opam dune python3 python3-pip

COPY build.sh /tmp
RUN chmod +x $BUILD
RUN $BUILD

WORKDIR $SRC