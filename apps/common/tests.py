import importlib.util
import os
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings

SETTINGS_PATH = Path(settings.BASE_DIR) / 'config' / 'settings.py'

HTTPS_SETTINGS = (
    'SESSION_COOKIE_SECURE',
    'CSRF_COOKIE_SECURE',
    'SECURE_PROXY_SSL_HEADER',
    'SECURE_HSTS_SECONDS',
    'SECURE_HSTS_INCLUDE_SUBDOMAINS',
    'SECURE_SSL_REDIRECT',
)


def load_settings(**env):
    """
    Execute config/settings.py as a throwaway module under exactly the given
    environment, so the result does not depend on the developer's own .env.
    """
    with mock.patch.dict(os.environ, env, clear=True):
        spec = importlib.util.spec_from_file_location('settings_under_test', SETTINGS_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class HttpsHardeningSettingsTests(TestCase):
    def test_cookies_are_secure_and_hsts_is_on_when_debug_is_off(self):
        config = load_settings(DEBUG='False')

        self.assertTrue(config.SESSION_COOKIE_SECURE)
        self.assertTrue(config.CSRF_COOKIE_SECURE)
        self.assertEqual(config.SECURE_PROXY_SSL_HEADER, ('HTTP_X_FORWARDED_PROTO', 'https'))
        self.assertEqual(config.SECURE_HSTS_SECONDS, 31536000)
        self.assertTrue(config.SECURE_HSTS_INCLUDE_SUBDOMAINS)

    def test_ssl_redirect_is_opt_in(self):
        self.assertFalse(load_settings(DEBUG='False').SECURE_SSL_REDIRECT)
        self.assertTrue(load_settings(DEBUG='False', SECURE_SSL_REDIRECT='True').SECURE_SSL_REDIRECT)

    def test_hsts_duration_can_be_overridden(self):
        config = load_settings(DEBUG='False', SECURE_HSTS_SECONDS='3600')

        self.assertEqual(config.SECURE_HSTS_SECONDS, 3600)

    def test_local_development_over_http_is_unaffected(self):
        config = load_settings(DEBUG='True', SECURE_SSL_REDIRECT='True', SECURE_HSTS_SECONDS='3600')

        self.assertFalse(config.SESSION_COOKIE_SECURE)
        self.assertFalse(config.CSRF_COOKIE_SECURE)
        for name in ('SECURE_PROXY_SSL_HEADER', 'SECURE_HSTS_SECONDS', 'SECURE_HSTS_INCLUDE_SUBDOMAINS', 'SECURE_SSL_REDIRECT'):
            self.assertFalse(hasattr(config, name), f'{name} must not be set when DEBUG is on')


class HttpsHardeningBehaviourTests(TestCase):
    """The production settings, applied to the real middleware stack."""

    def production_overrides(self):
        config = load_settings(DEBUG='False')
        return override_settings(**{name: getattr(config, name) for name in HTTPS_SETTINGS})

    def test_admin_login_cookies_are_marked_secure(self):
        with self.production_overrides():
            response = self.client.get('/admin/login/', HTTP_X_FORWARDED_PROTO='https')

        self.assertTrue(response.cookies['csrftoken']['secure'])

    def test_hsts_header_is_sent_behind_the_tls_terminating_proxy(self):
        with self.production_overrides():
            response = self.client.get('/admin/login/', HTTP_X_FORWARDED_PROTO='https')

        self.assertEqual(response['Strict-Transport-Security'], 'max-age=31536000; includeSubDomains')

    def test_session_cookie_is_marked_secure_on_login(self):
        from django.contrib.auth import get_user_model

        get_user_model().objects.create_superuser('admin', 'admin@example.com', 'a-long-test-password')

        with self.production_overrides():
            response = self.client.post(
                '/admin/login/',
                {'username': 'admin', 'password': 'a-long-test-password'},
                HTTP_X_FORWARDED_PROTO='https',
            )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.cookies['sessionid']['secure'])
