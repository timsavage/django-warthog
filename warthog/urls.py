# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf.urls import url
from .views import CmsPreview

urlpatterns = [
    url(r'^_preview/(\d+)/$', CmsPreview.as_view(), name='warthog-preview'),
]
