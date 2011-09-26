""" role """
from zope import interface
from memphis import config

from base import Base


class Principal(object):

    def __init__(self, uuid, name, login):
        self.uuid = uuid
        self.name = name
        self.login = login


class TestAuthentication(Base):

    def tearDown(self):
        config.cleanUp(self.__class__.__module__)
        super(TestAuthentication, self).tearDown()

    def test_auth_simple(self):
        import ptah

        info = ptah.authService.authenticate(
            {'login': 'user', 'password': '12345'})

        self.assertFalse(info.status)

        class Provider(object):
            def authenticate(self, creds):
                if creds['login'] == 'user':
                    return Principal('1', 'user', 'user')

        ptah.registerProvider('test-provider', Provider())

        info = ptah.authService.authenticate(
            {'login': 'user', 'password': '12345'})

        self.assertTrue(info.status)
        self.assertEqual(info.uuid, '1')

    def test_auth_checker(self):
        import ptah

        principal = Principal('1', 'user', 'user')
        
        info = ptah.authService.authenticatePrincipal(principal)
        self.assertTrue(info.status)
        self.assertEqual(info.uuid, '1')
        self.assertEqual(info.message, '')
        self.assertEqual(info.arguments, {})

        class Provider(object):
            def authenticate(self, creds):
                if creds['login'] == 'user':
                    return Principal('1', 'user', 'user')

        ptah.registerProvider('test-provider', Provider())

        def checker(info):
            info.message = 'Suspended'
            info.arguments['additional'] = 'test'
            return False

        ptah.registerAuthChecker(checker)

        info = ptah.authService.authenticate(
            {'login': 'user', 'password': '12345'})

        self.assertFalse(info.status)
        self.assertEqual(info.uuid, '1')
        self.assertEqual(info.message, 'Suspended')
        self.assertEqual(info.arguments, {'additional': 'test'})

        principal = Principal('1', 'user', 'user')
        
        info = ptah.authService.authenticatePrincipal(principal)
        self.assertFalse(info.status)
        self.assertEqual(info.uuid, '1')
        self.assertEqual(info.message, 'Suspended')
        self.assertEqual(info.arguments, {'additional': 'test'})

    def test_auth_get_set_userid(self):
        import ptah
        import ptah.authentication

        self.assertEqual(ptah.authService.getUserId(), None)

        ptah.authService.setUserId('user')
        self.assertEqual(ptah.authService.getUserId(), 'user')

        ptah.authentication.resetAuthCache(None)
        self.assertEqual(ptah.authService.getUserId(), None)

    def test_auth_principal(self):
        import ptah

        principal = Principal('1', 'user', 'user')
        def resolver(uuid):
            if uuid == 'test:1':
                return principal

        ptah.registerResolver('test', resolver)

        self.assertEqual(ptah.authService.getCurrentPrincipal(), None)

        ptah.authService.setUserId('test:1')
        self.assertEqual(ptah.authService.getCurrentPrincipal(), principal)

    def test_auth_principal_login(self):
        import ptah

        principal = Principal('1', 'user', 'user')
        class Provider(object):
            def getPrincipalByLogin(self, login):
                if login == 'user':
                    return principal

        ptah.registerProvider('test-provider', Provider())

        self.assertEqual(
            ptah.authService.getPrincipalByLogin('user2'), None)

        self.assertEqual(
            ptah.authService.getPrincipalByLogin('user'), principal)


class TestPrincipalSearcher(Base):

    def test_principal_searcher(self):
        import ptah
        
        principal = Principal('1', 'user', 'user')
        def search(term=''):
            if term == 'user':
                yield principal

        ptah.registerSearcher('test-provider', search)
        self.assertEqual(list(ptah.searchPrincipals('user')), [principal])
