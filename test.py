import tempfile
import os
import unittest

from sync import Sync


class SyncTestCase(unittest.TestCase):
    def setUp(self):
        self.originaldir = os.getcwd()
        self.testdir = tempfile.TemporaryDirectory()
        os.chdir(self.testdir.name)

    def tearDown(self):
        os.chdir(self.originaldir)
        self.testdir.cleanup()
    
    def test_init(self):
        os.mkdir("source")
        sync = Sync("source", "destination")
        self.assertEqual(sync.source_root, "source")
        self.assertEqual(sync.destination_root, "destination")
        self.assertTrue(os.path.exists(sync.destination_root))

    def test_sync(self):
        os.mkdir("source")
        with open('source/foo.txt', 'w') as f:
            f.write('a')
        sync = Sync("source", "destination")
        sync.sync()
        with open('destination/foo.txt', 'r') as f:
            self.assertEqual(f.read(), 'a')

        os.remove('source/foo.txt')
        sync.sync()
        self.assertFalse(os.path.exists("destination/foo.txt"))


if __name__ == '__main__':
    unittest.main()








