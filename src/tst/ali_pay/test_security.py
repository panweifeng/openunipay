import unittest
from ali_pay import security


class TestSecurity(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testSign(self):
        signValue = security.sign({"abc":"abc"})
        self.assertEqual(signValue, "OcUYLsWsMl2pkpD8jYRPkXYOBAiXKo/AThGqDiwxuDN0pOkDsd5mlem9tLy0+HypTabeX1mr6sz7IxbOWFfJ1fH5OR8P0bFgb8cOq8KGyG8ZVauVhls+hneiHoVMUHipEc3jVhE6Np27IiuN8nLh4tcrfbCHvWm5g5OGqN2FYSQ=")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
