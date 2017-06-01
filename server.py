import socket
from request import Request
from utils import log

from routes.routes_simpletodo import route_dict as simpletodo_routes
from routes.routes_static import route_static
from routes.routes_user import route_dict as user_routes
from routes.routes_weibo import route_dict as weibo_routes
from routes.routes_todo import route_dict as todo_routes


def error(request, code=404):
    """
    根据 code 返回不同的错误响应
    目前只有 404
    """
    # 之前上课我说过不要用数字来作为字典的 key
    # 但是在 HTTP 协议中 code 都是数字似乎更方便所以打破了这个原则
    e = {
        404: b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
    }
    return e.get(code, b'')


def response_for_path(request):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    path = request.path
    r = {
        '/static': route_static,
        # '/': route_index,
        # '/login': route_login,
        # '/messages': route_message,
    }
    # 注册微博的路由
    r.update(weibo_routes)
    r.update(todo_routes)
    # 注册 todo user 的路由
    r.update(simpletodo_routes)
    r.update(user_routes)
    response = r.get(path, error)
    return response(request)


def process_request(connection):
    r = connection.recv(1000)
    r = r.decode('utf-8')
    # log('ip and request, {}\n{}'.format(address, request))
    # 把原始请求数据传给 Request 对象
    request = Request(r)
    # 用 response_for_path 函数来得到 path 对应的响应内容
    response = response_for_path(request)
    log("akirayu response log:", response)
    # 把响应发送给客户端
    connection.sendall(response)
    # 处理完请求, 关闭连接
    connection.close()


def run(host='', port=3000):
    """
    启动服务器
    """
    import _thread
    # 初始化 socket 套路

    log('start at', '{}:{}'.format(host, port))
    with socket.socket() as s:
        # 使用 下面这句 可以保证程序重启后使用原有端口, 原因忽略
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)
        # 无限循环来处理请求
        while True:
            connection, address = s.accept()
            # 第二个参数类型必须是 tuple
            _thread.start_new_thread(process_request, (connection,))


if __name__ == '__main__':
    # 生成配置并且运行程序
    config = dict(
        host='',
        port=3000,
    )
    # 如果不了解 **kwargs 的用法, 上过基础课的请复习函数, 新同学自行搜索
    run(**config)
