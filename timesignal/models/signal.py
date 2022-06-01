from datetime import datetime, timedelta
from typing import Iterable

import numpy as np
from scipy import interpolate


class EventSignal:
    """
    Interpolable scalar-valued signal of discrete events.
    """
    
    def __init__(self, values=None, interpolation='linear'):
        # Internal data array; 2xN, where N is the number of samples
        self._data = None
        
        # Interpolation kind / function
        self._interpolation = interpolation
        self._interpolate = None
        
        if values is not None:  # Seed the signal with given values
            self.values = values
    
    @property
    def interpolation(self):
        return self._interpolation
    
    @interpolation.setter
    def interpolation(self, value):
        self._interpolation = value
        
        if self._data is not None:
            self._interpolate = interpolate.interp1d(
                self._data[0, :], 
                self._data[1, :], 
                kind=value, 
                copy=False, 
                bounds_error=True, 
                assume_sorted=True
            )
    
    def __len__(self):
        return self._data.shape[1]
    
    def __getitem__(self, time_index: datetime):
        return self.get_value_at_datetime(time_index)
    
    def _check_time_index(self, time_index: datetime):
        """
        Check if the given time index is within the bounds of the signal.
        """
        if time_index < self.start or time_index > self.end:
            raise ValueError(f'Time index {time_index} is out of bounds.')
    
    def get_value_at_datetime(self, time_index: datetime):
        """
        Get the value of the signal at a given datetime.
        """
        self._check_time_index(time_index)
        return self.interpolate_datetimes((time_index,)).item()
    
    def get_value_at_index(self, index: int):
        """
        Get the value of the signal at a given index.
        """
        return self._data[1, index]
    
    def interpolate_datetimes(self, time_indices: Iterable[datetime]) -> np.ndarray:
        """
        Get the interpolated values of the signal at the given datetimes.
        """
        return self._interpolate(tuple(map(self.encode_datetime, time_indices)))
    
    @staticmethod
    def encode_datetime(dt: datetime) -> float:
        """
        Encode a datetime object into a float value.
        """
        return dt.timestamp()
    
    @staticmethod
    def decode_datetime(ts: float) -> datetime:
        """
        Decode a float value into a datetime object.
        """
        return datetime.fromtimestamp(ts)
    
    @property
    def start(self) -> datetime:
        """
        Get the first datetime of the signal.
        """
        if self._data is None:
            return None
        
        return self.decode_datetime(self._data[0, 0])
    
    @property
    def end(self) -> datetime:
        """
        Get the last datetime of the signal.
        """
        if self._data is None:
            return None
        
        return self.decode_datetime(self._data[0, -1])
    
    @property
    def duration(self) -> timedelta:
        """
        Get the duration of the signal.
        """
        if self._data is None:
            return None
        
        return self.end - self.start
    
    @property
    def values(self):
        """
        Get the signal data as datetime-value pairs.
        """
        if self._data is None:
            return None
        
        return zip(map(self.decode_datetime, self._data[0, :]), self._data[1, :])
    
    @values.setter
    def values(self, values):
        """
        Set the signal data from datetime-value pairs.
        """
        self._data = np.array(
            [(self.encode_datetime(dt), float(val)) for dt, val in values],
            dtype=np.float64
        ).T
        
        # Sort the data by time
        self._data = self._data[:, self._data[0, :].argsort()]
        
        # Set the interpolation kind / function
        self.interpolation = self._interpolation


def test(n=10, m=10):
    test_times = [datetime.now() + timedelta(seconds=i) for i in range(n)]
    test_values = [i % m for i in range(n)]
    
    es = EventSignal(values=zip(test_times, test_values))
    
    return es
