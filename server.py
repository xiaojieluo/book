from sanic import Sanic
from book.handler import APIHandler
from book import route
# from sanic.config import LOGGING
import logging


def make_app(name=__name__, route=None, settings=None):
    app = Sanic(name)
    if settings is None:
        settings = dict()
    app.config.update(settings)

    # 循环导入 route
    for url, view in route:
        app.add_route(view.as_view(), url)

    # 注册中间件
    app.middleware(APIHandler.authenticated)

    return app

if __name__ == '__main__':
    app = make_app(__name__, route=route)
    # Serves files from the static folder to the URL /static
    app.static('/static', './server/static')
    debug=True

    logging_format = "[%(asctime)s] %(process)d-%(levelname)s "
    logging_format += "%(module)s::%(funcName)s():l%(lineno)d: "
    logging_format += "%(message)s"

    logging.basicConfig(
        format=logging_format,
        level=logging.DEBUG if debug else logging.INFO,
    )
    # logging = logging.getLogger()

    app.run(host='127.0.0.1',
            port=8888,
            workers=1,
            debug=debug
    )
