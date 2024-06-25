#!/bin/bash

# 检查参数是否为空
if [ -z "$1" ]; then
    echo "Usage: $0 <number>"
    exit 1
fi

# 参数
number="$1"

# 执行命令
nohup /iecube/onlineBox/frp/frpc -c "/iecube/onlineBox/ini/${number}.ini" > "/iecube/onlineBox/log/${number}.log" 2>&1 &

# 获取进程 ID
pid=$!

# 检查 PID 是否存在
if ps -p $pid > /dev/null; then
    # 进程存在，返回 PID
    echo "$pid"
else
    # 进程不存在，返回 0
    echo "0"
fi
