from django.db import models
from django import test
from warthog import cache


class CacheTest(models.Model):
    code = models.CharField(max_length=50, unique=True)
    other = models.IntegerField()

    class Meta:
        app_label = 'warthog_test'


class CacheTestCase(test.TestCase):
    def setUp(self):
        cache.default_cache.clear()

    def test_generate_obj_key_with_instance(self):
        m = CacheTest(pk=1, code='foo', other=69)
        actual = cache.generate_obj_key(m, pk=m.pk)

        self.assertEquals('model:warthog_test.cachetest[pk=1]', actual)

    def test_generate_obj_key_with_type(self):
        actual = cache.generate_obj_key(CacheTest, pk=2)

        self.assertEquals('model:warthog_test.cachetest[pk=2]', actual)

    def test_set_model(self):
        m = CacheTest(pk=1, code='foo', other=69)

        key = cache.set_model(m)
        self.assertEqual('model:warthog_test.cachetest[pk=1]', key)

        actual = cache.default_cache.get(key)
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, CacheTest)

    def test_get_model(self):
        actual = cache.get_model(CacheTest, 1)
        self.assertIsNone(actual)

        # Arrange
        target = CacheTest(pk=1, code='foo', other=69)
        cache.default_cache.set('model:warthog_test.cachetest[pk=1]', target)

        # Act
        actual = cache.get_model(CacheTest, 1)
        self.assertIsNotNone(actual)

    def test_set_model_by_attribute(self):
        # Act
        m = CacheTest(pk=1, code='foo', other=69)
        ref_key = cache.set_model_by_attribute(m, 'code')

        # Assert
        self.assertEqual('model:warthog_test.cachetest[code=foo]', ref_key)
        key = cache.default_cache.get(ref_key)
        self.assertEqual('model:warthog_test.cachetest[pk=1]', key)
        actual = cache.default_cache.get(key)
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, CacheTest)

    def test_get_model_by_attribute(self):
        actual = cache.get_model_by_attribute(CacheTest, 'code', 'foo')
        self.assertIsNone(actual)

        # Arrange
        target = CacheTest(pk=1, code='foo', other=69)
        cache.default_cache.set('model:warthog_test.cachetest[code=foo]', 'model:warthog_test.cachetest[pk=1]')
        cache.default_cache.set('model:warthog_test.cachetest[pk=1]', target)

        # Act
        actual = cache.get_model_by_attribute(CacheTest, 'code', 'foo')
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, CacheTest)
