import json
from tornado.testing import AsyncHTTPTestCase, gen_test # type: ignore
import listing_service
import tornado.options
tornado.options.define("debug", default=True)
tornado.options.define("port", default=6000)

class DummyOptions:
    debug = True

class TestListingsService(AsyncHTTPTestCase):
    def get_app(self):
        return listing_service.make_app(DummyOptions())

class TestListingsService(AsyncHTTPTestCase):
    def get_app(self):
        return listing_service.make_app(listing_service.tornado.options.options)

    @gen_test
    async def test_ping(self):
        response = await self.http_client.fetch(self.get_url("/listings/ping"))
        assert response.code == 200
        assert response.body.decode() == "pong!"

    @gen_test
    async def test_create_listing_and_fetch(self):
        # Create listing
        body = "user_id=1&listing_type=rent&price=4000"
        response = await self.http_client.fetch(
            self.get_url("/listings"),
            method="POST",
            body=body
        )
        data = json.loads(response.body.decode())
        assert data["result"] is True
        assert data["listing"]["price"] == 4000

        # Fetch listings
        resp = await self.http_client.fetch(self.get_url("/listings?page_num=1&page_size=5"))
        data = json.loads(resp.body.decode())
        assert data["result"] is True
        assert any(l["price"] == 4000 for l in data["listings"])

    @gen_test
    async def test_pagination(self):
        # Create multiple listings
        for i in range(3):
            body = f"user_id=2&listing_type=sale&price={1000+i}"
            await self.http_client.fetch(
                self.get_url("/listings"),
                method="POST",
                body=body
            )

        # Fetch page 2 with size 1
        resp = await self.http_client.fetch(self.get_url("/listings?page_num=2&page_size=1"))
        data = json.loads(resp.body.decode())
        assert data["result"] is True
        assert len(data["listings"]) == 1  # only one record per page

    @gen_test
    async def test_invalid_price(self):
        # Invalid price (string)
        body = "user_id=1&listing_type=rent&price=abc"
        resp = await self.http_client.fetch(
            self.get_url("/listings"),
            method="POST",
            body=body,
            raise_error=False
        )
        assert resp.code == 400
        data = json.loads(resp.body.decode())
        assert data["result"] is False
        assert "invalid price" in data["errors"][0]
