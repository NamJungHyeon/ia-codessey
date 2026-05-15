# main.py
import os


def check_system():
    '''시스템 연결 확인을 위한 초기화 함수'''
    # 작은따옴표(' ') 사용 및 대입 연산자(=) 앞뒤 공백 준수
    greeting = 'Hello Mars'
    print(greeting)
    print('-' * 30)


def analyze_mission_log(file_path):
    '''
    로그 파일을 읽어 분석하고, 시간 역순 출력 및 오류 사항을 별도로 저장한다.
    '''
    # 파일 존재 여부 확인 (예외 처리의 시작)
    if not os.path.exists(file_path):
        print(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
        return

    try:
        # UTF-8 인코딩으로 파일 열기
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        if not lines:
            print('로그 파일이 비어 있습니다.')
            return

        # 1. 보너스 과제: 출력 결과를 시간의 역순으로 정렬하여 출력
        print('[로그 분석 결과 - 시간 역순]')
        reversed_logs = lines[::-1]
        for line in reversed_logs:
            print(line.strip())

        # 2. 보너스 과제: 문제가 되는 부분(ERROR, CRITICAL)만 추출하여 별도 저장
        # 리스트 컴프리헨션 내 대입문 및 공백 가이드 준수
        error_logs = [line for line in lines if 'ERROR' in line or 'CRITICAL' in line]

        if error_logs:
            with open('error_report.log', 'w', encoding='utf-8') as error_file:
                error_file.writelines(error_logs)
            print('\n' + '=' * 40)
            print(f"분석 완료: {len(error_logs)}개의 치명적 오류를 'error_report.log'에 저장했습니다.")
        
    except IOError as e:
        print(f'파일 읽기 중 입출력 오류 발생: {e}')
    except Exception as e:
        print(f'알 수 없는 시스템 오류 발생: {e}')


if __name__ == '__main__':
    # 1. 설치 확인 출력
    check_system()
    
    # 2. 로그 분석 실행
    LOG_FILE = 'mission_computer_main.log'
    analyze_mission_log(LOG_FILE)