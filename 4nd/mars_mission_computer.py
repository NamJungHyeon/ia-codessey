import json
import time
import random
import threading
import sys


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

    def get_sensor_data(self):
        self._running = True
        last_avg_time = time.time()

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

                time.sleep(5)

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


RunComputer = MissionComputer()
RunComputer.get_sensor_data()
