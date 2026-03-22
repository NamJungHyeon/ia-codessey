"""
Mars Base Inventory Management System
화성 기지 재고 관리 및 인화성 물질 분류 시스템
"""

import csv
import pickle


CSV_FILE = 'Mars_Base_Inventory_List.csv'
DANGER_CSV_FILE = 'Mars_Base_Inventory_danger.csv'
BIN_FILE = 'Mars_Base_Inventory_List.bin'
FLAMMABILITY_THRESHOLD = 0.7


def read_csv(file_path):
    """CSV 파일을 읽어 리스트로 반환한다."""
    inventory = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row['Flammability'] = float(row['Flammability'])
                except ValueError:
                    row['Flammability'] = 0.0
                inventory.append(row)
    except FileNotFoundError:
        print(f'오류: 파일을 찾을 수 없습니다 - {file_path}')
    except PermissionError:
        print(f'오류: 파일 접근 권한이 없습니다 - {file_path}')
    except Exception as e:
        print(f'오류: 파일 읽기 실패 - {e}')
    return inventory


def print_inventory(inventory, title='재고 목록'):
    """재고 목록을 출력한다."""
    print(f'\n{"=" * 70}')
    print(f' {title}')
    print(f'{"=" * 70}')
    print(f'{"물질명":<25} {"밀도(g/cm³)":<15} {"비중":<10} {"강도":<12} {"인화성"}')
    print(f'{"-" * 70}')
    for item in inventory:
        print(
            f'{item["Substance"]:<25} '
            f'{item["Weight (g/cm³)"]:<15} '
            f'{item["Specific Gravity"]:<10} '
            f'{item["Strength"]:<12} '
            f'{item["Flammability"]}'
        )
    print(f'{"=" * 70}')
    print(f'총 {len(inventory)}개 항목\n')


def sort_by_flammability(inventory):
    """인화성 기준 내림차순 정렬된 새 리스트를 반환한다."""
    return sorted(inventory, key=lambda x: x['Flammability'], reverse=True)


def filter_dangerous(inventory, threshold):
    """인화성 지수가 threshold 이상인 항목만 반환한다."""
    return [item for item in inventory if item['Flammability'] >= threshold]


def save_csv(inventory, file_path):
    """재고 목록을 CSV 파일로 저장한다."""
    if not inventory:
        print(f'저장할 데이터가 없습니다: {file_path}')
        return
    try:
        fieldnames = ['Substance', 'Weight (g/cm³)', 'Specific Gravity', 'Strength', 'Flammability']
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(inventory)
        print(f'CSV 저장 완료: {file_path}')
    except PermissionError:
        print(f'오류: 파일 쓰기 권한이 없습니다 - {file_path}')
    except Exception as e:
        print(f'오류: CSV 저장 실패 - {e}')


def save_binary(inventory, file_path):
    """재고 목록을 이진 파일로 저장한다."""
    try:
        with open(file_path, 'wb') as f:
            pickle.dump(inventory, f)
        print(f'이진 파일 저장 완료: {file_path}')
    except PermissionError:
        print(f'오류: 파일 쓰기 권한이 없습니다 - {file_path}')
    except Exception as e:
        print(f'오류: 이진 파일 저장 실패 - {e}')


def load_binary(file_path):
    """이진 파일에서 재고 목록을 읽어 반환한다."""
    inventory = []
    try:
        with open(file_path, 'rb') as f:
            inventory = pickle.load(f)
        print(f'이진 파일 읽기 완료: {file_path}')
    except FileNotFoundError:
        print(f'오류: 파일을 찾을 수 없습니다 - {file_path}')
    except Exception as e:
        print(f'오류: 이진 파일 읽기 실패 - {e}')
    return inventory


def main():
    # 1. CSV 파일 읽기 및 출력
    inventory = read_csv(CSV_FILE)
    print_inventory(inventory, '화성 기지 전체 재고 목록')

    # 2. 인화성 높은 순으로 정렬
    sorted_inventory = sort_by_flammability(inventory)
    print_inventory(sorted_inventory, '인화성 순 정렬 목록')

    # 3. 인화성 0.7 이상 위험 물질 필터링 및 출력
    dangerous = filter_dangerous(sorted_inventory, FLAMMABILITY_THRESHOLD)
    print_inventory(dangerous, f'인화성 {FLAMMABILITY_THRESHOLD} 이상 위험 물질 목록')

    # 4. 위험 물질 목록 CSV 저장
    save_csv(dangerous, DANGER_CSV_FILE)

    # 보너스: 이진 파일 저장 및 읽기
    save_binary(sorted_inventory, BIN_FILE)
    loaded = load_binary(BIN_FILE)
    print_inventory(loaded, '이진 파일에서 읽어온 인화성 순 정렬 목록')


if __name__ == '__main__':
    main()
