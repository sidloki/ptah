from zope import interface
from pyramid.security import authenticated_userid
from pyramid.threadlocal import get_current_request

from ptah import config
from ptah.uri import resolve, resolver
from ptah.util import tldata
from ptah.interfaces import IAuthInfo, IAuthentication


class _Superuser(object):

    def __init__(self):
        self.__uri__ = 'ptah-auth:superuser'
        self.login = ''
        self.name = 'Manager'

    def __repr__(self):
        return '<ptah Superuser>'


SUPERUSER = _Superuser()
SUPERUSER_URI = 'ptah-auth:superuser'


@resolver('ptah-auth')
def superuser_resolver(uri):
    """System super user"""
    if uri == SUPERUSER_URI:
        return SUPERUSER


AUTH_CHECKER_ID = 'ptah.auth:checker'
AUTH_PROVIDER_ID = 'ptah.auth:provider'
AUTH_SEARCHER_ID = 'ptah.auth:searcher'


def auth_checker(checker):
    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            lambda config: config.get_cfg_storage(AUTH_CHECKER_ID)\
                .update({id(checker): checker}),
            discriminator=(AUTH_CHECKER_ID, checker))
        )
    return checker


def pyramid_auth_checker(config, checker):
    config.action(
        (AUTH_CHECKER_ID, checker),
        lambda config, checker: config.get_cfg_storage(AUTH_CHECKER_ID)\
            .update({id(checker): checker}),
        (config, checker))


def auth_provider(name):
    info = config.DirectiveInfo()

    def wrapper(cls):
        def _complete(cfg, cls, name):
            cfg.get_cfg_storage(AUTH_PROVIDER_ID)[name] = cls()

        info.attach(
            config.Action(
                _complete, (cls, name,),
                discriminator=(AUTH_PROVIDER_ID, name))
            )
        return cls

    return wrapper


def register_auth_provider(name, provider):
    info = config.DirectiveInfo()

    info.attach(
        config.Action(
            lambda config, n, p: config.get_cfg_storage(AUTH_PROVIDER_ID)\
                .update({n: p}),
            (name, provider),
            discriminator=(AUTH_PROVIDER_ID, name))
        )


def pyramid_auth_provider(config, name, provider):
    config.action(
        (AUTH_PROVIDER_ID, name),
        lambda config, n, p: \
            config.get_cfg_storage(AUTH_PROVIDER_ID).update({n: p}),
        (config, name, provider))


class AuthInfo(object):
    interface.implements(IAuthInfo)

    def __init__(self, principal, status=False, message=''):
        self.__uri__ = getattr(principal, '__uri__', None)
        self.principal = principal
        self.status = status
        self.message = message
        self.arguments = {}


_not_set = object()

USER_KEY = '__ptah_userid__'
EFFECTIVE_USER_KEY = '__ptah_effective__userid__'


class Authentication(object):
    interface.implements(IAuthentication)

    def authenticate(self, credentials):
        providers = config.get_cfg_storage(AUTH_PROVIDER_ID)
        for pname, provider in providers.items():
            principal = provider.authenticate(credentials)
            if principal is not None:
                info = AuthInfo(principal)

                for checker in \
                        config.get_cfg_storage(AUTH_CHECKER_ID).values():
                    if not checker(info):
                        return info

                info.status = True
                return info

        return AuthInfo(None)

    def authenticate_principal(self, principal):
        info = AuthInfo(principal)

        for checker in \
                config.get_cfg_storage(AUTH_CHECKER_ID).values():
            if not checker(info):
                return info

        info.status = True
        return info

    def set_userid(self, uri):
        tldata.set(USER_KEY, uri)

    def get_userid(self):
        uri = tldata.get(USER_KEY, _not_set)
        if uri is _not_set:
            try:
                self.set_userid(authenticated_userid(get_current_request()))
            except:  # pragma: no cover
                self.set_userid(None)
            return tldata.get(USER_KEY)
        return uri

    def set_effective_userid(self, uri):
        tldata.set(EFFECTIVE_USER_KEY, uri)

    def get_effective_userid(self):
        uri = tldata.get(EFFECTIVE_USER_KEY, _not_set)
        if uri is _not_set:
            return self.get_userid()
        return uri

    def get_current_principal(self):
        return resolve(self.get_userid())

    def get_principal_bylogin(self, login):
        providers = config.get_cfg_storage(AUTH_PROVIDER_ID)

        for pname, provider in providers.items():
            principal = provider.get_principal_bylogin(login)
            if principal is not None:
                return principal

authService = Authentication()


def search_principals(term):
    searchers = config.get_cfg_storage(AUTH_SEARCHER_ID)
    for name, searcher in searchers.items():
        for principal in searcher(term):
            yield principal


def register_principal_searcher(name, searcher):
    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            lambda config, name, searcher:
               config.get_cfg_storage(AUTH_SEARCHER_ID).update({name:searcher}),
            (name, searcher),
            discriminator=(AUTH_SEARCHER_ID, name))
        )


def pyramid_principal_searcher(config, name, searcher):
    config.action(
        (AUTH_SEARCHER_ID, name),
        lambda config, name, searcher:
            config.get_cfg_storage(AUTH_SEARCHER_ID).update({name:searcher}),
        (config, name, searcher))


def principal_searcher(name):
    info = config.DirectiveInfo()

    def wrapper(searcher):
        info.attach(
            config.Action(
                lambda config, name, searcher:
                    config.get_cfg_storage(AUTH_SEARCHER_ID)\
                        .update({name: searcher}),
                (name, searcher),
                discriminator=(AUTH_SEARCHER_ID, name))
            )

        return searcher

    return wrapper
