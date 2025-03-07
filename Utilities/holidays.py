import pandas as pd
import pytz
import datetime
from dateutil import rrule

# borrowed/tweaked from Quantopian
#
# Copyright 2013 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

start = pd.Timestamp('1990-01-01', tz='UTC')
end_base = pd.Timestamp('today', tz='UTC')
# Give an aggressive buffer for logic that needs to use the next trading
# day or minute.
end = end_base + pd.Timedelta(days=365)


def canonicalize_datetime(dt):
    # Strip out any HHMMSS or timezone info in the user's datetime, so that
    # all the datetimes we return will be 00:00:00 UTC.
    return datetime.datetime(dt.year, dt.month, dt.day, tzinfo=pytz.utc)


def get_non_trading_days(start, end):
    non_trading_rules = []

    start = canonicalize_datetime(start)
    end = canonicalize_datetime(end)

    # weekends = rrule.rrule(
    #     rrule.YEARLY,
    #     byweekday=(rrule.SA, rrule.SU),
    #     cache=True,
    #     dtstart=start,
    #     until=end
    # )
    # non_trading_rules.append(weekends)

    new_years = rrule.rrule(
        rrule.MONTHLY,
        byyearday=1,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(new_years)

    new_years_sunday = rrule.rrule(
        rrule.MONTHLY,
        byyearday=2,
        byweekday=rrule.MO,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(new_years_sunday)

    mlk_day = rrule.rrule(
        rrule.MONTHLY,
        bymonth=1,
        byweekday=(rrule.MO(+3)),
        cache=True,
        dtstart=datetime.datetime(1998, 1, 1, tzinfo=pytz.utc),
        until=end
    )
    non_trading_rules.append(mlk_day)

    presidents_day = rrule.rrule(
        rrule.MONTHLY,
        bymonth=2,
        byweekday=(rrule.MO(3)),
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(presidents_day)

    good_friday = rrule.rrule(
        rrule.DAILY,
        byeaster=-2,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(good_friday)

    memorial_day = rrule.rrule(
        rrule.MONTHLY,
        bymonth=5,
        byweekday=(rrule.MO(-1)),
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(memorial_day)

    july_4th = rrule.rrule(
        rrule.MONTHLY,
        bymonth=7,
        bymonthday=4,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(july_4th)

    july_4th_sunday = rrule.rrule(
        rrule.MONTHLY,
        bymonth=7,
        bymonthday=5,
        byweekday=rrule.MO,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(july_4th_sunday)

    july_4th_saturday = rrule.rrule(
        rrule.MONTHLY,
        bymonth=7,
        bymonthday=3,
        byweekday=rrule.FR,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(july_4th_saturday)

    labor_day = rrule.rrule(
        rrule.MONTHLY,
        bymonth=9,
        byweekday=(rrule.MO(1)),
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(labor_day)

    thanksgiving = rrule.rrule(
        rrule.MONTHLY,
        bymonth=11,
        byweekday=(rrule.TH(4)),
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(thanksgiving)

    christmas = rrule.rrule(
        rrule.MONTHLY,
        bymonth=12,
        bymonthday=25,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(christmas)

    christmas_sunday = rrule.rrule(
        rrule.MONTHLY,
        bymonth=12,
        bymonthday=26,
        byweekday=rrule.MO,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(christmas_sunday)

    # If Christmas is a Saturday then 24th, a Friday is observed.
    christmas_saturday = rrule.rrule(
        rrule.MONTHLY,
        bymonth=12,
        bymonthday=24,
        byweekday=rrule.FR,
        cache=True,
        dtstart=start,
        until=end
    )
    non_trading_rules.append(christmas_saturday)

    non_trading_ruleset = rrule.rruleset()

    for rule in non_trading_rules:
        non_trading_ruleset.rrule(rule)

    non_trading_days = non_trading_ruleset.between(start, end, inc=True)

    # Add September 11th closings
    # http://en.wikipedia.org/wiki/Aftermath_of_the_September_11_attacks
    # Due to the terrorist attacks, the stock market did not open on 9/11/2001
    # It did not open again until 9/17/2001.
    #
    #    September 2001
    # Su Mo Tu We Th Fr Sa
    #                    1
    #  2  3  4  5  6  7  8
    #  9 10 11 12 13 14 15
    # 16 17 18 19 20 21 22
    # 23 24 25 26 27 28 29
    # 30

    for day_num in range(11, 17):
        non_trading_days.append(
            datetime.datetime(2001, 9, day_num, tzinfo=pytz.utc))

    # Add closings due to Hurricane Sandy in 2012
    # http://en.wikipedia.org/wiki/Hurricane_sandy
    #
    # The stock exchange was closed due to Hurricane Sandy's
    # impact on New York.
    # It closed on 10/29 and 10/30, reopening on 10/31
    #     October 2012
    # Su Mo Tu We Th Fr Sa
    #     1  2  3  4  5  6
    #  7  8  9 10 11 12 13
    # 14 15 16 17 18 19 20
    # 21 22 23 24 25 26 27
    # 28 29 30 31

    for day_num in range(29, 31):
        non_trading_days.append(
            datetime.datetime(2012, 10, day_num, tzinfo=pytz.utc))

    # Misc closings from NYSE listing.
    # http://www.nyse.com/pdfs/closings.pdf
    #
    # National Days of Mourning
    # - President Richard Nixon
    non_trading_days.append(datetime.datetime(1994, 4, 27, tzinfo=pytz.utc))
    # - President Ronald W. Reagan - June 11, 2004
    non_trading_days.append(datetime.datetime(2004, 6, 11, tzinfo=pytz.utc))
    # - President Gerald R. Ford - Jan 2, 2007
    non_trading_days.append(datetime.datetime(2007, 1, 2, tzinfo=pytz.utc))

    non_trading_days.sort()
    non_trading_days = map(lambda d: datetime.date(d.year, d.month, d.day), non_trading_days)
    return pd.DatetimeIndex(non_trading_days)

__HOLIDAYS_START_DATE = datetime.date(2000, 1, 1)
__HOLIDAYS_END_DATE = datetime.date.today()

HOLIDAYS_BY_COUNTRY_CONFIG = \
    {
        'US': get_non_trading_days(__HOLIDAYS_START_DATE, __HOLIDAYS_END_DATE)
    }
