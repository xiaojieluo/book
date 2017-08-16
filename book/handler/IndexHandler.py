from book.handler import APIHandler
from sanic.response import json, text, html
import os
from book.web import log

class index(APIHandler):

    async def get(self, requests):
        log(requests)
        return json({'hello':'world'})
