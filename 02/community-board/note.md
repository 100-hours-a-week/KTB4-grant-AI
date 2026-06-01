# Weekly Challenge 과제 정리
## 디자인 패턴
1. Client: HTTP 요청
2. Router: URL 경로 분기 및 controller의 함수로 연결
3. Controller: 요청 검증 및 파라미터 추출, 필요한 값을 Service로 전달
4. Model(Service): 비즈니스 규칙에 따라 실제 로직 처리
5. Model(Repository): DB 접근 및 통신, 저장
6. DB