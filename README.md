# Mars Mission Computer

화성 기지의 미션 컴퓨터 상태를 모니터링하는 Python 프로그램입니다.

---

## 파일 구조

```
5nd/
├── mars_mission_computer.py  # 메인 소스 코드
├── setting.txt               # 출력 항목 설정 파일 (선택)
└── README.md
```

---

## 사용 라이브러리

| 라이브러리 | 종류 | 용도 |
|---|---|---|
| `json` | 표준 | 결과를 JSON 형식으로 출력 |
| `os` | 표준 | CPU 코어 수 조회 |
| `platform` | 표준 | OS 및 CPU 정보 조회 |
| `random` | 표준 | 센서 더미 데이터 생성 |
| `sys` | 표준 | 표준 입력 감지 (종료 처리) |
| `threading` | 표준 | 종료 대기 스레드 실행 |
| `time` | 표준 | 주기적 센서 데이터 수집 |
| `psutil` | 외부 | 메모리 크기, CPU/메모리 실시간 사용량 조회 |

> `psutil`은 설치 안 된 경우에도 예외 처리로 안전하게 동작합니다.

---

## 클래스 및 함수 설명

### `_load_settings()` (모듈 레벨 함수)

`setting.txt` 파일을 읽어 출력할 항목을 설정합니다.

- 파일이 없으면 모든 항목을 기본값(`True`)으로 사용합니다.
- `key = value` 형식으로 항목별 출력 여부를 지정합니다.

```
# setting.txt 예시
os_system = true
os_version = false
cpu_type = true
cpu_cores = true
memory_size = true
cpu_usage = true
memory_usage = false
```

---

### `DummySensor` 클래스

실제 센서 대신 랜덤 값을 생성하는 가상 센서입니다.

| 메서드 | 설명 |
|---|---|
| `set_env(env)` | 측정할 센서 타입 지정 |
| `get_env()` | 지정된 센서의 랜덤 값 반환 |

**센서 항목 및 범위**

| 항목 | 범위 |
|---|---|
| 기지 내부 온도 | 18.0 ~ 30.0 °C |
| 기지 외부 온도 | -80.0 ~ 20.0 °C |
| 기지 내부 습도 | 30.0 ~ 70.0 % |
| 외부 조도 | 0.0 ~ 1000.0 |
| 내부 CO2 농도 | 0.02 ~ 0.1 |
| 내부 산소 농도 | 4.0 ~ 7.0 |

---

### `MissionComputer` 클래스

미션 컴퓨터의 핵심 클래스입니다.

#### `get_mission_computer_info()`

미션 컴퓨터의 시스템 정보를 JSON으로 출력합니다.

```json
{
    "os_system": "Darwin",
    "os_version": "Darwin Kernel Version 25.3.0: ...",
    "cpu_type": "arm",
    "cpu_cores": 10,
    "memory_size": "16.0 GB"
}
```

#### `get_mission_computer_load()`

CPU와 메모리의 실시간 사용량을 JSON으로 출력합니다.
(`cpu_percent(interval=1)` 호출로 약 1초 대기 후 출력)

```json
{
    "cpu_usage": "12.5 %",
    "memory_usage": "68.3 %"
}
```

#### `get_sensor_data()`

5초마다 센서 데이터를 수집하여 JSON으로 출력합니다.
5분마다 수집된 데이터의 평균값을 별도로 출력합니다.

```json
{
    "mars_base_internal_temperature": 24.73,
    "mars_base_external_temperature": -42.18,
    "mars_base_internal_humidity": 55.61,
    "mars_base_external_illuminance": 312.44,
    "mars_base_internal_co2": 0.07,
    "mars_base_internal_oxygen": 5.83
}
```

**종료 방법:** Enter 키 입력 또는 `Ctrl+C`

#### `_print_five_min_avg()`

최근 5분간 수집된 센서 데이터의 평균값을 출력하는 내부 메서드입니다.

```
[5-minute average]
{
    "mars_base_internal_temperature": 25.1234,
    ...
}
```

---

## 실행 방법

```bash
python3 mars_mission_computer.py
```

## 실행 흐름

```
실행
 │
 ├─ get_mission_computer_info()  →  시스템 정보 JSON 1회 출력
 │
 ├─ get_mission_computer_load()  →  CPU/메모리 사용량 JSON 1회 출력 (~1초 소요)
 │
 └─ get_sensor_data() 루프 시작
       │
       ├─ [5초마다] 센서 데이터 JSON 출력
       │
       ├─ [5분마다] 5분 평균 JSON 출력
       │
       └─ [Enter 또는 Ctrl+C] → "System stoped...." 출력 후 종료
```
