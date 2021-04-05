# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   FileName:sharaJR.py
   Tool:    PyCharm
   Author:  姜楠
   date:    2021/3/20
-------------------------------------------------
"""
from django.http import JsonResponse

def JR(data,**args):
    return JsonResponse(data,json_dumps_params={'ensure_ascii':False},**args)

PaperProcess = {
    '开始':[

            {
                'name': '创建主题',
                'submitdata':[
                    {
                         'name': '毕业设计标题',
                         'type': 'text',
                         'check_string_len':{10:1000}
                     },
                    {
                         'name': '主题描述',
                         'type': 'richtext',
                         'check_string_len':{10:1000}
                    },
                ],
                'whocan':9,
                'next':'主题已创建',
                'key':'create_topic'
            },


    ],
    '主题已创建':[

            {
                'name': '驳回主题',
                'submitdata':[
                    {
                         'name': '驳回原因',
                         'type': 'richtext',
                         'check_string_len':{10:1000}
                    },
                ],
                'whocan':7,
                'next':'主题已驳回',
                'key':'reject_topic'
            },
            {
                'name': '批准主题',
                'submitdata':[
                    {
                         'name': '备注',
                         'type': 'richtext',
                         'check_string_len':{10:1000}
                    },
                ],
                'whocan':7,
                'next':'主题已通过',
                'key':'approve_topic'
            },

    ],
    '主题已驳回':[

            {
                'name': '修改主题',
                'submitdata':[
                    {
                         'name': '毕业设计标题',
                         'type': 'text',
                         'check_string_len':{10:1000}
                     },
                    {
                         'name': '主题描述',
                         'type': 'richtext',
                         'check_string_len':{10:1000}
                    },
                ],
                'whocan':9,
                'next':'主题已创建',
                'key':'create_topic'
            },


    ],
    '主题已通过':[

               {
                    'name': '提交毕设内容',
                    'submitdata':[
                        {
                             'name': '内容',
                             'type': 'richtext',
                             'check_string_len':{10:1000}
                        },
                    ],
                    'whocan':9,
                    'next':'学生已提交毕业设计',
                    'key':'create'
                },


    ],
    '学生已提交毕业设计':[

                {
                    'name': '评分',
                    'submitdata':[
                        {
                             'name': '得分',
                             'type': 'text',
                             'check_string_len':{10:1000}
                        },
                    ],
                    'whocan':7,
                    'next':'已评分',
                    'key':'end'
                },
                {
                    'name': '打回重做',
                    'submitdata':[
                        {
                             'name': '备注',
                             'type': 'richtext',
                             'check_string_len':{10:1000}
                        },
                    ],
                    'whocan':7,
                    'next':'主题已通过',
                    'key':'reject'
                },

    ],
    '已评分':[]
}

def Process(key):
    if key == 'reject_topic':
        return ['驳回主题','主题已驳回',1]
    elif key == 'approve_topic':
        return ['批准主题','主题已通过',1]
    elif key == 'create_topic':
        return ['修改主题','主题已创建',0]
    elif key == 'create':
        return ['提交毕设内容','学生已提交毕业设计',0]
    elif key == 'end':
        return ['评分','已评分',1]
    elif key == 'reject':
        return ['打回重做','主题已通过',1]