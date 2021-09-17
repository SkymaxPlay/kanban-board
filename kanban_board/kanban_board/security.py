import bcrypt
from pyramid.authentication import AuthTktCookieHelper

from .models import User


def hash_password(password):
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


class SecurityPolicy:
    def __init__(self, secret):
        self.authtkt = AuthTktCookieHelper(secret=secret)

    def identity(self, request):
        identity = self.authtkt.identify(request)

        if identity is None:
            return None

        return identity

    def authenticated_userid(self, request):
        identity = self.identity(request)

        if identity is not None:
            return identity["userid"]

    def remember(self, request, userid, **kw):
        return self.authtkt.remember(request, userid, **kw)

    def forget(self, request):
        return self.authtkt.forget(request)


def get_user_data(request):
    userid = request.authenticated_userid

    if not userid:
        return None

    result = request.dbsession.query(User).filter(User.id == userid)

    return result.first() if request is not None else None
