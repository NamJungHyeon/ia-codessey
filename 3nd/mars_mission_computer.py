import random
import datetime


class DummySensor:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0,
            'mars_base_external_temperature': 0,
            'mars_base_internal_humidity': 0,
            'mars_base_external_illuminance': 0,
            'mars_base_internal_co2': 0,
            'mars_base_internal_oxygen': 0,
        }

    def set_env(self):
        self.env_values['mars_base_internal_temperature'] = round(random.uniform(18, 30), 2)
        self.env_values['mars_base_external_temperature'] = round(random.uniform(0, 21), 2)
        self.env_values['mars_base_internal_humidity'] = round(random.uniform(50, 60), 2)
        self.env_values['mars_base_external_illuminance'] = round(random.uniform(500, 715), 2)
        self.env_values['mars_base_internal_co2'] = round(random.uniform(0.02, 0.1), 4)
        self.env_values['mars_base_internal_oxygen'] = round(random.uniform(4, 7), 2)

    def get_env(self):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = (
            f"{timestamp}, "
            f"{self.env_values['mars_base_internal_temperature']}, "
            f"{self.env_values['mars_base_external_temperature']}, "
            f"{self.env_values['mars_base_internal_humidity']}, "
            f"{self.env_values['mars_base_external_illuminance']}, "
            f"{self.env_values['mars_base_internal_co2']}, "
            f"{self.env_values['mars_base_internal_oxygen']}"
        )
        with open('sensor_log.log', 'a') as log_file:
            log_file.write(log_line + '\n')
        return self.env_values


ds = DummySensor()
ds.set_env()
env = ds.get_env()

print('----------------------------------------------')
print(f"  화성 기지 내부 온도   : {env['mars_base_internal_temperature']} °C")
print(f"  화성 기지 외부 온도   : {env['mars_base_external_temperature']} °C")
print(f"  화성 기지 내부 습도   : {env['mars_base_internal_humidity']} %")
print(f"  화성 기지 외부 광량   : {env['mars_base_external_illuminance']} W/m²")
print(f"  화성 기지 내부 CO2   : {env['mars_base_internal_co2']} %")
print(f"  화성 기지 내부 산소   : {env['mars_base_internal_oxygen']} %")
print('----------------------------------------------')
