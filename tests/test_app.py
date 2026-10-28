import os
import tempfile
import unittest

from app import VERSION, create_app


class VPCraftApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ['DATABASE_PATH'] = os.path.join(self.temp_dir.name, 'test.db')
        self.client = create_app().test_client()

    def tearDown(self):
        self.temp_dir.cleanup()
        os.environ.pop('DATABASE_PATH', None)

    def test_dashboard_is_served(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'VPCraft', response.data)

    def test_static_assets_are_served(self):
        self.assertEqual(self.client.get('/styles.css').status_code, 200)
        self.assertEqual(self.client.get('/app.js').status_code, 200)

    def test_health_endpoint(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['status'], 'healthy')
        self.assertEqual(payload['version'], VERSION)

    def test_readiness_endpoint_checks_database(self):
        response = self.client.get('/ready')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['database'], 'reachable')

    def test_overview_contains_platform_metadata(self):
        payload = self.client.get('/api/overview').get_json()
        self.assertEqual(payload['platform'], 'VPCraft')
        self.assertEqual(payload['version'], VERSION)
        self.assertIn('instance', payload)
        self.assertEqual(payload['latest_events'][0]['status'], 'started')

    def test_system_metrics_shape(self):
        payload = self.client.get('/api/system').get_json()
        for key in ('hostname', 'python', 'load', 'memory', 'disk', 'app_uptime_seconds'):
            self.assertIn(key, payload)
        self.assertGreaterEqual(payload['load']['cpu_count'], 1)

    def test_status_records_latency_samples(self):
        payload = self.client.get('/api/status').get_json()
        self.assertEqual(payload['status'], 'ok')
        self.assertEqual(payload['sample_count'], 1)
        self.assertGreaterEqual(payload['latency_ms'], 0)

    def test_status_throttles_sampling(self):
        self.client.get('/api/status')
        payload = self.client.get('/api/status').get_json()
        self.assertEqual(payload['sample_count'], 1)

    def test_unknown_route_returns_json_404(self):
        response = self.client.get('/does-not-exist')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.get_json())


if __name__ == '__main__':
    unittest.main()
