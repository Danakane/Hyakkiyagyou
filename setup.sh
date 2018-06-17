#!/bin/sh -

DIR="$(cd "$(dirname "$0")" && pwd)"
chmod go-rwx ${DIR}

APPSCRIPT="nuurihyon.py"
APPNAME="nuurihyon"
SRCPATH=${DIR}/${APPSCRIPT}
DSTPATH="/sbin"/${APPNAME}
ln -sf ${SRCPATH} ${DSTPATH}

