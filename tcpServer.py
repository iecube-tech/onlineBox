import socket
import threading
import json
import requests


TYPE_URL = {
    'add': '/device/add/',
    'del': '/device/del/',
}


def send_request(url, data):
    # 要设置的请求头
    headers = {
        # 'Content-Type': 'application/json',  # 设置内容类型
        'Content-Type': 'application/json',
        'Cross-Origin-Opener-Policy': 'same-origin',
        'X-Content-Type-Options': 'same-origin',
    }
    baseUrl = 'http://127.0.0.1:9000'
    response = requests.post(baseUrl+url, headers=headers, data=data)
    return response


# 处理客户端连接的函数
def handle_client(client_socket, address):
    print(f"[*] Accepted connection from {address[0]}:{address[1]}")
    # 接收客户端发送的数据
    client_socket.settimeout(20)
    back_msg = {'res': 0, 'strData': ''}
    try:
        recv = client_socket.recv(1024)
        message = json.loads(recv.decode('utf-8'))
        print(f"[*] Received:{message}")

        if message['type'] in TYPE_URL:
            data = message['deviceDetail']   # type(data)> dict
            response = send_request(TYPE_URL[message['type']], json.dumps(data))  # 发送过去接收到的类型为 <class 'str'>
        else:
            back_msg['strData'] = '非正确指令'
        # 返回消息给客户端

        # res = json.dumps(back_msg).encode('utf-8')
        res = str(response.json()).encode('utf-8')
        print(f"[*] Sent: {res}")
        client_socket.send(res)

    except socket.timeout:
        print(f"[!] Connection with {address[0]}:{address[1]} timed out")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        # 关闭客户端连接
        client_socket.close()
        print(f"[*] Connection with {address[0]}:{address[1]} closed")


# 主函数
def main():
    # 创建一个 IPv4 TCP 套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 绑定服务器地址和端口
    server_socket.bind(("0.0.0.0", 4900))

    # 开始监听客户端连接，允许最多5个连接排队
    server_socket.listen(5)
    print("[*] Listening on 127.0.0.1:4900")
    try:
        while True:
            # 接受客户端连接
            client_socket, address = server_socket.accept()

            # 创建一个线程来处理客户端连接
            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.start()
    except KeyboardInterrupt:
        print("[!] Server shutting down...")
    finally:
        # 关闭服务器套接字
        server_socket.close()


if __name__ == "__main__":
    main()
