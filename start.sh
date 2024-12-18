#!/bin/bash


id=$1
current_dir=$(dirname "$(realpath "$0")")
ARCH=$(uname -m)
TARGET_HOST="vnc.iecube.com.cn"
chmod +x "${current_dir}/frp/start_frp.sh"
chmod +x "${current_dir}/frp/stop_frp.sh"
chmod +x "${current_dir}/frp/aarch64/frpc"
chmod +x "${current_dir}/frp/x86/frpc"
rm -rf log/onlineBox.log

# 定义日志记录函数
log_message() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    # 获取传入的消息内容
    if [ ! -d "log" ]; then
        mkdir log
    fi
    echo "[$timestamp] $1" >> log/onlineBox.log
}

# 检查参数是否为空
if [ -z "$1" ]; then
    log_message "Usage: $0 <onlineBoxId>"
    exit 1
fi

# 使用正则表达式匹配是否为7位数字
if [[ $1 =~ ^[0-9]{7}$ ]]; then
    log_message "starting..."
else
    exit 1  # 不是7位数字，返回1表示假
    log_message "<onlineBoxId> length is 7"
fi

# network check
sleep_time=2
while ! ping -c 1 "$TARGET_HOST" &> /dev/null
do
  log_message "vnc.iecube.com.cn unreachable，waiting..."
  sleep $sleep_time
  sleep_time=$((sleep_time + 2))
done

# 初始化配置文件
config_file="$current_dir/init/init.ini"
remote_port=${id:3}
cat << EOF > "$config_file"
[common]
server_addr = vnc.iecube.com.cn
server_port = 7000

[tcp$id]
type = tcp
local_ip = 127.0.0.1
local_port = 4900
remote_port = $remote_port
EOF
log_message "init init.ini"

frp_pid=0
# 初始化frpc
if [ "$ARCH" = "aarch64" ]; then
    nohup "$current_dir"/frp/aarch64/frpc -c "$current_dir/init/init.ini" > "$current_dir/log/frp_init.log" 2>&1 &
    frp_pid=$!
elif [ "$ARCH" = "x86_64" ]; then
    nohup "$current_dir"/frp/x86/frpc -c "$current_dir/init/init.ini" > "$current_dir/log/frp_init.log" 2>&1 &
    frp_pid=$!
else
    log_message "frpc cannot run on $ARCH "
    exit 1
fi

# 获取进程 ID
if ps -p $frp_pid > /dev/null; then
    # 进程存在，返回 PID
    log_message "frpc $!"
else
    log_message "frpc started failed...exit"
    exit 1
fi

# 开启服务
nohup python3 "$current_dir"/manage.py runserver 127.0.0.1:9000 > /dev/null 2>&1 &
if ps -p $! > /dev/null; then
    # 进程存在，返回 PID
    log_message "boxServer $!"
else
    log_message "boxServer started failed...exit"
    exit 1
fi

# 开启tcp代理
nohup python3 "$current_dir"/tcpServer.py > /dev/null 2>&1 &
if ps -p $! > /dev/null; then
    # 进程存在，返回 PID
    log_message "boxServerProxy $!"
else
    log_message "boxServerProxy started failed...exit"
    exit 1
fi

log_message "done"
exit 0

