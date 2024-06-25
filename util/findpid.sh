#!/bin/bash

# 检查参数是否为空
if [ -z "$1" ]; then
    echo "Usage: $0 name"
    exit 1
fi

pid=$(ps -ef | grep $1 | grep -v color | grep -v grep | grep -v $0 | awk '{print $2}')
if [ -z "$pid" ]; then
    pid=0
fi
echo $pid
exit 0
