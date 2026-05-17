# Weekly Challenge 01 아이디어 구상
- AI 모델의 훈련 결과를 정리하는 `click` 패키지 및 CLI 기반 도구 만들기
- 훈련 과정에서의 모든 기록이 담긴 텍스트 파일들을 입력으로 받아 실험별 metric들을 표의 형태로 출력, 가장 좋은 결과의 실험을 찾아 성능과 경로를 출력하는 기능

예시
- `ckptpick summary exps/ --metric val_acc --mode max`
- `ckptpick best exps/ --metric val_loss --mode min`