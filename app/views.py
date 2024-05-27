import json
import subprocess
import logging
from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from jinja2 import Template
from django.conf import settings
from . import models
import os

# Create your views here.

TEMPLATE_STR = settings.TEMPLATE_STR


class BackMsg:
    def __init__(self, res=0, device_id=0, p_id=0, id_list=[], ip_list=[], str_data=''):
        self.res = res
        self.deviceId = device_id
        self.pId = p_id
        self.idList = id_list
        self.ipList = ip_list
        self.strData = str_data


@require_GET
def curl(request):
    back_msg = BackMsg(res=1)
    return JsonResponse(back_msg.__dict__)


@require_POST
def add_device(request):
    print(type(request.body.decode('utf-8')))
    post_data = json.loads(request.body.decode('utf-8'))
    print(request.body.decode('utf-8'))
    print(type(post_data))
    back_msg = BackMsg()
    try:
        deviceId = post_data['id']
        frpServerIp = post_data['frpServerIp']
        frpServerPort = post_data['frpServerPort']
        localIp = post_data['localIp']
        localPort = post_data['localPort']
        remotePort = post_data['remotePort']
        template = Template(TEMPLATE_STR)
        content = template.render(serverAdd=frpServerIp, serverPort=frpServerPort, localIp=localIp, localPort=localPort,
                                  remotePort=remotePort)
        print(content)
        with open(settings.DIR_OF_INI+str(deviceId)+".ini", "w") as file:
            file.write(content)
            file.close()
        # 执行运行frpc
        pid = start_frpc(deviceId)
        if pid > 0:
            back_msg.res = 1
            back_msg.deviceId = deviceId
            back_msg.pId = pid
        return JsonResponse(back_msg.__dict__)
    except Exception as e:
        logging.error(e)
    finally:
        return JsonResponse(back_msg.__dict__)


def start_frpc(id):
    """
    :param id: deviceId
    :return: 0: error pid: 进程号
    """
    command = ['/iecube/onlineBox/frp/start_frp.sh', str(id)]
    try:
        if os.name != 'posix':
            return 1
        # 执行Shell脚本并捕获输出
        output = subprocess.run(command, capture_output=True, text=True, check=True)
        # 返回Shell脚本的输出（PID）
        pid = int(output.stdout.strip())
        return pid
    except subprocess.CalledProcessError as e:
        logging.error("subprocess error: " + e.stdout)
        return 0


def stop_frpc(pid):
    """
    :param pid: frp进程号
    :return: 0 进程本来不存在/失败； 1 killed
    """
    command = ['/iecube/onlineBox/frp/stop_frp.sh', str(pid)]

    try:
        output = subprocess.run(command, capture_output=True, text=True, check=True)
        res = int(output.stdout.strip())
        return res
    except subprocess.CalledProcessError as e:
        logging.error("subprocess error: " + e.stdout)
        return 0
