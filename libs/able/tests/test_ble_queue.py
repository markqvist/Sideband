import unittest
import mock
from able.queue import ble_task


class TestBLETask(unittest.TestCase):

    def setUp(self):
        self.queue = mock.Mock()
        self.task_called = None

    @ble_task
    def increment(self, a=1, b=0):
        self.task_called = a + b

    def test_method_not_executed(self):
        self.increment()
        self.assertEqual(self.task_called, None)

    def test_task_enqued(self):
        self.increment()
        self.assertTrue(self.queue.enque.called)

    def test_task_default_arguments(self):
        self.increment()
        task = self.queue.enque.call_args[0][0]
        task()
        self.assertEqual(self.task_called, 1)

    def test_task_arguments_passed(self):
        self.increment(200, 11)
        task = self.queue.enque.call_args[0][0]
        task()
        self.assertEqual(self.task_called, 211)
