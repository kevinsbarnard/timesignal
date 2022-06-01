from datetime import datetime
from typing import Dict, Iterable, Tuple

from timesignal.models.signal import EventSignal


class EventSignalOrchestra:
    """
    Collection of named event signals. Provides a unified interface for interpolation.
    """
    
    def __init__(self, signals: Dict[str, EventSignal]):
        self._signals = signals

    @property
    def start(self) -> datetime:
        return min(signal.start for signal in self._signals.values())
    
    @property
    def end(self) -> datetime:
        return max(signal.end for signal in self._signals.values())
    
    def _check_time_index(self, time_index: datetime):
        """
        Check if the given time index is within the bounds of the signal orchestra.
        """
        if time_index < self.start or time_index > self.end:
            raise ValueError(f'Time index {time_index} is out of bounds.')

    def get_signal(self, name: str) -> EventSignal:
        """
        Get the named event signal.
        """
        if name not in self._signals:
            raise ValueError(f'Signal {name} does not exist.')
        
        return self._signals.get(name)
    
    def get_name_value_pairs_at_datetime(self, time_index: datetime) -> Iterable[Tuple[str, float]]:
        """
        Get name-value pairs of all valid event signals at a given datetime.
        """
        for name, signal in self._signals.items():
            try:
                value = signal[time_index]
                yield name, value
            except ValueError:
                pass

    def get_dict_at_datetime(self, time_index: datetime) -> Dict[str, float]:
        """
        Get a dictionary of all valid event signals at a given datetime.
        """
        return dict(self.get_name_value_pairs_at_datetime(time_index))

    def __getitem__(self, time_index: datetime):
        return self.get_dict_at_datetime(time_index)



def test():
    from timesignal.models import signal
    
    es1 = signal.test(n=10, m=5)
    es2 = signal.test(n=10, m=3)
    es3 = signal.test(n=10, m=2)
    
    eso = EventSignalOrchestra({
        'es1': es1,
        'es2': es2,
        'es3': es3,
    })
    
    return eso
