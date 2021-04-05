"""JnUniversity URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import common.views as views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/sign', views.LoginHandler().Handler),
    path('api/account', views.AccountHandler().Handler),
    path('api/notice',views.NoticeHandler().Handler),
    path('api/news',views.NewsHandler().Handler),
    path('api/paper',views.PaperHandler().Handler),
    path('api/config',views.ConfigHandler().Handler),
    path('api/etc',views.EtcHandler().Handler),
    path('api/wf_graduatedesign',views.WfHandler().Handler),
    path('api/upload',views.UploadHandler().Handler),
    path('files/upload',views.Files1().files_upload),
    path('files/download',views.Files1().files_download)
]
#+  static("/", document_root="./z_dist")
# + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
