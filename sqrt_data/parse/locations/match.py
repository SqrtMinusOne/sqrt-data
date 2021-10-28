# [[file:../../../org/locations.org::*Matching locations][Matching locations:1]]
import pandas as pd

from datetime import timedelta
from sqrt_data.api import settings

__all__ = ['LocationMatcher']


class LocationMatcher:
    def __init__(self):
        self._df_tz = pd.read_csv(settings['location']['tz_csv'])
        self._df_list = pd.read_csv(settings['location']['list_csv'])
        self._df_hostnames = pd.read_csv(settings['location']['hostnames_csv'])

        self._df_list['start_time'] = pd.to_datetime(
            self._df_list['start_time']
        )
        self._df_list = self._df_list.sort_values(
            by='start_time', ascending=False
        )

        self._init_timezones()

    def _init_timezones(self):
        self._timezones = {
            d.location: int(d.timezone)
            for d in self._df_tz.itertuples(index=False)
        }
        self._df_list['timezone'] = [
            self._timezones[l] for l in self._df_list['location']
        ]
        self._df_hostnames['timezone'] = [
            self._timezones[l] for l in self._df_hostnames['location']
        ]

    def get_location(self, time, hostname=None):
        if hostname is not None:
            matches = self._df_hostnames[self._df_hostnames.hostname == hostname
                                        ]
            if len(matches) > 0:
                match = matches.iloc[0]
                time += timedelta(seconds=60 * 60 * int(match.timezone))
                return (match.location, time)
        row = self._df_list[self._df_list.start_time < time.to_datetime64()
                           ].iloc[0]
        time += timedelta(seconds=60 * 60 * int(row.timezone))
        return (row.location, time)
# Matching locations:1 ends here
