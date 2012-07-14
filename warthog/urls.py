from django.conf.urls import *
from warthog.views import CMS

urlpatterns = patterns('',
    url(r'^_preview/', CMS.as_view()),
)