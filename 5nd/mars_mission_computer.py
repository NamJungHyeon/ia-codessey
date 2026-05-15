import json
import os
import platform
import random
import sys
import threading
import time

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def _load_settings():
    defaults = {
        'os_system': True,
        'os_version': True,
        'cpu_type': True,
        'cpu_cores': True,
        'memory_size': True,
        'cpu_usage': True,
        'memory_usage': True,
    }
    try:
        with open('setting.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip().lower()
                    if key in defaults:
                        defaults[key] = (value == 'true')
    except FileNotFoundError:
        pass
    except OSError as e:
        print(f'Setting file load error: {e}')
    except Exception as e:
        print(f'Unexpected error while loading settings: {e}')
    return defaults


class DummySensor:
    def __init__(self):
        self.env = None
        self._ranges = {
            'mars_base_internal_temperature': (18.0, 30.0),
            'mars_base_external_temperature': (-80.0, 20.0),
            'mars_base_internal_humidity': (30.0, 70.0),
            'mars_base_external_illuminance': (0.0, 1000.0),
            'mars_base_internal_co2': (0.02, 0.1),
            'mars_base_internal_oxygen': (4.0, 7.0),
        }

    def set_env(self, env):
        if env not in self._ranges:
            raise ValueError(f"Unknown sensor type: '{env}'")
        self.env = env

    def get_env(self):
        if self.env is None:
            raise RuntimeError('Sensor environment not set. Call set_env() first.')
        low, high = self._ranges[self.env]
        return round(random.uniform(low, high), 2)


class MissionComputer:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': None,
            'mars_base_external_temperature': None,
            'mars_base_internal_humidity': None,
            'mars_base_external_illuminance': None,
            'mars_base_internal_co2': None,
            'mars_base_internal_oxygen': None,
        }
        self.ds = DummySensor()
        self._running = False
        self._history = []
        self._settings = _load_settings()

    def get_mission_computer_info(self):
        settings = self._settings
        info = {}

        if settings.get('os_system', True):
            try:
                info['os_system'] = platform.system()
            except Exception as e:
                info['os_system'] = f'Error: {e}'

        if settings.get('os_version', True):
            try:
                info['os_version'] = platform.version()
            except Exception as e:
                info['os_version'] = f'Error: {e}'

        if settings.get('cpu_type', True):
            try:
                cpu = platform.processor() or platform.machine()
                info['cpu_type'] = cpu if cpu else 'Unknown'
            except Exception as e:
                info['cpu_type'] = f'Error: {e}'

        if settings.get('cpu_cores', True):
            try:
                info['cpu_cores'] = os.cpu_count()
            except Exception as e:
                info['cpu_cores'] = f'Error: {e}'

        if settings.get('memory_size', True):
            try:
                if not PSUTIL_AVAILABLE:
                    raise RuntimeError('psutil is not installed.')
                total = psutil.virtual_memory().total
                info['memory_size'] = f'{round(total / (1024 ** 3), 2)} GB'
            except Exception as e:
                info['memory_size'] = f'Error: {e}'

        try:
            print(json.dumps(info, indent=4))
        except (TypeError, ValueError) as e:
            print(f'JSON serialization error: {e}')

    def get_mission_computer_load(self):
        settings = self._settings
        load = {}

        if settings.get('cpu_usage', True):
            try:
                if not PSUTIL_AVAILABLE:
                    raise RuntimeError('psutil is not installed.')
                load['cpu_usage'] = f'{psutil.cpu_percent(interval=1)} %'
            except Exception as e:
                load['cpu_usage'] = f'Error: {e}'

        if settings.get('memory_usage', True):
            try:
                if not PSUTIL_AVAILABLE:
                    raise RuntimeError('psutil is not installed.')
                load['memory_usage'] = f'{psutil.virtual_memory().percent} %'
            except Exception as e:
                load['memory_usage'] = f'Error: {e}'

        try:
            print(json.dumps(load, indent=4))
        except (TypeError, ValueError) as e:
            print(f'JSON serialization error: {e}')

    def get_sensor_data(self):
        self._running = True
        last_avg_time = time.time()
        next_tick = time.time() + 5

        stop_thread = threading.Thread(target=self._wait_for_stop, daemon=True)
        stop_thread.start()

        try:
            while self._running:
                for key in self.env_values:
                    try:
                        self.ds.set_env(key)
                        self.env_values[key] = self.ds.get_env()
                    except (ValueError, RuntimeError) as e:
                        print(f'Sensor error [{key}]: {e}')

                self._history.append(dict(self.env_values))

                try:
                    print(json.dumps(self.env_values, indent=4))
                except (TypeError, ValueError) as e:
                    print(f'JSON serialization error: {e}')

                current_time = time.time()
                if current_time - last_avg_time >= 300:
                    self._print_five_min_avg()
                    self._history.clear()
                    last_avg_time = current_time

                # 드리프트 보정: 실행 시간을 제외한 나머지만 대기
                sleep_time = next_tick - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                next_tick += 5

        except KeyboardInterrupt:
            pass

        print('System stoped....')

    def _wait_for_stop(self):
        try:
            sys.stdin.readline()
        except (EOFError, OSError):
            pass
        self._running = False

    def _print_five_min_avg(self):
        if not self._history:
            return

        avg = {}
        for key in self.env_values:
            values = [h[key] for h in self._history if h.get(key) is not None]
            if values:
                avg[key] = round(sum(values) / len(values), 4)
            else:
                avg[key] = None

        print('\n[5-minute average]')
        try:
            print(json.dumps(avg, indent=4))
        except (TypeError, ValueError) as e:
            print(f'JSON serialization error: {e}')


runComputer = MissionComputer()
runComputer.get_mission_computer_info()
runComputer.get_mission_computer_load()
runComputer.get_sensor_data()
