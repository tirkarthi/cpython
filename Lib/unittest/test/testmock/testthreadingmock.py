import threading
import multiprocessing
import time
import unittest
import concurrent.futures

from test.support import start_threads
from unittest.mock import patch, ThreadingMock, call


class Something:

    def method_1(self):
        pass

    def method_2(self):
        pass


class TestThreadingMock(unittest.TestCase):

    def _call_after_delay(self, func, /, *args, **kwargs):
        time.sleep(kwargs.pop('delay'))
        func(*args, **kwargs)


    def setUp(self):
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    def tearDown(self):
        self._executor.shutdown()

    def run_async(self, func, /, *args, delay=0, **kwargs):
        self._executor.submit(self._call_after_delay, func, *args, **kwargs, delay=delay)

    def _make_mock(self, *args, **kwargs):
        return ThreadingMock(*args, **kwargs)

    def test_instance_check(self):
        waitable_mock = self._make_mock()

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()

            self.assertIsInstance(something.method_1, ThreadingMock)
            self.assertIsInstance(
                something.method_1().method_2(), ThreadingMock)


    def test_side_effect(self):
        waitable_mock = self._make_mock()

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            something.method_1.side_effect = [1]

            self.assertEqual(something.method_1(), 1)


    def test_spec(self):
        waitable_mock = self._make_mock(spec=Something)

        with patch(f'{__name__}.Something', waitable_mock) as m:
            something = m()

            self.assertIsInstance(something.method_1, ThreadingMock)
            self.assertIsInstance(
                something.method_1().method_2(), ThreadingMock)

            with self.assertRaises(AttributeError):
                m.test


    def test_wait_until_called(self):
        waitable_mock = self._make_mock(spec=Something)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            self.run_async(something.method_1, delay=0.01)
            something.method_1.wait_until_called()
            something.method_1.assert_called_once()


    def test_wait_until_called_called_before(self):
        waitable_mock = self._make_mock(spec=Something)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            something.method_1()
            something.method_1.wait_until_called()
            something.method_1.assert_called_once()


    def test_wait_until_called_magic_method(self):
        waitable_mock = self._make_mock(spec=Something)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            self.run_async(something.method_1.__str__, delay=0.01)
            something.method_1.__str__.wait_until_called()
            something.method_1.__str__.assert_called_once()


    def test_wait_until_called_timeout(self):
        waitable_mock = self._make_mock(spec=Something)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            self.run_async(something.method_1, delay=0.2)
            with self.assertRaises(AssertionError):
                something.method_1.wait_until_called(mock_timeout=0.1)
            something.method_1.assert_not_called()

            something.method_1.wait_until_called()
            something.method_1.assert_called_once()


    def test_wait_until_any_call_positional(self):
        waitable_mock = self._make_mock(spec=Something)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            self.run_async(something.method_1, 1, delay=0.1)
            self.run_async(something.method_1, 2, delay=0.2)
            self.run_async(something.method_1, 3, delay=0.3)
            self.assertNotIn(call(1), something.method_1.mock_calls)

            something.method_1.wait_until_any_call(1)
            something.method_1.assert_called_once_with(1)
            self.assertNotIn(call(2), something.method_1.mock_calls)
            self.assertNotIn(call(3), something.method_1.mock_calls)

            something.method_1.wait_until_any_call(3)
            self.assertIn(call(2), something.method_1.mock_calls)
            something.method_1.wait_until_any_call(2)


    def test_wait_until_any_call_keywords(self):
        waitable_mock = self._make_mock(spec=Something)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            self.run_async(something.method_1, a=1, delay=0.1)
            self.run_async(something.method_1, b=2, delay=0.2)
            self.run_async(something.method_1, c=3, delay=0.3)
            self.assertNotIn(call(a=1), something.method_1.mock_calls)

            something.method_1.wait_until_any_call(a=1)
            something.method_1.assert_called_once_with(a=1)
            self.assertNotIn(call(b=2), something.method_1.mock_calls)
            self.assertNotIn(call(c=3), something.method_1.mock_calls)

            something.method_1.wait_until_any_call(c=3)
            self.assertIn(call(b=2), something.method_1.mock_calls)
            something.method_1.wait_until_any_call(b=2)

    def test_wait_until_any_call_no_argument(self):
        waitable_mock = self._make_mock(spec=Something)

        with patch(f'{__name__}.Something', waitable_mock):
            something = Something()
            something.method_1(1)

            something.method_1.assert_called_once_with(1)
            with self.assertRaises(AssertionError):
                something.method_1.wait_until_any_call(mock_timeout=0.1)

            something.method_1()
            something.method_1.wait_until_any_call()


if __name__ == "__main__":
    unittest.main()
