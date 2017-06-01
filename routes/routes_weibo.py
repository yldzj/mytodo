from models import User
from models import Weibo
from models import Comment

from .session import session
from utils import template
from utils import response_with_headers
from utils import redirect
from utils import error
from utils import http_response
from utils import log

Tweet = Weibo


def current_user(request):
    session_id = request.cookies.get('user', '')
    user_id = session.get(session_id, -1)
    u = User.find(user_id)
    return u


# 微博相关页面
def index(request):
    user_id = int(request.query.get('user_id', -1))
    user = User.find(user_id)
    if user is None:
        return redirect('/login')
    else:
        # 找到 user 发布的所有 weibo
        #weibos = Weibo.find_all(user_id=user_id)
        weibos = Weibo.all()
        body = template('weibo_index.html', weibos=weibos)
        return http_response(body)


def new(request):
    u = current_user(request)
    body = template('weibo_new.html')
    return http_response(body)


def add(request):
    u = current_user(request)
    # 创建微博
    form = request.form()
    w = Tweet(form)
    w.user_id = u.id
    w.save()
    return redirect('/weibo/index?user_id={}'.format(u.id))


def delete(request):
    u = current_user(request)
    # 删除微博
    weibo_id = request.query.get('id', None)
    weibo_id = int(weibo_id)
    w = Tweet.find(weibo_id)
    if u.id == w.user_id:
        Weibo.delete(id=weibo_id)
    return redirect('/weibo/index?user_id={}'.format(u.id))


def edit(request):
    weibo_id = request.query.get('id', -1)
    weibo_id = int(weibo_id)
    w = Tweet.find(weibo_id)
    if w is None:
        return error(request)
    # 生成一个 edit 页面
    body = template('weibo_edit.html',
                    weibo_id=w.id,
                    weibo_content=w.content)
    return http_response(body)


def delcoments(request):
    """
    	删除当前用户此条微博下的所有评论
    """
    u = current_user(request)
    weibo_id = request.query.get('id', None)
    weibo_id = int(weibo_id)
    w = Tweet.find(weibo_id)
    coments = Comment.find_all(weibo_id=weibo_id)
    if u.id == w.user_id:
           for m in coments:
             Comment.delete(weibo_id=weibo_id)
    return redirect('/weibo/index?user_id={}'.format(u.id))


def del_onecoment(request):
    """
    	删除自己的评论
    """
    u = current_user(request)
    comment_id = request.query.get('id', None)
    comment_id = int( comment_id)
    coments = Comment.find_by(id=comment_id)
    if u.id == coments.user_id:
           Comment.delete(id= comment_id)
    return redirect('/weibo/index?user_id={}'.format(u.id))


def update(request):
    u = current_user(request)
    form = request.form()
    # Tweet.update(form, user_id=u.id)
    content = form.get('content', '')
    weibo_id = int(form.get('id', -1))
    w = Tweet.find(weibo_id)
    if u.id != w.user_id:
        return error(request)
    w.content = content
    w.save()
    # 重定向到用户的主页
    return redirect('/weibo/index?user_id={}'.format(u.id))


def comment_add(request):
    user = current_user(request)
    # 创建微博
    form = request.form()
    c = Comment(form, user_id=user.id)
    # c.user_id = user.id
    c.save()
    # 找到微博的用户
    uid = c.weibo().user().id
    return redirect('/weibo/index?user_id={}'.format(uid))


# 定义一个函数统一检测是否登录
def login_required(route_function):
    def func(request):
        u = current_user(request)
        log('登录鉴定, user ', u)
        if u is None:
            # 没登录 不让看 重定向到 /login
            return redirect('/login')
        else:
            # 登录了, 正常返回路由函数响应
            return route_function(request)
    return func


route_dict = {
    '/weibo/index': index,
    '/weibo/new': login_required(new),
    '/weibo/edit': login_required(edit),
    '/weibo/add': login_required(add),
    '/weibo/update': login_required(update),
    '/weibo/delete': login_required(delete),
    '/weibo/delcoments':login_required(delcoments),
      '/weibo/del_onecoment' :login_required(del_onecoment),
    '/comment/add': login_required(comment_add),
}
