import tornado.web
import tornado.gen
import tornado.options
import sqlite3
import time
import logging
import json

class App(tornado.web.Application):
    def __init__(self, handlers, **kwargs):
        super().__init__(handlers, **kwargs)
        self.db = sqlite3.connect("users.db")
        self.db.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        cursor = self.db.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
        """)
        self.db.commit()

class BaseHandler(tornado.web.RequestHandler):
    def write_json(self, obj, status_code=200):
        self.set_header("Content-Type", "application/json")
        self.set_status(status_code)
        self.write(json.dumps(obj))

class UsersHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        page_num = int(self.get_argument("page_num", 1))
        page_size = int(self.get_argument("page_size", 10))

        offset = (page_num - 1) * page_size
        cursor = self.application.db.cursor()
        results = cursor.execute(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (page_size, offset)
        )

        users = [dict(row) for row in results]
        self.write_json({"result": True, "users": users})

    @tornado.gen.coroutine
    @tornado.gen.coroutine

    def post(self):
        name = self.get_argument("name", None)
        if not name:
            self.write_json({"result": False, "errors": ["name is required"]}, status_code=400)
            return

        # Check if name already exists
        cursor = self.application.db.cursor()
        exists = cursor.execute("SELECT id FROM users WHERE name=?", (name,)).fetchone()
        if exists:
            self.write_json({"result": False, "errors": ["name must be unique"]}, status_code=400)
            return

        ts = int(time.time() * 1e6)
        cursor.execute(
            "INSERT INTO users (name, created_at, updated_at) VALUES (?, ?, ?)",
            (name, ts, ts)
        )
        self.application.db.commit()
        user_id = cursor.lastrowid

        self.write_json({
            "result": True,
            "user": {"id": user_id, "name": name, "created_at": ts, "updated_at": ts}
        })


class UserDetailHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, user_id):
        try:
            user_id = int(user_id)
        except:
            self.write_json({"result": False, "errors": ["invalid user_id"]}, status_code=400)
            return

        cursor = self.application.db.cursor()
        row = cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            self.write_json({"result": False, "errors": ["user not found"]}, status_code=404)
            return

        self.write_json({"result": True, "user": dict(row)})

def make_app(options):
    return App([
        (r"/users", UsersHandler),
        (r"/users/([0-9]+)", UserDetailHandler),
    ], debug=options.debug)

if __name__ == "__main__":
    tornado.options.define("port", default=6001)
    tornado.options.define("debug", default=True)
    tornado.options.parse_command_line()
    options = tornado.options.options

    app = make_app(options)
    app.listen(options.port)
    logging.info(f"Starting user service on port {options.port}")
    tornado.ioloop.IOLoop.instance().start()
