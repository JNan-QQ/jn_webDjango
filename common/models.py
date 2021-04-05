import traceback
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator,EmptyPage
from django.db import models, transaction, IntegrityError
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.utils import timezone


class User(AbstractUser):

    id = models.BigAutoField(primary_key=True)
    # 用户类型
    # 1： 超管 | 1000： 普通管理员  | 2000：学生  |  3000： 老师
    usertype = models.PositiveIntegerField()
    # 真实姓名
    realname = models.CharField(max_length=30, db_index=True)
    # 学号
    studentno = models.CharField(
        max_length=10,
        db_index=True,
        null=True, blank=True
    )
    # 备注描述
    desc = models.CharField(max_length=500, null=True, blank=True)
    REQUIRED_FIELDS = ['usertype', 'realname']
    class Meta:
        db_table = "by_user"

    @staticmethod
    def addone(data):
        if 'username' in data:#判断用户名是否存在
            if User.objects.filter(username=data['username']).exists():
                return {'ret':1,'msg':'用户名已存在'}
        try:
            user = User.objects.create(
                username=data['username'],
                realname=data['realname'],
                password=make_password(data['password']),
                studentno=data['studentno'],
                desc=data['desc'],
                usertype=data['usertype']
            )
            return {'ret':0,'id':user.id}
        except:
            err = traceback.format_exc()
            return {'ret':2,'msg':err}

    @staticmethod
    def listbypage(pagenum,pagesize,keywords):
        try:
            # # 返回一个 QuerySet 对象 ，包含所有的表记录
            # qs = Medicine.objects.values()
            # .order_by('-id') 表示按照 id字段的值 倒序排列
            # 这样可以保证最新的记录显示在最前面
            qs = User.objects.values('id','username',
                'realname','studentno','desc','usertype').order_by('-id')

            if keywords:
                conditions = [Q(realname__contains=one) for one in keywords.split(' ')]
                query = Q()
                for condition in conditions:
                    query &= condition
                qs = qs.filter(query)

            # 使用分页对象，设定每页多少条记录
            pgnt = Paginator(qs, pagesize)
            # 从数据库中读取数据，指定读取其中第几页
            page = pgnt.page(pagenum)
            # 将 QuerySet 对象 转化为 list 类型
            # 否则不能 被 转化为 JSON 字符串
            retlist = list(page)

            return {'ret': 0, 'items': retlist, 'total': pgnt.count,'keywords':keywords}
        except EmptyPage:
            return {'ret':0,'items':[],'total':0,'keywords':keywords}
        except:
            err = traceback.format_exc()
            return {'ret':2,'msg':err}

    @staticmethod
    def modifyone(accountid,newdata):
        try:
            # 根据 id 从数据库中找到相应的客户记录
            user = User.objects.get(id=accountid)
        except User.DoesNotExist:
            return {'ret': 1,'msg':f'id为{accountid}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}

        if 'password' in newdata:
            user.password = make_password(newdata.pop('password'))
        if 'username' in newdata:
            if User.objects.filter(username=newdata['username']).exists():
                return {'ret':1,'msg':'用户名已存在'}
        for key,value in newdata.items():
            setattr(User,key,value)
        # 注意，一定要执行save才能将修改信息保存到数据库
        user.save()
        return {'ret': 0}

    @staticmethod
    def deleteone(accountid):
        try:
            # 根据 id 从数据库中找到相应的客户记录
            user = User.objects.get(id=accountid)
            user.delete()
            return {'ret':0}
        except User.DoesNotExist:
            return {'ret': 1,'msg':f'id为{accountid}的用户不存在'}
        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}


# 文章，作为基类使用
class Article(models.Model):
    # 改用 BigAuto 支持更大的记录条数
    id = models.BigAutoField(primary_key=True)
    # 创建日期
    pubdate = models.DateTimeField(default=timezone.now,
                                   db_index=True)
    # 作者
    author = models.ForeignKey(User,
                               on_delete=models.PROTECT,
                               db_index=True)
    # 标题
    title = models.CharField(max_length=100, db_index=True)
    # 内容
    content = models.TextField(max_length=50000,
                               null=True,blank=True)
    # 状态 1: 发布 2：草稿 3:封禁
    # 管理员可以封禁  作者自己可以撤回
    # 要作为索引，因为会根据它来过滤搜索
    status = models.PositiveSmallIntegerField(default=1,
                                              db_index=True)
    STATUS_PUBLISHED = 1
    STATUS_HOLD      = 2
    STATUS_BANED     = 3
    class Meta:
        # 设置本身为为抽象，否则migrate会产生表
        abstract = True

    @classmethod
    def addone(cls,data,uid):
        try:
            record = cls.objects.create(
                author_id=uid,
                title=data['title'],
                content=data['content']
            )
            return {'ret': 0, 'id': record.id}

        except Exception:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}

    @classmethod
    def listbypage(cls, pagenum, pagesize, keywords, fields=None,
             checkauthorid=None,
             onlyPublished=True,
             withoutContent=False):
        # keywords 是 过滤 title里面包含的关键字
        # checkauthorid 是根据 作者id 过滤
        # onlyPublished 是 只显示 发布状态的
        try:
            if fields:
                columns = fields.split(',')
            else:
                columns = ['id', 'pubdate', 'author', 'author__realname','title', 'status']
                if not withoutContent:
                    columns.append('content')

            qs = cls.objects.values(*columns).order_by('-id')

            if checkauthorid:
                qs = qs.filter(author_id=checkauthorid)

            if onlyPublished:
                qs = qs.filter(status=cls.STATUS_PUBLISHED)

            if keywords:
                qlist = [Q(title__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in qlist:
                    query &= condition
                qs = qs.filter(query)

            pgnt = Paginator(qs, pagesize)

            retObj = list(pgnt.page(pagenum))

        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': keywords}

        return {'ret': 0, 'items': retObj, 'total': pgnt.count, 'keywords': keywords}

    @classmethod
    def getone(cls,oid, checkauthorid=None):
        try:
            # 根据 id 从数据库中找到相应的记录
            qs = cls.objects.filter(id=oid)\
                .values('id', 'pubdate', 'author',
                        'author__realname','title', 'content','status')

            if checkauthorid:
                qs = qs.filter(author_id=checkauthorid)

            if qs.count() == 0 :
                return {
                    'ret': 1,
                    'msg': f'id 为`{oid}`的记录不存在'
                }

            rec = list(qs)[0]
            return {'ret': 0, 'rec': rec}

        except:
            err = traceback.format_exc()
            return {'ret': 2, 'msg': err}

    @classmethod
    def getmany(cls, idlist):
        try:
            # 根据 id 从数据库中找到相应的记录
            qs = cls.objects.filter(pk__in=idlist)\
                .values('id', 'pubdate', 'author',
                        'author__realname','title', 'status')

            return {'ret': 0, 'items': list(qs)}

        except:
            err = traceback.format_exc()
            return {'ret': 1, 'msg': err}



    @classmethod
    def modifyone(cls, oid, newdata, checkauthorid=None):
        try:
            # 根据 id 从数据库中找到相应的客户记录
            rec = cls.objects.get(id=oid)
            if checkauthorid is not None:
                if rec.author_id != checkauthorid:
                    return {'ret': 5 ,'msg': f'您没有权限操作'}

            # 其他参数统一处理
            for field, value in newdata.items():
                setattr(rec, field, value)

            rec.save()
            return {'ret': 0}

        except cls.DoesNotExist:
            return {
                'ret': 1,
                'msg': f'id 为`{oid}`的记录不存在'
            }
        except:
            err = traceback.format_exc()
            return {'ret': 1, 'msg': err}

    @classmethod
    def deleteone(cls,oid, checkauthorid=None):
        # condition 是限制条件，比如只能删除自己发布的
        try:
            # 根据 id 从数据库中找到相应的客户记录
            rec = cls.objects.get(id=oid)
            if checkauthorid is not None:
                if rec.author_id != checkauthorid:
                    return {'ret': 5 ,'msg': f'您没有权限操作'}
            rec.delete()
            return {'ret': 0}
        except cls.DoesNotExist:
            return {
                'ret': 1,
                'msg': f'id 为`{oid}`的记录不存在'
            }
        except:
            err = traceback.format_exc()
            return {'ret': 1, 'msg': err}

    # 设置文章状态
    @classmethod
    def setstatus(cls,oid,status,checkauthorid=None):
        try:
            # 根据 id 从数据库中找到相应的客户记录
            rec = cls.objects.get(id=oid)
            if checkauthorid is not None:
                if rec.author_id != checkauthorid:
                    return {'ret': 5 ,'msg': f'您没有权限操作'}

            rec.status = status
            rec.save()
            return {'ret': 0, 'status': rec.status}

        except cls.DoesNotExist:
            return {
                'ret': 1,
                'msg': f'id 为`{oid}`的记录不存在'
            }
        except:
            err = traceback.format_exc()
            return {'ret': 1, 'msg': err}

# 公告
class Notice(Article):
    class Meta:
        db_table = "jn_notice"


# 新闻
class News(Article):

    class Meta:
        db_table = "jn_news"

# 论文
class Paper(Article):
    # 点赞数
    thumbupcount = models.PositiveIntegerField(default=0)
    class Meta:
        db_table = "jn_paper"


# 配置表
class Config(models.Model):
    # 配置项名称，目前主要是 homepage
    name = models.CharField(max_length=100, unique=True)
    # 内容，以json格式存储数据
    value = models.TextField(max_length=50000,null=True,default=None)
    class Meta:
        db_table = "jn_config"

    @classmethod
    def get(cls,name):
        if name not in ['homepage']:
            return {'ret': 2, 'msg': '不支持的配置项'}

        try:
            qs = cls.objects.filter(name=name)\
                .values('name','value')
            # 如果没有，就返回None
            if qs.count() == 0 :
                return {'ret': 0, 'value': None}

            rec = list(qs)[0]
            return {'ret': 0, 'value': rec['value']}

        except:
            err = traceback.format_exc()
            return {'ret': 1, 'msg': err}


    @classmethod
    def set(cls, name, value):
        try:
            rec = cls.objects.get(name=name)
            rec.value = value
            rec.save()
            return {'ret': 0}
        except cls.DoesNotExist:
            # 不存在，就创建记录
            cls.objects.create(name=name,value=value)
            return {'ret': 0}
        except:
            err = traceback.format_exc()
            return {'ret': 1, 'msg': err}

    @classmethod
    def gethomepagebyconfig(cls):
        try:
            rec = cls.objects.filter(name='homepage').values('value')
            reclist = eval(list(rec)[0].get('value'))
            print(type(reclist),reclist)
            news = reclist['news']
            notice = reclist['notice']
            paper = reclist['paper']
            new1 = []
            notice1 = []
            paper1 = []
            for ii in [list(News.objects.filter(id=i).values("id","pubdate",
                "author","author__realname","title","status")) for i in news]:
                new1.append(ii[0])
            for ii in [list(Notice.objects.filter(id=i).values("id","pubdate",
                "author","author__realname","title","status")) for i in notice]:
                notice1.append(ii[0])
            for ii in [list(Paper.objects.filter(id=i).values("id","pubdate",
                "author","author__realname","title","status")) for i in paper]:
                paper1.append(ii[0])
            return {'ret': 0,'info':{'news':new1,'notice':notice1,'paper':paper1}}
        except cls.DoesNotExist:
            return {'ret': 0,'info':{'news':[],'notice':[],'paper':[]}}
        except:
            err = traceback.format_exc()
            return {'ret': 1, 'msg': err}

# 用户点赞记录
class UserPaperThumbUp(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 通常数据库中，外键自动就是索引
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 我的点赞论文ID列表 这种格式： ,1,2,3,34,
    # 注意 第一个id 前面一定要有逗号，想一想，为什么
    thumbups = models.TextField(default=',')
    class Meta:
        db_table = "cimp_userpaperthumbup"

    @classmethod
    def thumbUpOrCancel(cls,userid,paperid):
        # 检查该用户对某个Paper的点赞是否存在
        utu = cls.objects.filter(user_id=userid).first()
        # 该用户还没有创建点赞记录
        if utu is None:
            # 创建一个
            utu = cls.objects.create(user_id=userid)
        paper = Paper.objects.get(id=paperid)
        #  该用户还没有对本paper点赞
        if f',{paperid},' not in utu.thumbups:
            # 点赞数加1
            paper.thumbupcount += 1
            # 在前面插入，而不是在后面添加 点赞
            # 因为 下次查询 通常就是最近点赞的，
            # 在前面会更快找到，这样性能较高
            utu.thumbups = f',{paperid}' + utu.thumbups
        #  该用户已经对本paper点赞，再次点击就是取消点赞
        else:
            # 点赞数减1
            paper.thumbupcount -= 1
            utu.thumbups = utu.thumbups.replace(f',{paperid}','')
        try:
            # 多项数据库操作必须放入事务
            with transaction.atomic():
                paper.save()
                utu.save()
            return {'ret': 0,'thumbupcount':paper.thumbupcount}
        except IntegrityError:
            return {'ret':5,'msg':'数据库操作失败'}


# 师生关系表
class StudentTeacherRelation(models.Model):
    # 关于 related_name 的作用，
    # 参考https://docs.djangoproject.com/en/3.0/topics/db/queries/#backwards-related-objects
    student = models.ForeignKey(User, on_delete=models.CASCADE,related_name='myteachers')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE,related_name='mystudents')
    # update_or_create 参考 https://docs.djangoproject.com/en/dev/ref/models/querysets/#update-or-create
    @staticmethod
    def setTeacherOfStudent(studentuid,teacheruid):
        StudentTeacherRelation.objects.update_or_create(
            # kargs 是寻找条件
            student_id = studentuid,
            # 如果能找到记录，就更新defaults里面的内容
            # 如果找不到记录， 就创建记录，
            # 字段是 kargs 和 defaults里面更新的内容
            defaults={'teacher_id': teacheruid}
        )

        return {'ret':0}

    # 获取学生的老师
    @staticmethod
    def getTeacherOfStudent(studentuid):
        stRelation = StudentTeacherRelation.objects.filter(student_id=studentuid).first()
        if stRelation:
            return {
                'ret': 0,
                'teacher':{
                    'id': stRelation.teacher.id,
                    'realname': stRelation.teacher.realname
                }
            }
        else:
            return {
                'ret': 0,
                'teacher' : {
                    'id': -1,
                    'realname': '尚未设置'
                }
            }


    # 获取老师的学生
    @staticmethod
    def getStudentsOfTeacher(teacheruid):
        qs = StudentTeacherRelation.objects.filter(teacher_id=teacheruid).values(
            'student_id','student__realname'
        )

        return {
                'ret': 0,
                'students' : list(qs)
        }



# 工作流表基类
class WF(models.Model):
    id = models.BigAutoField(primary_key=True)
    # 标题
    title = models.CharField(max_length=100, db_index=True,default='')
    # 创建人
    creator = models.ForeignKey(User,on_delete=models.PROTECT)
    # 创建日期
    createdate = models.DateTimeField(default=timezone.now,
                                   db_index=True)
    # 当前状态，也就是走到哪一步
    currentstate = models.CharField(max_length=50)


    class Meta:
        # 设置本身为为抽象，否则migrate会产生表
        abstract = True


#  工作流表每个操作步骤数据，分开存放，方便操作和提升效率
class WFStep(models.Model):
    id = models.BigAutoField(primary_key=True)

    # 本步骤操作人
    operator = models.ForeignKey(User, on_delete=models.PROTECT)

    # 操作日期
    actiondate = models.DateTimeField(default=timezone.now,
                                      db_index=True)
    # 操作名称
    actionname = models.CharField(max_length=50)

    # 操作数据记录
    actiondata = models.TextField(default='')

    # 操作完进入到什么状态
    nextstate = models.CharField(max_length=50)

    class Meta:
        # 设置本身为为抽象，否则migrate会产生表
        abstract = True

# 工作流数据管理 基类
class WFDataMgr:

    @classmethod
    def list(cls, pagenum, pagesize,keywords,fields=None,creatorids=None):
        '''
        列出 工作流记录
        :param pagenum:
        :param pagesize:
        :param keywords:  过滤 title里面包含的关键字
        :param fields:
        :param creatorids:  是根据 作者id 过滤，是列表，里面有多个id
        :param onlyPublished:
        :return:
        '''
        try:
            if fields:
                columns = fields.split(',')
            else:
                columns = ('id', 'creator', 'creator__realname','title', 'currentstate','createdate')

            qs = cls.WF_MODEL.objects.values(*columns).order_by('-id')

            if creatorids:
                qs = qs.filter(creator_id__in=creatorids)


            if keywords:
                qlist = [Q(title__contains=one) for one in keywords.split(' ') if one]
                query = Q()
                for condition in qlist:
                    query &= condition
                qs = qs.filter(query)

            pgnt = Paginator(qs, pagesize)

            # retObj = {'total':pgnt, 'content':pgnt.page(pagenum)}

            retObj = list(pgnt.page(pagenum))

        except EmptyPage:
            return {'ret': 0, 'items': [], 'total': 0, 'keywords': keywords}

        return {'ret': 0, 'items': retObj, 'total': pgnt.count, 'keywords': keywords}




    @classmethod
    def getone(cls,oid, getsteps=True):

        try:
            # 根据 id 从数据库中找到相应的记录
            # wf = cls.WF_MODEL.objects.filter(id=oid)\
            #     .values('id', 'creator', 'creator__realname','title', 'currentstate','createdate',
            #             'steps').first()

            wf = cls.WF_MODEL.objects.get(id=oid)


            rec = {
                'id': wf.id,
                'creatorname': wf.creator.realname,
                'title': wf.title,
                'currentstate': wf.currentstate,
                'createdate': wf.createdate,
            }

            # 获取工作流步骤数据
            if getsteps:
                qs2 = cls.WF_STEP_MODEL.objects.filter(wf_id=wf.id).values(
                    'id','operator__realname','actiondate','actionname','nextstate'
                )
                rec['steps'] = list(qs2)



            return {'ret': 0, 'rec': rec}

        except:
            err = traceback.format_exc()
            return {'ret': 1, 'msg': err}



    # 主要是获取该步骤的动作submitdata
    @classmethod
    def getStepActionData(cls,step_id):

        try:
            rec = cls.WF_STEP_MODEL.objects.get(id=step_id)
            print(rec.actiondata)
            return {'ret': 0, 'data':eval(rec.actiondata)}

        except:
            err = traceback.format_exc()
            return {'ret': 1, 'msg': err}




    @classmethod
    def create(cls,title,uid,actionname,actiondata,nextstate):
        with transaction.atomic():

            wf = cls.WF_MODEL.objects.create(
                title = title,
                creator_id = uid,
                currentstate = nextstate,
            )

            # 创建步骤表记录
            wfstep = cls.WF_STEP_MODEL.objects.create(
                operator_id = uid,
                actionname = actionname,
                actiondata = actiondata,
                nextstate = nextstate,
                wf = wf
            )

        return wf

    @classmethod
    def update(cls,wf_id,uid,actionname,actiondata,nextstate,title=None):
        '''

        :param wf_id:
        :param uid: 操作者userid
        :param actionname:
        :param actiondata:
        :param nextstate:
        :param title: 可能某个步骤需要更新整个工作流的title
        :return:
        '''
        with transaction.atomic():

            wf = cls.WF_MODEL.objects.get(pk=wf_id)
            wf.currentstate=nextstate
            if title is not None:
                wf.title = title
            wf.save()

            # 创建步骤表记录
            wfstep = cls.WF_STEP_MODEL.objects.create(
                operator_id = uid,
                actionname = actionname,
                actiondata = actiondata,
                nextstate = nextstate,
                wf_id = wf_id
            )

        return wf





# 毕业设计工作流
class WF_Design(WF):

    class Meta:
        db_table = "jn_wf_design"

# 毕业设计工作流表每个操作步骤数据
class WF_Design_Step(WFStep):
    # 对应哪个工作流记录
    wf = models.ForeignKey(WF_Design,
                           on_delete=models.PROTECT,
                           related_name='steps')

    class Meta:
        db_table = "jn_wf_design_step"


class WF_Design_DataMgr(WFDataMgr):

    WF_MODEL      = WF_Design
    WF_STEP_MODEL = WF_Design_Step
