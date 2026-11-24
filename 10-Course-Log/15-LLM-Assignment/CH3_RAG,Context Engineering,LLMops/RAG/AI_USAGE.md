# AI 사용 기록

AI는 개념 질문과 직접 작성한 코드의 오류 원인을 확인할 때 사용할 수 있습니다. 미작성 빈칸, 과제 전체, 평가 사례나 선택 심화의 설계를 대신 완성해 달라고 요청하지 않습니다. 실제 실행 결과를 만들거나 고쳐 달라고 요청하지 않습니다.

사용하지 않았다면 아래에 사용하지 않음이라고 적으세요. 사용했다면 필요한 만큼 기록하세요. API 키나 원문 개인정보를 대화에 넣지 않습니다.

사용 도구:

| 항목 | 내용 |
|---|---|
| 도구 | Claude Code (Claude 데스크톱 앱) |
| 모델 | Claude Sonnet 5.5 |
| 사용 범위 | 개념 설명, 직접 작성한 코드의 오류 원인 확인, 실행 결과 읽기, 관측 주석의 사실 대조 |
| 환경 준비 | uv sync와 demo 실행을 AI가 명령으로 실행해 확인 |
| API 키 | 대화에 넣지 않음. 키는 .env에만 있고 AI는 비어 있는 .env.example만 읽음 |

질문과 관련 함수:

| 관련 함수 | 물어본 것 | AI가 한 일 |
|---|---|---|
| prepare_chunks | 문단 정리(split과 join), 메타데이터 사전과 chunk_id의 f-string, 문단을 유지하는 이유 | 개념과 비유, 터미널 실험 안내, 오류 원인 설명 |
| build_index | 임베딩과 정규화, E5의 passage/query 접두어, PointStruct의 id/vector/payload, list 변환 | 개념과 비유, 오류 메시지 해석 |
| search | 현행 문서와 category로 거르는 Qdrant 필터 구조 | FieldCondition, MatchValue, Filter(must)의 역할 설명, 대소문자 오류 지적 |
| rewrite_query | 반복문 안에서 별칭을 정식 명칭으로 바꾸는 방법 | replace 사용법을 다른 예시로 안내, 따옴표 오류 지적 |
| answer_question | 검색 결과를 [chunk_id] 본문으로 묶어 잇는 방법, 검색하지 않은 출처 검사 | 단계 분해, any와 all 설명, 연습용 rows를 덮어쓴 문제 지적 |
| measure | 문서 Recall 계산, 필요한 문서가 없을 때 None | 집합과 개수 개념, None 오류 지적 |
| make_golden | 평가 사례 6칸의 의미, 원문 ID와 청크 ID의 차이, 반환 형식 | 형식과 규칙 설명, 제공 사례와 원문 보여 줌, return 구조 오류 해석 |
| 실행 결과 | run index, run answer, run evaluate 결과 읽기, 관측 주석 검토 | 결과 해석, 주석의 숫자와 사례를 결과와 대조 |

이해한 내용:

| 주제 | 이해한 내용 |
|---|---|
| 청킹과 메타데이터 | 문단 단위로 쪼개면 근거를 찾을 때 너무 길거나 짧지 않다. status와 category는 검색 필터, chunk_id는 출처, document_id는 필요한 문서 확인에 쓰이므로 보존한다. |
| 임베딩과 정규화 | 문장을 숫자 묶음(벡터)으로 바꾸어 뜻이 비슷한 문장을 가깝게 둔다. 정규화는 길이를 1로 맞추어 방향(뜻)만 비교하게 한다. 문서에는 passage:, 질문에는 query: 를 붙인다. |
| 벡터 저장과 필터 | PointStruct는 번호(id), 위치(vector), 설명 정보(payload) 세 칸이며 vector는 list로 넣는다. 검색 전에 status가 current이고 category가 같은 조건을 Filter의 must로 묶어 후보를 먼저 거른다. |
| 별칭 변환 | 반복문이 갱신하는 rewritten에 replace(alias, formal_name)를 거듭 적용한다. 답변 생성에는 원질문을 유지한다. |
| 출처 검사 | 답변의 citations 중 검색 결과(allowed)에 없는 번호가 하나라도 있으면 any 조건으로 막는다. |
| 파이썬 규칙 | 따옴표가 있으면 글자 자체, 없으면 변수 이름이다. 이름의 대소문자, 괄호 짝, return은 함수를 끝낸다는 점, 목록은 대괄호로 묶는다는 점을 오류 메시지로 확인했다. |
| 문서 Recall | 필요한 문서 중 찾은 비율(교집합 개수 나누기 필요한 문서 수)이고 필요한 문서가 없으면 None이다. relevant_document_ids는 원문 ID, citations는 청크 ID로 다르다. |
| 결과 해석의 한계 | answer_check는 핵심 문구와 보류 여부만 보는 보조 지표이므로 사실성은 답변 본문과 reference_answer를 직접 비교한다. 사례 4개와 top_k=1이라 결과를 일반화하기 어렵다. |

직접 수정한 부분:

AI는 정답 코드를 대신 쓰지 않았습니다. 다른 예시로 모양을 보여 준 곳(사과를 딸기로 바꾸기, 색과 크기 조건 등)은 있으며 실제 값과 이름은 직접 채웠습니다.

| 함수 | 직접 작성한 것 | 직접 고친 오류 |
|---|---|---|
| prepare_chunks | 공백 정리, 사전 구성, chunk_id의 f-string, 이유 주석 | 사전의 = 를 : 로, f-string 따옴표 짝 |
| build_index | vectors 계산, PointStruct 연결 | 괄호 짝, 불필요한 [0:7] 삭제, 칸 이름 vector, list( )의 위치 |
| search | 조건 두 개와 Filter(must) | filter를 Filter로 |
| rewrite_query | replace 한 줄 | alias와 formal_name의 따옴표 제거 |
| answer_question | context(목록식과 빈 줄 join), 출처 검사(any) | 연습용 rows 삭제, join의 소괄호, for 뒤 이름 맞추기 |
| measure | recall 식, 관측 주석 | else를 None으로 |
| make_golden | 평가 사례 두 개(질문, 분류, 정답 문장, 원문 ID, 핵심 문구)를 원문을 읽고 직접 정함 | [vpn] 따옴표, return 하나로 합쳐 목록으로 묶기 |

관측 주석은 evaluation-live.json의 결과를 읽고 직접 작성했습니다. AI는 숫자와 사례가 결과와 맞는지만 대조했습니다.

다시 실행한 명령과 확인 결과:

| 명령 | 결과 |
|---|---|
| uv run --frozen python main.py check index | 3개 중 3개 통과 |
| uv run --frozen python main.py check answer | 2개 중 2개 통과 |
| uv run --frozen python main.py check evaluate | 3개 중 3개 통과 |
| uv run --frozen python main.py run index | artifacts/index.json 저장 |
| uv run --frozen python main.py run answer --live | 질문을 "VPN 원격 접속 ..."으로 변환해 vpn:0을 검색, 답변은 보안팀, 출처 vpn:0, needs_human false |
| uv run --frozen python main.py run evaluate --live | 변환 전 Recall 0.67과 답변 확인 0.75가 변환 후 1.0과 1.0으로 상승 |

run evaluate --live 결과 중 눈여겨본 점은 다음과 같습니다.

| 구분 | 내용 |
|---|---|
| 개선 | given-firewall 한 건. 변환 전에는 door 문서를 검색해 검색 누락, 변환 후에는 vpn 문서를 검색 |
| 악화 | 없음 |
| 보류 | given-unknown은 두 조건 모두 검색 결과 없이 담당자 확인으로 보류 |
| 한계 | 변환 후 질문이 "API 토큰를"처럼 조사가 어색해짐 |
