FROM ubuntu:22.04

# basic setting
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ >/etc/timezone

ENV SRC=/src
ENV OUT=/out
RUN mkdir -p $SRC $OUT/smake-out

ENV BUILD=/src/build.sh

# Sparrow
ENV SMAKE_DIR=/smake
ENV SMAKE_BIN=$SMAKE_DIR/smake
ENV SMAKE_OUT=$OUT/smake-out

# for debian package build
ENV DEB_BUILD_OPTIONS="nocheck notest"
RUN sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y make git gcc tzdata bear dpkg-dev libtinfo5 wget vim tmux opam

RUN git clone https://github.com/prosyslab/smake.git
RUN git clone https://github.com/prosyslab/patron-artifact.git $SRC

RUN chmod +x $SRC/patron-artifact/build_latest.sh
RUN $SRC/patron-artifact/build_latest.sh

WORKDIR $SRC