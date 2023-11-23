from unittest import TestCase

from src.g_flow.main import get_usage


class TestGFlow(TestCase):
    def test_usage(self):
        self.assertIsNotNone(get_usage())
