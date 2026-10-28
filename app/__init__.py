from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import os
import sqlite3
import time

from flask import Flask, jsonify, send_from_directory

from . import system

VERSION = '1.0.0'
SAMPLE_INTERVAL_SECONDS = 5
MAX_SAMPLES = 500
MAX_EVENTS = 100


def utc_now():
    return datetime.now(timezone.utc)


def create_app():
    app = Flask(__name__)
    web_dir = Path(__file__).resolve().parent.parent / 'web'
    app.config['DATABASE_PATH'] = os.getenv('DATABASE_PATH', str(Path(app.instance_path) / 'vpcraft.db'))
    environment = os.getenv('APP_ENV', 'local')

    @contextmanager
    def database():
        Path(app.config['DATABASE_PATH']).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(app.config['DATABASE_PATH'], timeout=5)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    with database() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            environment TEXT NOT NULL,
            version TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS health_samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latency_ms REAL NOT NULL,
            created_at TEXT NOT NULL
        )''')
        db.execute('INSERT INTO events(environment, version, status, created_at) VALUES (?, ?, ?, ?)',
                   (environment, VERSION, 'started', utc_now().isoformat()))
        db.execute('DELETE FROM events WHERE id <= (SELECT MAX(id) FROM events) - ?', (MAX_EVENTS,))

    @app.after_request
    def security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('Cache-Control', 'no-store')
        return response

    @app.get('/')
    def dashboard():
        return send_from_directory(web_dir, 'index.html')

    @app.get('/styles.css')
    def styles():
        return send_from_directory(web_dir, 'styles.css')

    @app.get('/app.js')
    def browser_script():
        return send_from_directory(web_dir, 'app.js')

    @app.get('/health')
    def health():
        return jsonify(status='healthy', service='vpcraft-api', version=VERSION), 200

    @app.get('/ready')
    def ready():
        try:
            with database() as db:
                db.execute('SELECT 1').fetchone()
            return jsonify(status='ready', database='reachable'), 200
        except sqlite3.Error:
            return jsonify(status='not_ready', database='unavailable'), 503

    @app.get('/api/overview')
    def overview():
        with database() as db:
            rows = db.execute(
                'SELECT environment, version, status, created_at FROM events ORDER BY id DESC LIMIT 8').fetchall()
        return jsonify({
            'platform': 'VPCraft',
            'version': VERSION,
            'environment': environment,
            'region': os.getenv('AWS_REGION', 'not-deployed'),
            'service_status': 'operational',
            'instance': {
                'id': os.getenv('INSTANCE_ID') or None,
                'type': os.getenv('INSTANCE_TYPE') or None,
                'availability_zone': os.getenv('AVAILABILITY_ZONE') or None,
                'public_ip': os.getenv('PUBLIC_IP') or None,
            },
            'latest_events': [dict(row) for row in rows],
        })

    @app.get('/api/system')
    def system_metrics():
        return jsonify(system.snapshot(str(Path(app.config['DATABASE_PATH']).parent)))

    @app.get('/api/status')
    def status():
        try:
            with database() as db:
                started = time.perf_counter()
                db.execute('SELECT COUNT(*) FROM events').fetchone()
                latency = round((time.perf_counter() - started) * 1000, 3)
                last = db.execute('SELECT created_at FROM health_samples ORDER BY id DESC LIMIT 1').fetchone()
                now = utc_now()
                if last is None or (now - datetime.fromisoformat(last['created_at'])).total_seconds() >= SAMPLE_INTERVAL_SECONDS:
                    db.execute('INSERT INTO health_samples(latency_ms, created_at) VALUES (?, ?)',
                               (latency, now.isoformat()))
                    db.execute('DELETE FROM health_samples WHERE id <= (SELECT MAX(id) FROM health_samples) - ?',
                               (MAX_SAMPLES,))
                samples = db.execute(
                    'SELECT latency_ms, created_at FROM health_samples ORDER BY id DESC LIMIT 30').fetchall()
        except sqlite3.Error:
            return jsonify(status='unavailable'), 503
        series = [dict(row) for row in reversed(samples)]
        values = [item['latency_ms'] for item in series]
        return jsonify({
            'status': 'ok',
            'latency_ms': latency,
            'average_latency_ms': round(sum(values) / len(values), 3),
            'max_latency_ms': max(values),
            'sample_count': len(values),
            'samples': series,
        })

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify(error='Not found'), 404

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify(error='Internal server error'), 500

    return app
