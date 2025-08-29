import json
import os
import sqlite3
import tempfile
import tornado.testing
import tornado.web
from user_service import make_app  # assuming your service file is named main.py


class UsersServiceTest(tornado.testing.AsyncHTTPTestCase):
    def setUp(self):
        # create temporary DB file
        self.db_fd, self.db_path = tempfile.mkstemp()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        os.close(self.db_fd)
        os.remove(self.db_path)

    def get_app(self):
        class Options:
            debug = True

        # override app to use temporary db
        app = make_app(Options())
        app.db.close()
        app.db = sqlite3.connect(self.db_path)
        app.db.row_factory = sqlite3.Row
        app.init_db()
        return app

    def test_create_user_success(self):
        body = "name=Alice"
        response = self.fetch("/users", method="POST", body=body)
        self.assertEqual(response.code, 200)

        data = json.loads(response.body)
        self.assertTrue(data["result"])
        self.assertEqual(data["user"]["name"], "Alice")

    def test_create_user_without_name(self):
        response = self.fetch("/users", method="POST", body="")
        self.assertEqual(response.code, 400)

        data = json.loads(response.body)
        self.assertFalse(data["result"])
        self.assertIn("name is required", data["errors"])

    def test_create_duplicate_user(self):
        body = "name=Bob"
        self.fetch("/users", method="POST", body=body)
        response = self.fetch("/users", method="POST", body=body)

        self.assertEqual(response.code, 400)
        data = json.loads(response.body)
        self.assertFalse(data["result"])
        self.assertIn("name must be unique", data["errors"])

    def test_get_users_pagination(self):
        # insert multiple users
        for i in range(1, 6):
            self.fetch("/users", method="POST", body=f"name=User{i}")

        response = self.fetch("/users?page_num=1&page_size=2")
        self.assertEqual(response.code, 200)

        data = json.loads(response.body)
        self.assertTrue(data["result"])
        self.assertEqual(len(data["users"]), 2)

    def test_get_user_detail_success(self):
        # create a user
        response = self.fetch("/users", method="POST", body="name=Charlie")
        data = json.loads(response.body)
        user_id = data["user"]["id"]

        response = self.fetch(f"/users/{user_id}")
        self.assertEqual(response.code, 200)

        data = json.loads(response.body)
        self.assertTrue(data["result"])
        self.assertEqual(data["user"]["id"], user_id)

    def test_get_user_detail_not_found(self):
        response = self.fetch("/users/9999")
        self.assertEqual(response.code, 404)

        data = json.loads(response.body)
        self.assertFalse(data["result"])
        self.assertIn("user not found", data["errors"])

    def test_get_user_detail_invalid_id(self):
        response = self.fetch("/users/abc")
        self.assertEqual(response.code, 404)

        data = json.loads(response.body)
        self.assertFalse(data["result"])
        self.assertIn("invalid user_id", data["errors"])


if __name__ == "__main__":
    tornado.testing.main()
