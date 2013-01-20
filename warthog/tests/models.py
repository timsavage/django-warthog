import datetime
from django import test
from django.core.exceptions import ValidationError
from django.utils import timezone
from warthog.models import Resource


THIRTY_MINUTES = datetime.timedelta(minutes=30)
FUTURE = timezone.now() + THIRTY_MINUTES
PAST = timezone.now() - THIRTY_MINUTES

TEST_RESOURCES = {
    'deleted': Resource(deleted=True, published=True, publish_date=None, unpublish_date=None),
    'live': Resource(deleted=False, published=True, publish_date=None, unpublish_date=None),
    'unpublished': Resource(deleted=False, published=False, publish_date=None, unpublish_date=None),
    'scheduled': Resource(deleted=False, published=True, publish_date=FUTURE, unpublish_date=None),
    'expired': Resource(deleted=False, published=True, publish_date=None, unpublish_date=PAST),
    'live_in_range': Resource(deleted=False, published=True, publish_date=PAST, unpublish_date=FUTURE),
    'live_no_start': Resource(deleted=False, published=True, publish_date=None, unpublish_date=FUTURE),
    'live_no_end': Resource(deleted=False, published=True, publish_date=PAST, unpublish_date=None),
}

PUBLISHED_STATUS = lambda t: t.published_status
IS_LIVE = lambda t: t.is_live


class ContentModelTestCase(test.TestCase):
    """
    Test cases for the content model.
    """
    def assertTargetEqual(self, target_resource, resolver, expected_value):
        target = TEST_RESOURCES[target_resource]
        actual_value = resolver(target)
        self.assertEqual(expected_value, actual_value)

    ## Published Status tests

    def test_published_status_deleted(self):
        self.assertTargetEqual('deleted', PUBLISHED_STATUS, Resource.STATUS_DELETED)

    def test_published_status_live(self):
        self.assertTargetEqual('live', PUBLISHED_STATUS, Resource.STATUS_LIVE)

    def test_published_status_unpublished(self):
        self.assertTargetEqual('unpublished', PUBLISHED_STATUS, Resource.STATUS_UNPUBLISHED)

    def test_published_status_scheduled(self):
        self.assertTargetEqual('scheduled', PUBLISHED_STATUS, Resource.STATUS_SCHEDULED)

    def test_published_status_expired(self):
        self.assertTargetEqual('expired', PUBLISHED_STATUS, Resource.STATUS_EXPIRED)

    def test_published_status_live_in_range(self):
        self.assertTargetEqual('live_in_range', PUBLISHED_STATUS, Resource.STATUS_LIVE)

    def test_published_status_live_no_start(self):
        self.assertTargetEqual('live_no_start', PUBLISHED_STATUS, Resource.STATUS_LIVE)

    def test_published_status_live_no_end(self):
        self.assertTargetEqual('live_no_end', PUBLISHED_STATUS, Resource.STATUS_LIVE)

    ## Is Live tests

    def test_is_live_deleted(self):
        self.assertTargetEqual('deleted', IS_LIVE, False)

    def test_is_live_live(self):
        self.assertTargetEqual('live', IS_LIVE, True)

    def test_is_live_unpublished(self):
        self.assertTargetEqual('unpublished', IS_LIVE, False)

    def test_is_live_scheduled(self):
        self.assertTargetEqual('scheduled', IS_LIVE, False)

    def test_is_live_expired(self):
        self.assertTargetEqual('expired', IS_LIVE, False)

    def test_is_live_live_in_range(self):
        self.assertTargetEqual('live_in_range', IS_LIVE, True)

    def test_is_live_live_no_start(self):
        self.assertTargetEqual('live_no_start', IS_LIVE, True)

    def test_is_live_live_no_end(self):
        self.assertTargetEqual('live_no_end', IS_LIVE, True)


    ## Other property tests

    def test_is_root(self):
        target = Resource(parent=None)
        self.assertTrue(target.is_root)

        parent = Resource()
        target = Resource(parent=parent)
        self.assertFalse(target.is_root)

    def test_menu_title(self):
        target = Resource(title="Foo")
        self.assertEqual("Foo", target.menu_title)

        target = Resource(title="Foo", menu_title_raw="Bar")
        self.assertEqual("Bar", target.menu_title)


    ## Methods

    def test_clean_no_dates(self):
        target = Resource()
        target.clean()

    def test_clean_no_publish_date(self):
        target = Resource(publish_date=None, unpublish_date=FUTURE)
        target.clean()

    def test_clean_no_unpublish_date(self):
        target = Resource(publish_date=PAST, unpublish_date=None)
        target.clean()

    def test_clean_valid_range(self):
        target = Resource(publish_date=PAST, unpublish_date=FUTURE)
        target.clean()

    def test_clean_invalid_range(self):
        target = Resource(publish_date=FUTURE, unpublish_date=PAST)
        self.assertRaises(ValidationError, lambda: target.clean())

