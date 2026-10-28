"""Lightweight host and process metrics read from /proc (no extra dependencies)."""
import os
import shutil
import socket
import platform
import time

_STARTED = time.monotonic()


def app_uptime_seconds():
    return int(time.monotonic() - _STARTED)


def host_uptime_seconds():
    try:
        with open('/proc/uptime') as handle:
            return int(float(handle.read().split()[0]))
    except (OSError, ValueError, IndexError):
        return None


def memory():
    try:
        info = {}
        with open('/proc/meminfo') as handle:
            for line in handle:
                key, value = line.split(':', 1)
                info[key] = int(value.split()[0])
        total = info['MemTotal']
        available = info.get('MemAvailable', info.get('MemFree', 0))
        used = total - available
        return {
            'total_mb': round(total / 1024),
            'used_mb': round(used / 1024),
            'percent': round(used / total * 100, 1),
        }
    except (OSError, KeyError, ValueError, ZeroDivisionError):
        return None


def disk(path):
    target = path if os.path.isdir(path) else '/'
    try:
        usage = shutil.disk_usage(target)
        return {
            'total_gb': round(usage.total / 1024 ** 3, 1),
            'used_gb': round(usage.used / 1024 ** 3, 1),
            'percent': round(usage.used / usage.total * 100, 1),
        }
    except OSError:
        return None


def load():
    cpus = os.cpu_count() or 1
    try:
        one, five, fifteen = os.getloadavg()
    except (OSError, AttributeError):
        return {'cpu_count': cpus, 'one': None, 'five': None, 'fifteen': None, 'percent': None}
    return {
        'cpu_count': cpus,
        'one': round(one, 2),
        'five': round(five, 2),
        'fifteen': round(fifteen, 2),
        'percent': round(min(100.0, one / cpus * 100), 1),
    }


def snapshot(data_dir):
    return {
        'hostname': socket.gethostname(),
        'python': platform.python_version(),
        'load': load(),
        'memory': memory(),
        'disk': disk(data_dir),
        'host_uptime_seconds': host_uptime_seconds(),
        'app_uptime_seconds': app_uptime_seconds(),
    }
