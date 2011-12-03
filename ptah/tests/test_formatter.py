""" formatter tests """
import pytz
from datetime import datetime, timedelta

import ptah
from ptah import formatter
from ptah.testing import PtahTestCase


class TestFormatter(PtahTestCase):

    def test_formatter_registration(self):
        def simple(v):
            return 'simple-%s'%v

        format = formatter.format
        format['simple'] = simple

        self.assertEqual(format.simple('test'), 'simple-test')
        self.assertRaises(ValueError, format.__setitem__, 'simple', simple)

        del format['simple']
        self.assertEqual(getattr(format, 'simple', None), None)
        self.assertFalse('simple' in format)

    def test_datetime_formatter(self):
        format = formatter.format
        self.assertTrue('datetime' in format)

        # format only datetime
        self.assertEqual(format.datetime('text string'), 'text string')

        # default format
        dt = datetime(2011, 2, 6, 10, 35, 45, 80, pytz.UTC)
        self.assertEqual(format.datetime(dt, 'short'),
                         '02/06/11 04:35 AM')
        self.assertEqual(format.datetime(dt, 'medium'),
                         'Feb 06, 2011 04:35 AM')
        self.assertEqual(format.datetime(dt, 'long'),
                         'February 06, 2011 04:35 AM -0600')
        self.assertEqual(format.datetime(dt, 'full'),
                         'Sunday, February 06, 2011 04:35:45 AM CST')

    def test_datetime_formatter2(self):
        format = formatter.format

        # datetime without timezone
        dt = datetime(2011, 2, 6, 10, 35, 45, 80)
        self.assertEqual(format.datetime(dt, 'short'),
                         '02/06/11 04:35 AM')

        # different format
        dt = datetime(2011, 2, 6, 10, 35, 45, 80, pytz.UTC)

        FORMAT = ptah.get_settings('format', self.registry)
        FORMAT['date_short'] = '%b %d, %Y'

        self.assertEqual(format.datetime(dt, 'short'),
                         'Feb 06, 2011 04:35 AM')

    def test_timedelta_formatter(self):
        format = formatter.format
        self.assertTrue('timedelta' in format)

        # format only timedelta
        self.assertEqual(format.timedelta('text string'), 'text string')

        # full format
        td = timedelta(hours=10, minutes=5, seconds=45)

        self.assertEqual(format.timedelta(td, 'full'),
                         '10 hour(s) 5 min(s) 45 sec(s)')

        # medium format
        self.assertEqual(format.timedelta(td, 'medium'),
                         '10:05:45')

        # seconds format
        self.assertEqual(format.timedelta(td, 'seconds'),
                         '36345.0000')

        # default format
        self.assertEqual(format.timedelta(td), '10:05:45')

    def test_size_formatter(self):
        format = formatter.format
        self.assertTrue('size' in format)

        # format only timedelta
        self.assertEqual(format.size('text string'), 'text string')

        v = 1024
        self.assertEqual(format.size(v, 'b'), '1024 B')

        self.assertEqual(format.size(v, 'k'), '1.00 Kb')

        self.assertEqual(format.size(1024*768, 'm'), '0.75 Mb')
        self.assertEqual(format.size(1024*768*768, 'm'), '576.00 Mb')
