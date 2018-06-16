import time
from abc import ABCMeta, abstractmethod
from datetime import datetime

from qf_lib.backtesting.events.empty_queue_event.empty_queue_event import EmptyQueueEvent
from qf_lib.backtesting.events.empty_queue_event.empty_queue_event_listener import EmptyQueueEventListener
from qf_lib.backtesting.events.empty_queue_event.empty_queue_event_notifier import EmptyQueueEventNotifier
from qf_lib.backtesting.events.end_trading_event.end_trading_event import EndTradingEvent
from qf_lib.backtesting.events.event_manager import EventManager
from qf_lib.backtesting.events.time_event.scheduler import Scheduler
from qf_lib.common.utils.dateutils.timer import SettableTimer, RealTimer


class TimeFlowController(EmptyQueueEventListener, metaclass=ABCMeta):
    """
    Abstract class for all TimeFlowControllers. TimeFlowController is an object which is responsible for controlling
    time flow of a backtest or live trading session, i.e. it's responsible for producing TimeEvents and putting
    them in the EventManager's event queue.
    """

    def __init__(self, event_manager: EventManager, empty_queue_event_notifier: EmptyQueueEventNotifier):
        self.event_manager = event_manager
        empty_queue_event_notifier.subscribe(self)

    def on_empty_queue_event(self, event: EmptyQueueEvent):
        self.generate_time_event()

    @abstractmethod
    def generate_time_event(self):
        """
        Checks when the next planned TimeEvent should occur, lets the time pass until that moment (or fast-forwards
        the time if it's a backtest) and then publishes the TimeEvent.
        """
        pass


class BacktestTimeFlowController(TimeFlowController):
    def __init__(self, scheduler: Scheduler, event_manager: EventManager, settable_timer: SettableTimer,
                 empty_queue_event_notifier: EmptyQueueEventNotifier, backtest_end_date: datetime):
        super().__init__(event_manager, empty_queue_event_notifier)
        self.scheduler = scheduler
        self.settable_timer = settable_timer
        self.backtest_end_date = backtest_end_date

    def generate_time_event(self):
        time_event = self.scheduler.get_next_time_event()
        next_time_of_event = time_event.time

        if next_time_of_event > self.backtest_end_date:
            self.event_manager.publish(EndTradingEvent(self.backtest_end_date))
        else:
            # because it's a backtest we don't really need to wait until the time of next TimeEvent; we can simply
            # fast-forward the timer to that time
            self.settable_timer.set_current_time(next_time_of_event)
            self.event_manager.publish(time_event)


class LiveSessionTimeFlowController(TimeFlowController):
    def __init__(self, scheduler: Scheduler, event_manager: EventManager, real_timer: RealTimer,
                 empty_queue_event_notifier: EmptyQueueEventNotifier):
        super().__init__(event_manager, empty_queue_event_notifier)
        self.scheduler = scheduler
        self.real_timer = real_timer

    def generate_time_event(self):
        time_event = self.scheduler.get_next_time_event()
        next_time_of_event = time_event.time

        self.sleep_until(next_time_of_event)
        self.event_manager.publish(time_event)

    def sleep_until(self, time_of_next_time_event: datetime):
        # if we're in the live session we need to put the program to sleep until the next TimeEvent
        now = self.real_timer.now()
        waiting_time = time_of_next_time_event - now
        time.sleep(waiting_time.total_seconds())