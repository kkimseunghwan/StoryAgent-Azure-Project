import logging

def main(context: str) -> str:
    """
    이것이 액티비티 함수의 본체입니다.
    오케스트레이터로부터 받은 데이터를 처리하는 로직을 여기에 작성합니다.
    """
    logging.info(f"Activity가 다음 입력값으로 실행되었습니다: {context}")
    
    # TODO: 나중에 이 부분에 실제 파일 처리 코드를 추가할 것입니다.
    # (예: 음성 변환, 텍스트 추출 등)
    
    # 처리 결과를 문자열로 반환합니다.
    return f"Hello {context}!"