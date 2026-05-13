DICTIONARY = [
    'the', 'is', 'are', 'was', 'and', 'for', 'not', 'with',
    'base', 'mars', 'alpha', 'code', 'security', 'access',
    'door', 'key', 'open', 'niner', 'seven', 'one',
]


def caesar_cipher_decode(target_text):
    """카이사르 암호를 모든 자리수(1~26)로 순서대로 해독하여 출력한다.

    사전(DICTIONARY)에 있는 단어가 발견되면 즉시 반복을 멈추고
    해당 자리수와 해독 결과를 반환한다.

    Returns:
        tuple: (shift, decoded_text) 또는 발견 못 하면 (None, None)
    """
    for shift in range(1, 27):
        decoded_chars = []
        for ch in target_text:
            if ch.isalpha():
                base = ord('A') if ch.isupper() else ord('a')
                decoded_chars.append(chr((ord(ch) - base - shift) % 26 + base))
            else:
                decoded_chars.append(ch)
        decoded = ''.join(decoded_chars)
        print(f'[shift {shift:>2}] {decoded}')

        words = decoded.lower().split()
        if any(word in DICTIONARY for word in words):
            print(f'\n사전 단어 발견 — shift {shift}에서 해독 완료')
            return shift, decoded

    return None, None


def save_result(shift, decoded_text):
    try:
        with open('result.txt', 'w', encoding='utf-8') as f:
            f.write(f'shift: {shift}\n')
            f.write(decoded_text)
        print(f'\n[result.txt 저장 완료] shift={shift}')
    except OSError as e:
        print(f'result.txt 저장 실패: {e}')


def main():
    try:
        with open('password.txt', 'r', encoding='utf-8') as f:
            password = f.read().strip()
    except FileNotFoundError:
        print('password.txt 파일을 찾을 수 없습니다.')
        return
    except OSError as e:
        print(f'password.txt 읽기 실패: {e}')
        return

    print(f'[암호문]\n{password}\n')
    print('=' * 50)

    shift, decoded = caesar_cipher_decode(password)

    if shift is None:
        print('\n자동 탐지 실패. 올바른 shift 번호를 직접 입력하세요 (1~26): ', end='')
        try:
            manual_shift = int(input())
            decoded_chars = []
            for ch in password:
                if ch.isalpha():
                    base = ord('A') if ch.isupper() else ord('a')
                    decoded_chars.append(
                        chr((ord(ch) - base - manual_shift) % 26 + base)
                    )
                else:
                    decoded_chars.append(ch)
            decoded = ''.join(decoded_chars)
            shift = manual_shift
            print(f'[결과] {decoded}')
        except ValueError:
            print('올바른 숫자를 입력하지 않아 종료합니다.')
            return

    save_result(shift, decoded)


if __name__ == '__main__':
    main()
