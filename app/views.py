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
    def __init__(self, res=0, device_id=0, device_state=0, p_id=0, id_list=[], ip_list=[], str_data=''):
        self.res = res
        self.deviceId = device_id
        self.deviceState = device_state
        self.pid = p_id
        self.idList = id_list
        self.ipList = ip_list
        self.strData = str_data


@require_GET
def curl(request):
    back_msg = BackMsg(res=1)
    return JsonResponse(back_msg.__dict__)


@require_POST
def add_device(request):
    # print(type(request.body.decode('utf-8')))
    post_data = json.loads(request.body.decode('utf-8'))
    # print(request.body.decode('utf-8'))
    # print(type(post_data))
    back_msg = BackMsg()
    try:
        deviceId = post_data['id']
        pid = post_data['pid']
        frpServerIp = post_data['frpServerIp']
        frpServerPort = post_data['frpServerPort']
        localIp = post_data['localIp']
        localPort = post_data['localPort']
        remotePort = post_data['remotePort']
        template = Template(TEMPLATE_STR)
        content = template.render(serverAdd=frpServerIp, serverPort=frpServerPort, id=deviceId, localIp=localIp,
                                  localPort=localPort, remotePort=remotePort)
        # print(content)
        with open(settings.DIR_OF_INI+str(deviceId)+".ini", "w") as file:
            file.write(content)
            file.close()
        # 执行运行frpc
        pid = start_frpc(deviceId)
        if pid > 0:
            back_msg.res = 1
            back_msg.deviceId = deviceId
            back_msg.deviceState = 1
            back_msg.pid = pid
        return JsonResponse(back_msg.__dict__)
    except Exception as e:
        logging.error(e)
        back_msg.strData = str(e)
        return JsonResponse(back_msg.__dict__)
    finally:
        return JsonResponse(back_msg.__dict__)


@require_POST
def del_device(request):
    post_data = json.loads(request.body.decode('utf-8'))
    back_msg = BackMsg()
    try:
        deviceId = post_data['id']
        pid = post_data['pid']
        if os.name == 'posix':
            stop_frpc(pid=pid)
            if os.path.exists(settings.DIR_OF_INI+str(deviceId)+".ini"):
                os.remove(settings.DIR_OF_INI+str(deviceId)+".ini")
            back_msg.res = 1
        return JsonResponse(back_msg.__dict__)
    except Exception as e:
        logging.error(e)
        back_msg.strData = str(e)
        return JsonResponse(back_msg.__dict__)
    finally:
        return JsonResponse(back_msg.__dict__)


@require_POST
def start_device(request):
    post_data = json.loads(request.body.decode('utf-8'))
    back_msg = BackMsg()
    try:
        deviceId = post_data['id']
        pid = post_data['pid']
        frpServerIp = post_data['frpServerIp']
        frpServerPort = post_data['frpServerPort']
        localIp = post_data['localIp']
        localPort = post_data['localPort']
        remotePort = post_data['remotePort']
        if os.name == 'posix':
            if not os.path.exists(settings.DIR_OF_INI+str(deviceId)+'.ini'):
                template = Template(TEMPLATE_STR)
                content = template.render(serverAdd=frpServerIp, serverPort=frpServerPort, localIp=localIp,
                                          localPort=localPort,
                                          remotePort=remotePort)
                with open(settings.DIR_OF_INI + str(deviceId) + ".ini", "w") as file:
                    file.write(content)
                    file.close()
            # 开启frp
            new_pid = start_frpc(deviceId)
            if new_pid > 0:
                back_msg.res = 1
                back_msg.deviceId = deviceId
                back_msg.deviceState = 1
                back_msg.pid = new_pid

        return JsonResponse(back_msg.__dict__)
    except Exception as e:
        logging.error(e)
        back_msg.strData = str(e)
        return JsonResponse(back_msg.__dict__)
    finally:
        return JsonResponse(back_msg.__dict__)


@require_POST
def stop_device(request):
    post_data = json.loads(request.body.decode('utf-8'))
    back_msg = BackMsg()
    try:
        deviceId = post_data['id']
        pid = post_data['pid']
        if os.name == 'posix':
            res = stop_frpc(pid=pid)
            back_msg.res = 1
            back_msg.deviceId = deviceId
            back_msg.deviceState = 0
            back_msg.pid = 0
            if res != 1:
                back_msg.strData = 'onlineBox未找到该设备进程'

        return JsonResponse(back_msg.__dict__)
    except Exception as e:
        logging.error(e)
        back_msg.strData = str(e)
        return JsonResponse(back_msg.__dict__)
    finally:
        return JsonResponse(back_msg.__dict__)


@require_POST
def device_status(request):
    """
    查询device的状态 远程状态， 在线状态
    :param request: 固定的请求格式
    :return: 固定的响应消息格式
    """
    post_data = json.loads(request.body.decode('utf-8'))
    back_msg = BackMsg()
    try:
        deviceId = post_data['id']
        pid = post_data['pid']
        localIp = post_data['localIp']
        # 查询该id的frp进程是否正常 判断远程开启状态
        grep_command = f"ps -ef | grep ini/{deviceId}.ini"
        grep_process = subprocess.Popen(grep_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        grep_output, grep_error = grep_process.communicate()
        if grep_output:
            lines = grep_output.strip().split('\n')
            for line in lines:
                # 提取进程号（第二列）
                parts = line.split()
                if len(parts) >= 2:
                    back_msg.pid = int(parts[1])
        else:
            # 如果输出为空，表示未找到匹配的进程
            back_msg.pid = 0

        # 查询该ip port的连通状态判断是否在线
        ping_process = subprocess.Popen(['ping', '-c', '1', '-W', '1', localIp], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        ping_output, ping_error = ping_process.communicate()
        ping_output = ping_output.decode('utf-8')
        if "1 received" in ping_output:
            back_msg.deviceState = 1
        else:
            back_msg.deviceState = 0

        back_msg.res = 1
        return JsonResponse(back_msg.__dict__)
    except Exception as e:
        logging.error(e)
        back_msg.strData = str(e)
        return JsonResponse(back_msg.__dict__)
    finally:
        return JsonResponse(back_msg.__dict__)


def start_frpc(id):
    """
    :param id: deviceId
    :return: 0: error pid: 进程号
    """
    try:
        if os.name != 'posix':
            return 1
        # 执行Shell脚本并捕获输出
        command = ['bash', '/iecube/onlineBox/frp/start_frp.sh', str(id)]
        output = subprocess.run(command, capture_output=True, text=True, check=True)
        # 返回Shell脚本的输出（pid）
        pid = int(output.stdout.strip())
        return pid
    except subprocess.CalledProcessError as e:
        logging.error("subprocess error: " + e.stdout)
        return 0


def stop_frpc(pid):
    """
    :param pid: frp进程号
    :return: 0 进程本来不存在/失败； 1 成功 killed
    """
    try:
        if pid == 0:
            return 1
        if os.name != 'posix':
            return 1
        command = ['bash', '/iecube/onlineBox/frp/stop_frp.sh', str(pid)]
        output = subprocess.run(command, capture_output=True, text=True, check=True)
        res = int(output.stdout.strip())
        return res
    except subprocess.CalledProcessError as e:
        logging.error("subprocess error: " + e.stdout)
        return 0
