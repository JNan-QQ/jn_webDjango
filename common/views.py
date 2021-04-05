import os
from random import randint
from django.contrib.auth import authenticate, login, logout
import json

from django.contrib.auth.hashers import make_password
from django.db.models import F
from django.http import HttpResponse, StreamingHttpResponse, FileResponse
from django.shortcuts import render

from lib.sharaJR import JR,PaperProcess,Process
from .models import User,News,Notice,\
    Paper,Config,UserPaperThumbUp,StudentTeacherRelation,WF_Design_DataMgr,WF_Design
from JnUniversity.settings import UPLOAD_DIR

class LoginHandler:
    def Handler(self,request):
        # 从请求获取body消息体中,并放入request对象的params中
        request.params = json.loads(request.body)
        action = request.params.get('action')
        if action == 'signin':
            return self.Signin(request)
        elif action == 'signout':
            return self.Signout(request)
        else:
            return JR({'ret':2,'msg':'action参数错误！'})

    def Signin(self,request):
        userName = request.params.get('username')
        passWord = request.params.get('password')
        # 使用 Django auth 库里面的 方法校验用户名、密码
        user = authenticate(username=userName, password=passWord)

        if user is None:
            return JR({'ret':1,'msg':'没有找到该用户！'})
        if not user.is_active:
            return JR({'ret': 1, 'msg': '该用户已被禁用！'})
        login(request, user)
        # 在session中存入用户类型
        request.session['usertype'] = user.usertype
        request.session['username'] = user.username
        request.session.set_expiry(0)
        return JR({
                    'ret': 0,
                    'usertype':user.usertype,
                    'userid':user.id,
                    'realname':user.realname
                    })

    def Signout(self,request):
        logout(request)
        request.session.flush()
        return JR({'ret':0})

class AccountHandler:
    def Handler(self,request):
        # 将请求参数统一放入request 的 params 属性中，方便后续处理
        # GET请求 参数 在 request 对象的 GET属性中
        if request.session.get('usertype') != 1:
            return JR({'ret': 5 ,'msg': f'您没有权限操作'})
        if request.method == 'GET':
            request.params = request.GET
        # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
        elif request.method in ['POST', 'PUT', 'DELETE']:
            # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
            request.params = json.loads(request.body)
        else:
            return JR({'ret':1,'msg':'请求方式错误！'})

        # 根据不同的action分派给不同的函数进行处理
        action = request.params.get('action')
        if action == 'listbypage':
            return self.listbypage(request)
        elif action == 'addone':
            return self.addone(request)
        elif action == 'modifyone':
            return self.modifyone(request)
        elif action == 'deleteone':
            return self.deleteone(request)
        else:
            return JR({'ret':2,'msg':'action参数错误！'})

    def listbypage(self,request):
        pagenum = int(request.params.get('pagenum'))
        pagesize = int(request.params.get('pagesize'))
        keywords = request.params.get('keywords')
        ret = User.listbypage(pagenum,pagesize,keywords)
        return JR(ret)


    def addone(self,request):
        data = request.params.get('data')
        ret = User.addone(data)
        return JR(ret)

    def modifyone(self,request):
        accountid = request.params.get('id')
        newdata = request.params.get('newdata')
        ret = User.modifyone(accountid,newdata)
        return JR(ret)


    def deleteone(self,request):
        accountid = request.params.get('id')
        ret = User.deleteone(accountid)
        return JR(ret)

class NoticeHandler:
    def __init__(self):
        self.mode = Notice
        self.key = False

    def Handler(self, request):
        # 将请求参数统一放入request 的 params 属性中，方便后续处理
        # GET请求 参数 在 request 对象的 GET属性中
        if request.session.get('usertype') is None:
            return JR({'ret': 5 ,'msg': f'您没有登陆'})

        if request.method == 'GET':
            request.params = request.GET
        # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
        elif request.method in ['POST', 'PUT', 'DELETE']:
            # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
            request.params = json.loads(request.body)
        else:
            return JR({'ret': 1, 'msg': '请求方式错误！'})

        # 根据不同的action分派给不同的函数进行处理
        action = request.params.get('action')
        if action == 'listbypage':
            return self.listbypage(request)
        elif action == 'listbypage_allstate':
            return self.listbypage_allstate(request)
        elif action == 'listminebypage':
            return self.listminebypage(request)
        elif action == 'getone':
            return self.getone(request)
        elif action == 'banone':
            return self.babone(request)
        elif action == 'publishone':
            return self.publishone(request)
        elif action == 'holdone':
            return self.holdone(request)
        elif action == 'addone':
            return self.addone(request)
        elif action == 'modifyone':
            return self.modifyone(request)
        elif action == 'deleteone':
            return self.deleteone(request)
        else:
            return JR({'ret': 2, 'msg': 'action参数错误！'})

    def listbypage(self, request):
        pagenum = int(request.params.get('pagenum'))
        pagesize = int(request.params.get('pagesize'))
        keywords = request.params.get('keywords')
        ret = self.mode.listbypage(pagenum,pagesize,keywords)
        return JR(ret)

    def listbypage_allstate(self, request):
        if request.session.get('usertype') !=1:
            return JR({'ret': 5, 'msg': f'您没有权限操作'})

        pagenum = int(request.params.get('pagenum'))
        pagesize = int(request.params.get('pagesize'))
        keywords = request.params.get('keywords')
        ret = self.mode.listbypage(pagenum,pagesize,keywords,onlyPublished=False)
        return JR(ret)

    def listminebypage(self,request):
        if request.session.get('usertype') == 1:
            return JR({'ret': 5, 'msg': f'您没有权限操作'})
        cid = request.user.id
        pagenum = int(request.params.get('pagenum'))
        pagesize = int(request.params.get('pagesize'))
        keywords = request.params.get('keywords')
        ret = self.mode.listbypage(pagenum, pagesize, keywords,checkauthorid=cid)
        return JR(ret)

    def getone(self,request):
        accountid = request.params.get('id')
        ret = self.mode.getone(accountid)
        return JR(ret)

    def babone(self,request):
        if request.session.get('usertype') != 1:
            return JR({'ret': 5, 'msg': f'您没有权限操作'})
        accountid = request.params.get('id')
        ret = self.mode.setstatus(accountid,3)
        return JR(ret)

    def publishone(self,request):
        if request.session.get('usertype') !=1:
            cid = request.user.id
        else:
            cid = None
        accountid = request.params.get('id')
        ret = self.mode.setstatus(accountid, 1)
        return JR(ret)

    def holdone(self,request):
        if request.session.get('usertype') ==1:
            cid = None
        else:
            cid = request.user.id
        print(cid)
        accountid = request.params.get('id')
        ret = self.mode.setstatus(accountid,2,checkauthorid=cid)
        return JR(ret)

    def addone(self, request):
        data = request.params.get('data')
        uid = request.user.id
        ret = self.mode.addone(data,uid)
        return JR(ret)

    def modifyone(self, request):
        if request.session.get('usertype') != 1:
            cid = request.user.id
        else:
            cid = None
        accountid = request.params.get('id')
        newdata = request.params.get('newdata')
        ret = self.mode.modifyone(accountid, newdata,checkauthorid=cid)
        return JR(ret)

    def deleteone(self, request):
        if request.session.get('usertype') != 1:
            cid = request.user.id
        else:
            cid = None
        accountid = request.params.get('id')
        ret = self.mode.deleteone(accountid,checkauthorid=cid)
        return JR(ret)

class NewsHandler(NoticeHandler):
    def __init__(self):
        super().__init__()
        self.mode = News


class PaperHandler(NoticeHandler):
    def __init__(self):
        super().__init__()
        self.mode = Paper

class UploadHandler:
    def Handler(self,request):
        uploadfile = request.FILES['upload1']
        filetype = uploadfile.name.split('.')[-1]
        if filetype not in ['jpg','png']:
            return JR({'ret':12,'msg':'文件类型错误'})
        if uploadfile.size > 10*1024*1024:
            return JR({'ret': 13, 'msg': '文件太大'})

        filename = f'{request.user.id}_{randint(1,999)}.{filetype}'
        with open(f'{UPLOAD_DIR}/{filename}','wb') as fb:
            by = uploadfile.read()
            fb.write(by)
        return JR({'ret': 0, 'url':f'/upload/{filename}'})

class ConfigHandler:
    def Handler(self,request):
        # 将请求参数统一放入request 的 params 属性中，方便后续处理
        # GET请求 参数 在 request 对象的 GET属性中
        if request.method == 'GET':
            request.params = request.GET
        # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
        elif request.method in ['POST', 'PUT', 'DELETE']:
            # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
            request.params = json.loads(request.body)
        else:
            return JR({'ret':1,'msg':'请求方式错误！'})

        # 根据不同的action分派给不同的函数进行处理
        action = request.params.get('action')
        if action == 'gethomepagebyconfig':
            return self.gethomepagebyconfig(request)
        if action == 'set':
            return self.set(request)
        if action == 'get':
            return self.get(request)
        else:
            return JR({'ret':2,'msg':'action参数错误！'})

    def gethomepagebyconfig(self,request):
        ret = Config.gethomepagebyconfig()
        return JR(ret)

    def get(self,request):
        if request.session.get('usertype') != 1:
            print(request.session.get('usertype'))
            return JR({'ret': 5 ,'msg': f'您没有权限操作'})
        name = request.params.get('name')
        ret = Config.get(name)
        return JR(ret)

    def set(self,request):
        if request.session.get('usertype') != 1:
            print(request.session.get('usertype'))
            return JR({'ret': 5 ,'msg': f'您没有权限操作'})
        name = request.params.get('name')
        value = request.params.get('value')
        ret = Config.set(name,value)
        return JR(ret)

class EtcHandler:
    def Handler(self,request):
        # 将请求参数统一放入request 的 params 属性中，方便后续处理
        # GET请求 参数 在 request 对象的 GET属性中
        if request.method == 'GET':
            request.params = request.GET
        # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
        elif request.method in ['POST', 'PUT', 'DELETE']:
            # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
            request.params = json.loads(request.body)
        else:
            return JR({'ret':1,'msg':'请求方式错误！'})

        # 根据不同的action分派给不同的函数进行处理
        action = request.params.get('action')
        if action == 'getmyprofile':
            return self.getmyprofile(request)
        elif action == 'setmyprofile':
            return self.setmyprofile(request)
        elif action == 'listteachers':
            return self.listteachers(request)
        elif action == 'thumbuporcancel':
            return self.thumbuporcancel(request)
        else:
            return JR({'ret':2,'msg':'action参数错误！'})

    def getmyprofile(self,request):
        usertype = request.session.get('usertype')
        uid = request.user.id
        qs = User.objects.annotate(userid=F('id')).filter(id=uid).values("userid","username","usertype","realname")
        ret = list(qs)[0]
        if usertype == 2000:
            ret1 = StudentTeacherRelation.getTeacherOfStudent(uid)
            ret['teacher'] = ret1['teacher']
        return JR({'ret': 0, 'profile': ret})

    def thumbuporcancel(self,request):
        paperid = request.params.get('paperid')
        ret = UserPaperThumbUp.thumbUpOrCancel(request.user.id,paperid)
        return JR(ret)

    def setmyprofile(self,request):
        usertype = request.session.get('usertype')
        newdata = request.params.get('newdata')
        user = User.objects.get(id=request.user.id)
        if usertype == 3000:
            if 'realname' in newdata:
                user.realname = newdata['realname']
            if 'password' in newdata:
                user.password = make_password(newdata['password'])

        elif usertype == 2000:
            StudentTeacherRelation.setTeacherOfStudent(user.id,newdata['teacherid'])
            if 'realname' in newdata:
                user.realname = newdata['realname']
            if 'password' in newdata:
                user.password = make_password(newdata['password'])
        user.save()
        return JR({'ret':0})

    def listteachers(self,request):
        qs = User.objects.filter(usertype=3000).values('id', 'realname')
        rea = list(qs)
        return JR({'ret': 0, 'items': rea})

class WfHandler:
    def Handler(self,request):
        # 将请求参数统一放入request 的 params 属性中，方便后续处理
        # GET请求 参数 在 request 对象的 GET属性中
        if request.method == 'GET':
            request.params = request.GET
        # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
        elif request.method in ['POST', 'PUT', 'DELETE']:
            # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
            request.params = json.loads(request.body)
        else:
            return JR({'ret':1,'msg':'请求方式错误！'})

        # 根据不同的action分派给不同的函数进行处理
        action = request.params.get('action')
        if action == 'listbypage':
            return self.listbypage(request)
        elif action == 'getone':
            return self.getone(request)
        elif action == 'stepaction':
            return self.stepaction(request)
        elif action == 'getstepactiondata':
            return self.getstepactiondata(request)
        else:
            return JR({'ret':2,'msg':'action参数错误！'})

    def listbypage(self,request):
        pagenum = int(request.params.get('pagenum'))
        pagesize = int(request.params.get('pagesize'))
        keywords = request.params.get('keywords')
        ret = WF_Design_DataMgr.list(pagenum, pagesize, keywords)
        return JR(ret)

    def getone(self,request):
        wf_id = request.params.get('wf_id')
        withwhatcanido = request.params.get('withwhatcanido')
        key1 = request.params.get('key')
        uid = request.user.id
        if wf_id == '-1':
            return JR({
                          "ret": 0,
                          "rec": {
                            "id": -1,
                            "creatorname": "",
                            "title": "",
                            "currentstate": "",
                            "createdate": ""
                          },
                'whaticando': PaperProcess['开始']
            })
        else:
            ret = WF_Design_DataMgr.getone(wf_id, withwhatcanido)
            stuid = WF_Design.objects.get(id=wf_id).creator_id
            itt = WF_Design.objects.get(id=wf_id).currentstate
            if uid == stuid:
                if itt not in ['主题已驳回','主题已通过','已评分']:
                    ret['whaticando'] = [{'name': '等待老师审批'}]
                elif itt == '已评分':
                    ret['whaticando'] = [{'name': '流程结束'}]
                else:
                    ret['whaticando'] = PaperProcess[itt]
            elif uid == StudentTeacherRelation.objects.get(student_id=stuid).teacher_id:
                if itt not in ['主题已创建','学生已提交毕业设计','已评分']:
                    ret['whaticando'] = [{'name': '等待学生创建'}]
                elif itt == '已评分':
                    ret['whaticando'] = [{'name': '流程结束'}]
                else:
                    ret['whaticando'] = PaperProcess[itt]
            return JR(ret)

    def stepaction(self,request):
        data = request.params.get('submitdata')
        wf_id = request.params.get('wf_id')
        key1 = request.params.get('key')
        uid = request.user.id
        if wf_id == -1:
            ret = WF_Design_DataMgr.create \
                (data[0]['value'], uid, '开始', data, '主题已创建')
        else:
            stuid = WF_Design.objects.get(id=wf_id).creator_id

            keyl = Process(key1)
            if uid == stuid:
                print(keyl[2])
                if keyl[2] == 1:
                    return JR({'ret':123,'msg':'无权限操作'})
                else:
                    ret = WF_Design_DataMgr.update(wf_id,uid,keyl[0],data,keyl[1])
            elif uid == StudentTeacherRelation.objects.get(student_id=stuid).teacher_id:
                if keyl[2] == 0:
                    return JR({'ret':123,'msg':'无权限操作'})
                else:
                    ret = WF_Design_DataMgr.update(wf_id, uid, keyl[0], data, keyl[1])
        return JR({"ret": 0, "wf_id": ret.id})

    def getstepactiondata(self,request):
        step = int(request.params.get('step_id'))
        ret = WF_Design_DataMgr.getStepActionData(step)
        return JR(ret)

# ----------------------------------------------------


class Files1:

    def files_upload(self,request):
        # 请求方法为POST时,进行处理;
        if request.method == "POST":
            # 获取上传的文件,如果没有文件,则默认为None;
            File = request.FILES.get("myfile", None)
            if File is None:
                return HttpResponse("no files for upload!")
            else:
                # 打开特定的文件进行二进制的写操作;
                with open("D:\手机电脑共享\jn\Files\save\%s-%s" %(randint(100,999),File.name), 'wb+') as f:
                    # 分块写入文件;
                    for chunk in File.chunks():
                        f.write(chunk)
                return JR({'ret':0,'mmsg':'%s上传成功' % File.name})
        else:
            filepath = 'D:\手机电脑共享\jn\Files\save'
            file = os.listdir(filepath)
            str1 = '<tr>'
            for i in file:
                str1 += f'<td><a href ="http://127.0.0.' \
                        f'1/files/download?action={i}"> {i} </a><td/><br/>'
            str1 += '<tr/>'

            return render(request, 'files.html',{'file_list': str1})


    def files_download(self,request):
        filename = request.GET.get('action')
        filepath = 'Files/save/%s'%filename

        def file_iterator(file, chunk_size=512):
            with open(file) as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        response = StreamingHttpResponse(file_iterator(filepath))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)
        return response






