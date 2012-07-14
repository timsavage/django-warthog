from django.conf.urls import *
from warthog.views import CMSPreview

urlpatterns = patterns('',
    url(r'^_preview/(\d+)/$', CMSPreview.as_view(), name='warthog-preview'),
)
