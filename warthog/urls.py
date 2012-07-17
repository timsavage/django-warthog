from django.conf.urls import *
from warthog.views import CmsPreview

urlpatterns = patterns('',
    url(r'^_preview/(\d+)/$', CmsPreview.as_view(), name='warthog-preview'),
)
