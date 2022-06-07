from datetime import datetime
from typing import Dict, Iterable, Tuple, Union

from timesignal.models.signal import EventSignal


class EventOrchestra:
    """
    Collection of named event signals. Provides a unified interface for interpolation. Event orchestras are recursively-composable.
    """
    
    def __init__(self, elements: Dict[str, Union[EventSignal, 'EventOrchestra']]):
        self._elements = elements

    @property
    def start(self) -> datetime:
        return min(element.start for element in self._elements.values())
    
    @property
    def end(self) -> datetime:
        return max(element.end for element in self._elements.values())
    
    def _check_time_index(self, time_index: datetime):
        """
        Check if the given time index is within the bounds of the signal orchestra.
        """
        if time_index < self.start or time_index > self.end:
            raise ValueError(f'Time index {time_index} is out of bounds.')

    def get_signal(self, name: str) -> Union[EventSignal, 'EventOrchestra']:
        """
        Get the named element.
        """
        if name not in self._elements:
            raise ValueError(f'Element {name} does not exist.')
        
        return self._elements.get(name)
    
    def get_name_value_pairs_at_datetime(self, time_index: datetime) -> Iterable[Tuple[str, Union[float, 'EventOrchestra']]]:
        """
        Get name-value pairs of all valid elements at a given datetime.
        """
        for name, signal in self._elements.items():
            try:
                value = signal[time_index]
                yield name, value
            except ValueError:
                pass

    def get_dict_at_datetime(self, time_index: datetime) -> Dict[str, Union[float, dict]]:
        """
        Get a dictionary of all valid event signal values at a given datetime.
        Recursively calls get_dict_at_datetime on all nested event orchestras.
        """
        d = {}
        for name, value in self.get_name_value_pairs_at_datetime(time_index):
            d[name] = value.get_dict_at_datetime(time_index) if isinstance(value, EventOrchestra) else value
        return d

    def __getitem__(self, time_index: datetime):
        return self.get_dict_at_datetime(time_index)



def test():
    from timesignal.models import signal
    
    eo1 = EventOrchestra({
        'es1': signal.test(n=10, m=5),
        'es2': signal.test(n=10, m=4),
        'es3': signal.test(n=10, m=3),
    })
    
    eo2 = EventOrchestra({
        'eo1': eo1,
        'es4': signal.test(n=10, m=2),
    })
    
    return eo2
