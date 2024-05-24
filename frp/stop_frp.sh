#!/bin/bash

# 检查参数是否传递
if [ $# -ne 1 ]; then
    echo "Usage: $0 <pid>"
    exit 1
fi

# 获取传递的 PID
pid=$1

# 检查是否存在该 PID 的进程
if ps -p $pid > /dev/null; then
    # 存在则杀死该进程 返回 1
    kill -9 $pid
    exit 1
else
    # 不存在返回 0
    exit 0
fi
