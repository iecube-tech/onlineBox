#!/bin/bash

# 检查参数是否为空
if [ -z "$1" ]; then
    echo "Usage: $0 <onlineBoxId>"
    exit 1
fi

# 使用正则表达式匹配是否为7位数字
if [[ $1 =~ ^[0-9]{7}$ ]]; then
    echo "starting..."
else
    exit 1  # 不是7位数字，返回1表示假
    echo "<onlineBoxId> length is 7"
fi

id=$1
current_dir=$(dirname "$(realpath "$0")")
# 更改 stop_frp.sh start.frp.sh 权限 777
chmod 777 "$current_dir/frp/"

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
echo "init init.ini"

# 初始化frpc
nohup $current_dir/frp/frpc -c "$current_dir/init/init.ini" > "$current_dir/log/frp_init.log" 2>&1 &
# 获取进程 ID
if ps -p $! > /dev/null; then
    # 进程存在，返回 PID
    echo "frpc $!"
else
    echo "frpc started failed...exit"
    exit 1
fi

# 开启服务
nohup python3 $current_dir/manage.py runserver 127.0.0.1:9000 > /dev/null 2>&1 &
if ps -p $! > /dev/null; then
    # 进程存在，返回 PID
    echo "boxServer $!"
else
    echo "boxServer started failed...exit"
    exit 1
fi

# 开启tcp代理
nohup python3 $current_dir/tcpServer.py > /dev/null 2>&1 &
if ps -p $! > /dev/null; then
    # 进程存在，返回 PID
    echo "boxServerProxy $!"
else
    echo "boxServerProxy started failed...exit"
    exit 1
fi

echo "done"
exit 0

