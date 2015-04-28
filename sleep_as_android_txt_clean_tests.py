# use nosetests framework to test this file

import nose.tools
from nose.tools import eq_, assert_almost_equal
from datetime import timedelta


from sleep_as_android_txt_clean import *

def test_wrapDateTime_no_need_for_wrapping():
    dt = datetime.strptime("14. 01. 2015 19:59", '%d. %m. %Y %H:%M')
    (actual_dateWrapped, actual_hourWrapped) = wrapDateTime(dt)
    expected_dateWrapped = datetime.strptime("14. 01. 2015", '%d. %m. %Y').date()
    eq_(actual_dateWrapped, expected_dateWrapped)
    assert_almost_equal(actual_hourWrapped, 19.983, 3)

def test_wrapDateTime_need_wrapping():
    dt = datetime.strptime("14. 01. 2015 20:01", '%d. %m. %Y %H:%M')
    (actual_dateWrapped, actual_hourWrapped) = wrapDateTime(dt, 20)
    expected_dateWrapped = datetime.strptime("15. 01. 2015", '%d. %m. %Y').date()
    eq_(actual_dateWrapped, expected_dateWrapped)
    assert_almost_equal(actual_hourWrapped, -3.98, 2)

if __name__ == '__main__':
    test_wrapDateTime_need_wrapping()