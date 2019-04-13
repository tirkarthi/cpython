import threading
import time
import unittest

from test.support import start_threads
from unittest.mock import patch, WaitableMock, call


class Something:

    def method_1(self):
        pass

    def method_2(self):
        pass


class TestWaitableMock(unittest.TestCase):


    def _call_after_delay(self, func, *args, delay):
        time.sleep(delay)
        func(*args)


    def _create_thread(self, func, *args, **kwargs):
        thread = threading.Thread(target=self._call_after_delay,
                                  args=(func,) + args, kwargs=kwargs)
        return thread


    def test_instance_check(self):
        waitable_mock = WaitableMock(event_class=threading.Event)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()

            self.assertIsInstance(something.method_1, WaitableMock)
            self.assertIsInstance(
                something.method_1().method_2(), WaitableMock)


    def test_side_effect(self):
        waitable_mock = WaitableMock(event_class=threading.Event)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            something.method_1.side_effect = [1]

            self.assertEqual(something.method_1(), 1)


    def test_spec(self):
        waitable_mock = WaitableMock(
            event_class=threading.Event, spec=Something)

        with patch(f'{__name__}.Something', waitable_mock) as m:
            something = m()

            self.assertIsInstance(something.method_1, WaitableMock)
            self.assertIsInstance(
                something.method_1().method_2(), WaitableMock)

            with self.assertRaises(AttributeError):
                m.test


    def test_wait_until_called(self):
        waitable_mock = WaitableMock(event_class=threading.Event)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            thread = self._create_thread(something.method_1, delay=0.5)

            with start_threads([thread]):
                something.method_1.wait_until_called()
                something.method_1.assert_called_once()


    def test_wait_until_called_magic_method(self):
        waitable_mock = WaitableMock(event_class=threading.Event)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            thread = self._create_thread(something.method_1.__str__, delay=0.5)

            with start_threads([thread]):
                something.method_1.__str__.wait_until_called()
                something.method_1.__str__.assert_called_once()


    def test_wait_until_called_timeout(self):
        waitable_mock = WaitableMock(event_class=threading.Event)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            thread = self._create_thread(something.method_1, delay=0.5)

            with start_threads([thread]):
                something.method_1.wait_until_called(timeout=0.1)
                something.method_1.assert_not_called()

                something.method_1.wait_until_called()
                something.method_1.assert_called_once()


    def test_wait_until_called_with(self):
        waitable_mock = WaitableMock(event_class=threading.Event)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            thread_1 = self._create_thread(something.method_1, 1, delay=0.5)
            thread_2 = self._create_thread(something.method_2, 1, delay=0.1)
            thread_3 = self._create_thread(something.method_2, 2, delay=0.1)

            with start_threads([thread_1, thread_2, thread_3]):
                something.method_1.wait_until_called_with(1, timeout=0.1)
                something.method_1.assert_not_called()

                something.method_1.wait_until_called(timeout=2.0)
                something.method_1.assert_called_once_with(1)
                self.assertEqual(something.method_1.mock_calls, [call(1)])
                something.method_2.assert_has_calls(
                    [call(1), call(2)], any_order=True)


    def test_wait_until_called_with_no_argument(self):
        waitable_mock = WaitableMock(event_class=threading.Event)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            something.method_1(1)

            something.method_1.assert_called_once_with(1)
            self.assertFalse(
                something.method_1.wait_until_called_with(timeout=0.1))

            thread_1 = self._create_thread(something.method_1, delay=0.1)
            with start_threads([thread_1]):
                self.assertTrue(something.method_1.wait_until_called_with())


if __name__ == "__main__":
    unittest.main()
