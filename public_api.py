import tornado.web
import tornado.gen
import tornado.options
import json
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

LISTING_SERVICE_URL = "http://localhost:6000/listings"
USER_SERVICE_URL = "http://localhost:6001/users"

class BaseHandler(tornado.web.RequestHandler):
    def write_json(self, obj, status_code=200):
        self.set_header("Content-Type", "application/json")
        self.set_status(status_code)
        self.write(json.dumps(obj))

class PublicListingsHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        page_num = int(self.get_argument("page_num", 1))
        page_size = int(self.get_argument("page_size", 10))
        user_id = self.get_argument("user_id", None)

        # Prepare URL for Listing Service
        url = f"{LISTING_SERVICE_URL}?page_num={page_num}&page_size={page_size}"
        if user_id:
            url += f"&user_id={user_id}"

        http_client = AsyncHTTPClient()
        try:
            resp = yield http_client.fetch(url)
            listings = json.loads(resp.body.decode())["listings"]
        except Exception as e:
            self.write_json({"result": False, "errors": ["listing service unavailable"]}, status_code=503)
            return

        # Fetch users info and enrich listings
        enriched_listings = []
        for l in listings:
            user = None
            try:
                resp_user = yield http_client.fetch(f"{USER_SERVICE_URL}/{l['user_id']}")
                user = json.loads(resp_user.body.decode())["user"]
            except:
                user = None
            l["user"] = user
            enriched_listings.append(l)

        self.write_json({"result": True, "listings": enriched_listings, "page_num": page_num, "page_size": page_size, "total_records": len(enriched_listings)})

class PublicUsersHandler(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        try:
            data = json.loads(self.request.body.decode())
        except:
            self.write_json({"result": False, "errors": ["invalid JSON"]}, status_code=400)
            return

        if "name" not in data:
            self.write_json({"result": False, "errors": ["name is required"]}, status_code=400)
            return

        http_client = AsyncHTTPClient()
        try:
            req = HTTPRequest(url=USER_SERVICE_URL, method="POST", body=f"name={data['name']}")
            resp = yield http_client.fetch(req)
            result = json.loads(resp.body.decode())
        except Exception as e:
            self.write_json({"result": False, "errors": ["user service unavailable"]}, status_code=503)
            return

        self.write_json(result)

class PublicListingsCreateHandler(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        try:
            data = json.loads(self.request.body.decode())
        except:
            self.write_json({"result": False, "errors": ["invalid JSON"]}, status_code=400)
            return

        required_fields = ["user_id", "listing_type", "price"]
        for f in required_fields:
            if f not in data:
                self.write_json({"result": False, "errors": [f"{f} is required"]}, status_code=400)
                return

        http_client = AsyncHTTPClient()
        body = f"user_id={data['user_id']}&listing_type={data['listing_type']}&price={data['price']}"
        try:
            req = HTTPRequest(url=LISTING_SERVICE_URL, method="POST", body=body)
            resp = yield http_client.fetch(req)
            result = json.loads(resp.body.decode())
        except Exception as e:
            self.write_json({"result": False, "errors": ["listing service unavailable"]}, status_code=503)
            return

        self.write_json(result)

def make_app(options):
    return tornado.web.Application([
        (r"/public-api/listings", PublicListingsHandler),
        (r"/public-api/listings/create", PublicListingsCreateHandler),
        (r"/public-api/users", PublicUsersHandler),
    ], debug=options.debug)

if __name__ == "__main__":
    tornado.options.define("port", default=6002)
    tornado.options.define("debug", default=True)
    tornado.options.parse_command_line()
    options = tornado.options.options

    app = make_app(options)
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
