# LLM Evaluation

LLM 애플리케이션의 품질을 어떻게 측정하고 검증하는지 정리합니다.

## 채워갈 주제

- 정확 일치(exact match)가 LLM 평가에 맞지 않는 이유
- 평가 지표: 정답률, 형식 준수율, 파싱 실패율
- 결정적 부분(Prompt · Parser)과 비결정적 부분(Model) 분리하기
- 형식 검증 · 스키마 검증 · 내용 검증의 계층
- 평가 셋 고정과 회귀 테스트
- 토큰 사용량 · 지연 시간 측정

## 관련 학습 로그

- [07-Practical-DL-Prompt-Engineering](../10-Course-Log/07-Practical-DL-Prompt-Engineering/) — 구조화 출력, 평가 루브릭
- [10-LangChain](../10-Course-Log/10-LangChain/) — Output Parser와 검증 계층
- [game-bug-triage-llm-eval](../40-Projects/game-bug-triage-llm-eval/) — 로컬 LLM 비교 평가 프로젝트

## 규칙

직접 설명할 수 있는 내용만 옮깁니다.
