# -*- coding=utf-8 -*-
# 开发人员 ：姜楠
# 开发时间 ：2021/2/22 16:54
# 文件名称 ：hosthand.PY
# 开发工具 ：PyCharm
from django.http import JsonResponse,HttpResponse
from django.contrib.auth import authenticate, login, logout

import json




def dispatcherBase(request,action2HandlerTable):
    # 将请求参数统一放入request 的 params 属性中，方便后续处理

    # GET请求 参数 在 request 对象的 GET属性中
    if request.method == 'GET':
        request.params = request.GET

    # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
    elif request.method in ['POST','PUT','DELETE']:
        # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
        request.params = json.loads(request.body)
    # 根据不同的action分派给不同的函数进行处理
    action = request.params['action']

    # 根据session判断用户是否是登录的管理员用户
    us = request.session.get('type')
    if us == 'super':
        pass
    elif us == 'dd':
        if action in ['listbypage','getone','listminebypage']:
            pass
        else:
            return JsonResponse({'cookid': us,'msg':'不是管理员账户'})

    if action in action2HandlerTable:
        handlerFunc = action2HandlerTable[action]
        return handlerFunc(request)

    else:
        return JsonResponse({'ret': 1, 'msg': 'action参数错误'})


def dispatcherBase1(request,action2HandlerTable):

    # 将请求参数统一放入request 的 params 属性中，方便后续处理

    # GET请求 参数 在 request 对象的 GET属性中
    if request.method == 'GET':
        request.params = request.GET

    # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
    elif request.method in ['POST','PUT','DELETE']:
        # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
        request.params = json.loads(request.body)


    # 根据不同的action分派给不同的函数进行处理
    action = request.params['action']

    # 根据session判断用户是否是登录的管理员用户
    us = request.session.get('type')
    if us == 'dd':
        if action in ['banone','publishone','set','get']:
            return JsonResponse({'ret':1,'msg':'没有操作权限'})
        else:
            pass
    elif us == 'super':
        pass

    if action in action2HandlerTable:
        handlerFunc = action2HandlerTable[action]
        return handlerFunc(request)

    else:
        return JsonResponse({'ret': 1, 'msg': 'action参数错误'})