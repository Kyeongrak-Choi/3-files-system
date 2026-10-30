# Auto Healing MVP 데모 실행 절차

## 1. 정상 기준선

    py -m unittest discover -s tests -v

서버는 다음 명령으로 실행한다.

    py run_server.py

Swagger UI는 `http://127.0.0.1:18001/docs`, ReDoc은 `http://127.0.0.1:18001/redoc`에서 확인할 수 있다.

서버 실행 후 다음 요청을 보낸다.

    POST /coach
    {"item_name":"책","price":10000,"reason":"읽고 싶다"}

예상 결과: `status=ok`, 숙고 질문 3개 이상.

## 2. 장애 주입 순서

1. `POST /fault` with `{"fault":"http_429","count":3}`
2. `POST /coach`로 대체 응답 확인
3. `DELETE /fault`로 장애 해제
4. `POST /fault` with `{"fault":"timeout","count":3}`
5. 연결 실패·5xx도 같은 방식으로 반복
6. 모든 사건의 incident_id, attempt, state와 검증 결과를 기록

장애 주입 대상은 모의 LLM뿐이며 운영 대상은 허용되지 않는다.

## 3. 성공 증거

- 정상 요청: `status=ok`
- 허용 장애: `status=degraded` 또는 정책에 따른 에스컬레이션
- 응답 스키마 검증 PASS
- 최대 시도 3회
- 사건별 MTTD·MTTR 산출
- 민감정보 없는 구조화 로그
