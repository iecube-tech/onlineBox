#!/bin/bash

# 检查参数是否为空
if [ -z "$1" ]; then
    echo "Usage: $0 <number>"
    exit 1
fi

# 参数
number="$1"

ARCH=$(uname -m)
current_dir=$(dirname "$(realpath "$0")")
pid=0

# 执行命令
if [ "$ARCH" = "aarch64" ]; then
  nohup "${current_dir}"/aarch64/frpc -c "/iecube/onlineBox/ini/${number}.ini" > "/iecube/onlineBox/log/${number}.log" 2>&1 &
  pid=$!
elif [ "$ARCH" = "x86_64" ]; then
  nohup "${current_dir}"/x86/frpc -c "/iecube/onlineBox/ini/${number}.ini" > "/iecube/onlineBox/log/${number}.log" 2>&1 &
  pid=$!
else
  echo "0"
  exit 0
fi

# 检查 PID 是否存在
if [[ $pid -ne 0 ]]; then
  if ps -p $pid > /dev/null; then
      # 进程存在，返回 PID
      echo "$pid"
  else
      # 进程不存在，返回 0
      echo "0"
  fi
else
  echo "0"
fi
