from onetutor.tests.BaseTest import BaseTest


class BaseTestViews(BaseTest):

    def setUp(self, path='') -> None:
        super(BaseTestViews, self).setUp(path)
        self.path = path

    def get(self):
        return self.client.get(self.path)

    def post(self, data):
        return self.client.post(self.path, data)
