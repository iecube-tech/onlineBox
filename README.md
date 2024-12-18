# 创建用户 组 
 iecube:iecube
# this project run with linux
 with python 3.9 django 4.2
 django==4.2  jinja2  requests
# onlineBoxService
onlineBox 的 守护进程，用于管理远程设备

# run path
`mkdir /iecube`
cd `/iecube` :  git clone https://github.com/iecube-tech/onlineBox.git

# make service
`vi /lib/systemd/system/onlineBox.service`
```shell
[Unit]
Description=onlineBox
After=network.target remote-fs.target nss-lookup.target
Wants=network.target

[Service]
Type=forking
User=iecube
ExecStart=/iecube/onlineBox/start.sh 1014901 #这里id要变化 
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

`chmod +x /lib/systemd/system/onlineBox.service`

`service start onlineBox`

`systemctl enable onlineBox`