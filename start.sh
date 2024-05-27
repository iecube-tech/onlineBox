#!/bin/bash

# 检查参数是否为空
if [ -z "$1" ]; then
    echo "Usage: $0 <onlineBoxId>"
    exit 1
fi

id=$1