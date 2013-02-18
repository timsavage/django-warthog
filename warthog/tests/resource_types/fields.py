# coding=utf-8
from django import test
from ...resource_types import fields


class ResourceFieldBaseTestCase(test.TestCase):

    def test_to_database(self):
        target = fields.ResourceFieldBase()