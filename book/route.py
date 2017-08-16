from book.handler import IndexHandler as Index
from book.handler import UserHandler as User
# from server.handler import ArticleHandler as Article
# from server.handler import PageHandler as Page
# from server.handler import AdminHandler as Admin

route = [
    (r'/', Index.index),
    (r'/index', Index.index),
]

route += [
    (r'/users', User.index),
    (r'/users/<objectid:\w{24}>/refreshSessionToken', User.refreshSessionToken),
    # (r'/users/me', User.index),
    (r'/login', User.login)
]
#
# route += [
#     (r'/login', User.login),
#     (r'/logout', User.logout)
# ]
#
# route += [
#     (r'/articles', Article.index),
#     (r'/articles/update/<article_id:int>', Article.update),
#     (r'/articles/delete', Article.delete),
#     (r'/articles/create', Article.create),
#     (r'/articles/generate', Article.generate),
# ]
#
# route += [
#     (r'/pages', Page.index),
# ]
#
# route += [
#     (r'/admin', Admin.index),
# ]
