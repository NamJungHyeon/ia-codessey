"""
door_hacking.py - emergency_storage_key.zip 브루트포스 비밀번호 크래커

비밀번호 형식: 6자리, 소문자(a-z) + 숫자(0-9), 특수문자 없음
"""

import zipfile
import string
import struct
import time
import zlib
import os
import array
import multiprocessing
import concurrent.futures

_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_FILE = os.path.join(_DIR, 'emergency_storage_key.zip')
PASSWORD_FILE = os.path.join(_DIR, 'password.txt')
CHARSET = string.ascii_lowercase + string.digits
PASSWORD_LENGTH = 6

# ZipCrypto용 CRC32 테이블 (사전 계산, 모듈 로드 시 1회만 실행)
_CRC32 = array.array('I', [0] * 256)
for _i in range(256):
    _v = _i
    for _ in range(8):
        _v = (_v >> 1) ^ 0xEDB88320 if _v & 1 else _v >> 1
    _CRC32[_i] = _v


def _read_zip_crypto_data(zip_path):
    """암호화 헤더(12바이트)와 검증 바이트를 zip에서 추출."""
    with open(zip_path, 'rb') as f:
        raw = f.read(30)
    sig, _, flags, _, mod_time, _, crc, _, _, fname_len, extra_len = \
        struct.unpack_from('<4sHHHHHIIIHH', raw)
    if sig != b'PK\x03\x04':
        raise ValueError('유효하지 않은 zip 파일입니다.')
    with open(zip_path, 'rb') as f:
        f.seek(30 + fname_len + extra_len)
        enc_header = f.read(12)
    check_byte = (mod_time >> 8) & 0xFF if (flags & 0x08) else (crc >> 24) & 0xFF
    return bytes(enc_header), check_byte


def _try_password(enc_header, check_byte, pwd_ints):
    """ZipCrypto 헤더 검증 (12바이트, 예외 없음) → 빠른 1차 필터."""
    t = _CRC32
    k0, k1, k2 = 0x12345678, 0x23456789, 0x34567890
    for c in pwd_ints:
        k0 = t[(k0 ^ c) & 0xFF] ^ (k0 >> 8)
        k1 = (k1 + (k0 & 0xFF)) & 0xFFFFFFFF
        k1 = (k1 * 134775813 + 1) & 0xFFFFFFFF
        k2 = t[(k2 ^ (k1 >> 24)) & 0xFF] ^ (k2 >> 8)
    d = 0
    for b in enc_header:
        tmp = k2 | 2
        d = b ^ (((tmp * (tmp ^ 1)) >> 8) & 0xFF)
        k0 = t[(k0 ^ d) & 0xFF] ^ (k0 >> 8)
        k1 = (k1 + (k0 & 0xFF)) & 0xFFFFFFFF
        k1 = (k1 * 134775813 + 1) & 0xFFFFFFFF
        k2 = t[(k2 ^ (k1 >> 24)) & 0xFF] ^ (k2 >> 8)
    return d == check_byte


def _worker(args):
    """
    멀티프로세스 워커.
    - zipfile/파일핸들 없음 → 프로세스 간 충돌 없음
    - _try_password로 빠르게 필터 후 오탐만 zipfile 검증
    """
    zip_path, enc_header, check_byte, start_idx, count, charset_bytes, pwd_len = args
    clen = len(charset_bytes)
    total = clen ** pwd_len

    for offset in range(count):
        idx = start_idx + offset
        if idx >= total:
            break

        # 선형 인덱스 → 비밀번호 (정수 리스트)
        pwd = []
        n = idx
        for _ in range(pwd_len):
            pwd.append(charset_bytes[n % clen])
            n //= clen
        pwd.reverse()

        if not _try_password(enc_header, check_byte, pwd):
            continue

        # 후보 발견 → zipfile로 최종 검증 (오탐 제거)
        password = bytes(pwd).decode()
        try:
            with zipfile.ZipFile(zip_path) as zf:
                zf.read(zf.namelist()[0], pwd=password.encode())
            return password
        except (RuntimeError, zlib.error, zipfile.BadZipFile):
            pass

    return None


def _save_password(found_password, attempts, elapsed_total):
    if found_password:
        print(f'[+] 비밀번호 발견: {found_password}')
        print(f'[+] 총 시도 횟수 : {attempts:,}')
        print(f'[+] 총 소요 시간 : {elapsed_total:.2f}초')
        try:
            with open(PASSWORD_FILE, 'w') as f:
                f.write(found_password)
            print(f'[+] 비밀번호 저장: {PASSWORD_FILE}')
        except OSError as e:
            print(f'[!] 파일 저장 실패: {e}')
    else:
        print('[!] 탐색 범위 내에서 비밀번호를 찾지 못했습니다.')
        print(f'[*] 총 시도 횟수 : {attempts:,}')
        print(f'[*] 총 소요 시간 : {elapsed_total:.2f}초')


def unlock_zip_fast():
    """멀티프로세스 크래커 - 모든 CPU 코어 활용."""
    total = len(CHARSET) ** PASSWORD_LENGTH
    num_cores = multiprocessing.cpu_count()

    print(f'[*] 대상 파일    : {ZIP_FILE}')
    print(f'[*] 문자 집합    : {CHARSET}')
    print(f'[*] 비밀번호 길이: {PASSWORD_LENGTH}')
    print(f'[*] 탐색 공간    : {total:,} 조합')
    print(f'[*] CPU 코어 수  : {num_cores}')
    print('-' * 60)

    try:
        enc_header, check_byte = _read_zip_crypto_data(ZIP_FILE)
    except FileNotFoundError:
        print(f'[!] 오류: "{ZIP_FILE}" 파일을 찾을 수 없습니다.')
        return None
    except (zipfile.BadZipFile, ValueError) as e:
        print(f'[!] 오류: {e}')
        return None

    charset_bytes = CHARSET.encode()
    # 코어당 200청크 → 각 청크가 충분히 작아 조기 종료 시 빠르게 반환
    chunk_size = max(1, total // (num_cores * 200))
    chunk_args = [
        (ZIP_FILE, enc_header, check_byte, start, chunk_size, charset_bytes, PASSWORD_LENGTH)
        for start in range(0, total, chunk_size)
    ]
    num_chunks = len(chunk_args)

    start_time = time.time()
    print(f'[*] 시작 시각    : {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))}')
    print(f'[*] 총 청크 수   : {num_chunks:,}  (청크당 {chunk_size:,} 조합)')
    print('[*] 크래킹 중... (프로세스 초기화 중, 잠시 대기)\n')

    found_password = None
    completed = 0

    executor = concurrent.futures.ProcessPoolExecutor(max_workers=num_cores)
    futures = [executor.submit(_worker, args) for args in chunk_args]

    try:
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            try:
                result = future.result()
            except Exception:
                result = None
            elapsed = time.time() - start_time
            progress = completed / num_chunks * 100
            speed_est = (completed * chunk_size) / elapsed if elapsed > 0 else 0
            print(
                f'  [{progress:>5.1f}%] '
                f'청크: {completed:>5} / {num_chunks} | '
                f'경과: {elapsed:>7.1f}초 | '
                f'속도(추정): {speed_est:>11,.0f} pw/s'
            )
            if result is not None:
                found_password = result
                for f in futures:
                    f.cancel()
                break
    except KeyboardInterrupt:
        print('\n[!] 사용자가 중단했습니다.')
        for f in futures:
            f.cancel()
    finally:
        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except TypeError:
            # Python 3.8 이하: cancel_futures 미지원
            executor.shutdown(wait=False)

    elapsed_total = time.time() - start_time
    print()
    _save_password(found_password, completed * chunk_size, elapsed_total)
    return found_password


if __name__ == '__main__':
    multiprocessing.freeze_support()  # Windows 실행파일 지원
    unlock_zip_fast()
