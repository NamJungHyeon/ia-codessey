# mars_mission_computer.py

화성 기지의 환경 센서 데이터를 수집하고 출력하는 미션 컴퓨터 시뮬레이터입니다.

---

## 사용 방법

```bash
python3 mars_mission_computer.py
```

실행하면 5초마다 센서 데이터가 JSON 형태로 출력됩니다.
**Enter** 키를 누르거나 **Ctrl+C** 를 입력하면 종료됩니다.

---

## 구조 개요

```
mars_mission_computer.py
├── DummySensor       # 센서 역할을 하는 클래스 (랜덤값 생성)
└── MissionComputer   # 미션 컴퓨터 클래스 (데이터 수집 및 출력)
    └── RunComputer   # MissionComputer 인스턴스 (실행 진입점)
```

---

## 클래스 설명

### DummySensor

실제 하드웨어 센서 대신 랜덤한 값을 생성하는 더미 센서 클래스입니다.

#### 속성

| 속성 | 설명 |
|------|------|
| `env` | 현재 측정 중인 센서 종류 (기본값: `None`) |
| `_ranges` | 센서 종류별 값의 최소/최대 범위를 담은 딕셔너리 |

#### 센서 종류 및 값 범위

| 센서 키 | 설명 | 범위 |
|---------|------|------|
| `mars_base_internal_temperature` | 기지 내부 온도 (°C) | 18.0 ~ 30.0 |
| `mars_base_external_temperature` | 기지 외부 온도 (°C) | -80.0 ~ 20.0 |
| `mars_base_internal_humidity` | 기지 내부 습도 (%) | 30.0 ~ 70.0 |
| `mars_base_external_illuminance` | 기지 외부 광량 (lux) | 0.0 ~ 1000.0 |
| `mars_base_internal_co2` | 기지 내부 이산화탄소 농도 (%) | 0.02 ~ 0.1 |
| `mars_base_internal_oxygen` | 기지 내부 산소 농도 (%) | 4.0 ~ 7.0 |

#### 메소드

**`set_env(env)`**
- 측정할 센서 종류를 지정합니다.
- `env`가 `_ranges`에 없는 키일 경우 `ValueError`를 발생시킵니다.

**`get_env()`**
- 현재 지정된 센서의 랜덤 측정값을 반환합니다.
- `set_env()` 호출 없이 사용하면 `RuntimeError`를 발생시킵니다.

---

### MissionComputer

센서 데이터를 주기적으로 수집하고 출력하는 미션 컴퓨터 클래스입니다.

#### 속성

| 속성 | 설명 |
|------|------|
| `env_values` | 6가지 환경값을 저장하는 딕셔너리 |
| `ds` | `DummySensor` 인스턴스 |
| `_running` | 데이터 수집 루프의 실행 상태 플래그 |
| `_history` | 5분 평균 계산을 위한 측정값 누적 리스트 |

#### 메소드

**`get_sensor_data()`**

메인 루프를 실행하는 메소드입니다. 아래 동작을 5초마다 반복합니다.

1. `DummySensor`로부터 6가지 환경값을 읽어 `env_values`에 저장
2. `env_values`를 JSON 형태로 출력
3. 5분(300초) 경과 시 `_print_five_min_avg()` 호출 후 기록 초기화

```json
{
    "mars_base_internal_temperature": 22.45,
    "mars_base_external_temperature": -35.12,
    "mars_base_internal_humidity": 51.30,
    "mars_base_external_illuminance": 487.60,
    "mars_base_internal_co2": 0.05,
    "mars_base_internal_oxygen": 5.73
}
```

**`_wait_for_stop()`**

백그라운드 스레드에서 실행되며, Enter 키 입력을 감지하면 루프를 멈춥니다.
stdin이 닫히거나 파이프 환경에서 발생하는 `EOFError`, `OSError`를 처리합니다.

**`_print_five_min_avg()`**

최근 5분간 누적된 측정값의 평균을 계산해 JSON 형태로 출력합니다.
센서 오류로 `None`이 포함된 경우 해당 값은 평균 계산에서 제외됩니다.

```json
[5-minute average]
{
    "mars_base_internal_temperature": 24.1023,
    "mars_base_external_temperature": -41.2387,
    ...
}
```

---

## 종료 방법

| 방법 | 동작 |
|------|------|
| **Enter** 키 입력 | 루프 종료 후 `System stoped....` 출력 |
| **Ctrl+C** | `KeyboardInterrupt` 처리 후 `System stoped....` 출력 |

---

## 예외처리 목록

| 위치 | 예외 종류 | 처리 내용 |
|------|-----------|-----------|
| `set_env()` | `ValueError` | 잘못된 센서 키 전달 시 오류 발생 |
| `get_env()` | `RuntimeError` | `set_env()` 미호출 상태에서 사용 시 오류 발생 |
| `get_sensor_data()` 센서 수집 | `ValueError`, `RuntimeError` | 한 센서의 오류가 전체 루프를 멈추지 않도록 개별 처리 |
| `get_sensor_data()` JSON 출력 | `TypeError`, `ValueError` | 직렬화 불가 값 방어 처리 |
| `get_sensor_data()` 루프 전체 | `KeyboardInterrupt` | Ctrl+C로 안전하게 종료 |
| `_wait_for_stop()` | `EOFError`, `OSError` | stdin 닫힘 또는 파이프 환경 대응 |
| `_print_five_min_avg()` | `None` 값 필터링 | 센서 오류로 None이 남은 경우 평균 계산 TypeError 방지 |
| `_print_five_min_avg()` JSON 출력 | `TypeError`, `ValueError` | 직렬화 불가 값 방어 처리 |

---

## 실행 흐름

```
python3 mars_mission_computer.py
        |
        v
  MissionComputer 인스턴스 생성 (RunComputer)
        |
        v
  get_sensor_data() 호출
        |
        +-- 백그라운드 스레드 시작 (_wait_for_stop)
        |
        v
  [루프 시작] ──────────────────────────────────────┐
        |                                            |
        v                                            |
  DummySensor로 6가지 환경값 수집                    |
        |                                            |
        v                                            |
  env_values를 JSON으로 출력                         |
        |                                            |
        v                                            |
  5분 경과 여부 확인                                  |
  └─ 경과 시: 5분 평균 출력 및 기록 초기화           |
        |                                            |
        v                                            |
  5초 대기 ────────────────────────────────────────┘
        |
  Enter 또는 Ctrl+C 입력 시 루프 탈출
        |
        v
  'System stoped....' 출력
```

---

## 제약 사항

- Python 3.x 사용
- 표준 라이브러리만 사용 (`json`, `time`, `random`, `threading`, `sys`)
- PEP 8 스타일 가이드 준수
