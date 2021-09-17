from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

from .security import SecurityPolicy


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings, session_factory=SignedCookieSessionFactory("secretkb")) as config:
        config.set_security_policy(SecurityPolicy(secret="secr3t123"))
        config.include('.models')
        config.include('pyramid_jinja2')
        config.include('.routes')
        config.scan()
    return config.make_wsgi_app()
