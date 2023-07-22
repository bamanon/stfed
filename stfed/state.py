import typing
import dataclasses

@dataclasses.dataclass()
class Subscription:
    subject: "Publisher"
    callback: typing.Callable[[any], any]
    
    def unsubscribe(self):
        if self.subject is None:
            return
        self.subject.unsubscribe(self.callback)
        self.subject = None
        self.callback = None


T = typing.TypeVar("T")
T1 = typing.TypeVar("T1")

class Publisher(typing.Generic[T]):
    def __init__(self):
        self.__subscribers: set[typing.Callable[[T], any]] = set()
        self.__initialized = False

    def subscribe(self, callback: typing.Callable[[T], any]) -> Subscription:
        self.__subscribers.add(callback)
        if self.__initialized:
            callback(self.__last_value)
        return Subscription(self, callback)
    
    def map_subscribe(
        self,
        selector: typing.Callable[[T], T1],
        callback: typing.Callable[[T1], any]
    ) -> Subscription:
        state = { 'prev_val': None, 'initialized': False }
        def handler(next_state: T) -> any:
            next_val = selector(next_state)
            if not state['initialized'] or next_val != state['prev_val']:
                callback(next_val)
            state['prev_val'] = next_val
            state['initialized'] = True
        return self.subscribe(handler)


    def unsubscribe(self, subscription: Subscription) -> None:
        self.__subscribers.remove(subscription)


    def next(self, value: T) -> None:
        self.__last_value = value
        self.__initialized = True
        for callback in self.__subscribers:
            callback(value)

    def snapshot(self) -> T:
        return self.__last_value
