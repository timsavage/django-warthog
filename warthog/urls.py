# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf.urls import *
from .views import CmsPreview

urlpatterns = patterns('',
    url(r'^_preview/(\d+)/$', CmsPreview.as_view(), name='warthog-preview'),
)
