import urllib.parse
from utils import log


# 定义一个 class 用于保存请求的数据
class Request(object):
    def __init__(self, request_data):
        r = request_data
        self.raw_data = r
        log("akira request log:", r)
        self.method = r.split()[0]
        self.path = r.split()[1]
        # 把 body 放入 request 中
        self.body = r.split('\r\n\r\n', 1)[1]
        #
        self.query = {}
        self.headers = {}
        self.cookies = {}
        #
        path, query = self.parsed_path()
        self.path = path
        self.query = query
        # 解析 HTTP header 和 cookie
        self.add_headers()
        self.add_cookies()
        log('Request: path and query', path, query)

    def add_cookies(self):
        """
        height=169; user=gua
        """
        '''
        Cookie:user=gua;login_time=xx;
        =>
        {
        'user':'gua',
        'login_time':'xx',
        }
        '''
        cookies = self.headers.get('Cookie', '')
        kvs = cookies.split('; ')
        log('cookie', kvs)
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    def add_headers(self):
        """
        Accept-Language: zh-CN,zh;q=0.8
        Cookie: height=169; user=gua
        """
        r = self.raw_data
        # 把 header 拿出来
        header = r.split('\r\n\r\n', 1)[0]
        lines = header.split('\r\n')[1:]
        # lines = header.split('\r\n')
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v

    def parsed_path(self):
        """
        /gua?message=hello&author=gua
        {
            'message': 'hello',
            'author': 'gua',
        }
        """
        path = self.path
        index = path.find('?')
        if index == -1:
            return path, {}
        else:
            path, query_string = path.split('?', 1)
            args = query_string.split('&')
            query = {}
            for arg in args:
                k, v = arg.split('=')
                query[k] = v
            return path, query

    def form(self):
        body = urllib.parse.unquote(self.body)
        print('form', self.body)
        # print('parsed body', body)
        args = body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        print('form()', f)
        return f
