# AI 사용 기록

AI는 개념 질문과 직접 작성한 코드의 오류 원인 확인에 사용할 수 있습니다. 과제 전체, 미작성 빈칸, 선택 심화의 설계나 정답을 대신 작성하도록 요청하지 않습니다. 설명을 이해한 뒤 직접 수정하고 다시 검사하세요.

사용하지 않았다면 아래에 사용하지 않음이라고 적습니다. 사용했다면 필요한 만큼 행을 추가하세요. API 키와 개인 정보는 기록하지 않습니다.

사용 도구:

| 항목 | 내용 |
|---|---|
| 도구 | Claude Code (Claude 데스크톱 앱) |
| 모델 | Claude Sonnet 5.5 |
| 사용 범위 | 개념 설명, 직접 작성한 코드의 오류 원인 확인, 실행 결과 읽기, 관측 주석의 사실 대조 |
| API 키 | 대화에 넣지 않음. 키는 .env에만 있고 --live 실행 때 프로그램이 읽음 |
| 선택 심화 | 진행하지 않음 (merge_summary는 작성하지 않음) |

| 사용 도구 | 질문 | 이해한 내용 | 직접 수정한 부분 | 다시 실행한 명령과 결과 |
|---|---|---|---|---|
| Claude Code (Sonnet 5.5) | select_context: 접근, 신뢰, 활성, 만료 조건을 하나로 묶는 방법과 우선순위보다 먼저 거르는 이유 | 거를 자료를 먼저 정하고 그다음에 순서를 정한다. 우선순위가 높아도 접근하면 안 되거나 만료된 자료면 입력에 들어가면 안 된다. and가 or보다 먼저 계산되므로 or 조건은 괄호로 묶는다. | allowed 조건식과 deepcopy로 원본을 보존하는 append, 이유 주석 | check all: 자료 선택, 만료와 사용자 경계, 동점 순서 통과 |
| Claude Code (Sonnet 5.5) | memory_action: read, create, update, delete 네 동작과 사본 보존 | 저장소 안의 값을 직접 내주면 바깥에서 바꿀 수 있어 deepcopy로 복사한다. read는 없으면 None, create는 이미 있으면 오류, update는 없으면 오류, delete는 없어도 오류 없이 지운다. | 네 동작의 한 줄씩 (records.get(key), records[key] = copy.deepcopy(value), records.pop(key, None)) | check all: 저장소 재조회와 CRUD, 사용자별 분리, 사본 보존, 잘못된 작업 통과 |
| Claude Code (Sonnet 5.5) | build_messages: 고정 지시, 참고 자료, 대화, 현재 질문의 순서와 장기 기억과 세션 상태의 차이 | 메시지는 role과 content를 가진 사전의 목록이다. 지시는 developer, 자료와 질문은 user로 나누어 자료 안의 문장이 지시를 덮어쓰지 못하게 한다. 장기 기억은 사용자별로 남는 records, 세션 상태는 대화가 끝나면 사라지는 turns이다. | 반환 목록, 이유 주석 | check all: 지시와 참고 자료 분리, 자료의 자기 신뢰 주장 통과 |
| Claude Code (Sonnet 5.5) | summarize: 항목별 최신 값과 출처 턴 | 같은 항목이 다시 나오면 같은 칸에 덮어써서 최신 값이 남고, 다시 안 나온 항목은 그대로 남는다. 한 칸에는 값과 출처 턴 ID를 함께 담는다. | summary[name]에 value와 source_turn_id를 담는 사전 | check all: 최신 값과 근거 요약, 사용자 발화만 요약 통과 |
| Claude Code (Sonnet 5.5) | select_window: 입력 예산과 중단 조건 | 입력 예산은 한도에서 출력 자리(reserve)와 안전 여유(margin)를 뺀 값이다. 최근 턴부터 넣다가 예산과 같으면 포함, 넘으면 멈춘다. | budget 식, 중단 조건 if, 관측 주석 | check all: 전체 예산과 연속된 최근 턴, 압축 전후 정보 보존 통과 |
| Claude Code (Sonnet 5.5) | cache_key: 캐시 키에 넣을 것과 해시 | 키는 사용자 ID와 고정 지시로 만들고 질문은 넣지 않는다(매번 달라지면 재사용할 수 없다). 해시는 같은 재료면 항상 같은 값, 재료가 달라지면 다른 값을 준다. 이어 붙일 때 줄바꿈이 없으면 서로 다른 조합이 같은 글이 될 수 있다. | 사용자 ID, 줄바꿈, 고정 지시를 합친 글과 sha256 해시, 관측 주석 | check all: 사용자별 안정된 캐시 키, 관측값과 비용 기록 통과 |
| Claude Code (Sonnet 5.5) | 실행 결과 읽기와 관측 주석 검토 | 추정 토큰과 실제 input_tokens는 다르다. 캐시 쓰기는 비용이 들어 첫 사용이 더 비쌀 수 있고, 재사용에서 읽기가 관측되었다. 최종 입력에 제외한 오염 자료가 없는지도 확인한다. | 관측 주석 두 개를 결과를 읽고 직접 작성 | 아래 표 참고 |

AI가 알려 준 부분(정답에 가까운 안내):

| 위치 | AI가 알려 준 것 | 이후 직접 한 것 |
|---|---|---|
| build_messages | 세 번째 항목은 사전이 아니라 *history를 목록 안에 그대로 두는 형태라는 점 | 틀린 모양(사전 안의 "*history")을 직접 고쳐 적용 |
| summarize | 값 자리에 value, 출처 자리에 turn[...] 꼴을 쓴다는 방향. 턴의 칸 이름이 id라는 점은 AI가 데이터 파일을 열어 확인해 알려 줌 | 두 자리의 변수 선택과 코드 작성 |
| select_window | 예산과 같을 때는 포함해야 하므로 > 기호를 써야 한다는 점 | 조건식 작성, 처음 쓴 >= 는 직접 > 로 수정 |
| cache_key | 해시 호출의 바깥 틀(sha256(글.encode("utf-8")).hexdigest())과 줄바꿈이 필요한 이유 | f-string과 괄호 구성, 처음 쓴 불필요한 [ 는 직접 삭제 |

직접 고친 오류:

| 함수 | 오류 | 고친 내용 |
|---|---|---|
| select_context | 조건을 { } 로 묶어 집합이 됨, public에 따옴표 없음, or에 괄호 없음, 날짜를 글자로 적음, 여러 줄 식이 끊김 | 따옴표와 괄호, now 변수, 전체를 괄호로 묶음 |
| memory_action | records.get(value)처럼 사전을 키로 사용, deepcopy에 인자 두 개, = 대신 ==, 닫는 괄호 초과, delete의 pop 인자 오류 | records.get(key), 인자 하나의 deepcopy, 대입 =, records.pop(key, None) |
| build_messages | 반환 목록의 바깥 모양이 맞지 않음, *history를 role 값 글자로 넣음 | 바깥을 [ ] 목록으로 바꾸고 *history를 항목으로 둠 |
| summarize | value 자리에 name, 출처에 턴 전체, 없는 칸 이름(turn_id, load_data) | value, turn["id"] |
| select_window | 비교를 >= 로 적음 | > 로 수정 |
| cache_key | 줄바꿈 누락, sha256( 뒤의 불필요한 [ | \n 추가, [ 삭제 |

관측 주석은 compare-live.json과 cache-live.json의 결과를 읽고 직접 작성했습니다. AI는 숫자와 사례가 결과와 맞는지만 대조했습니다.

다시 실행한 명령과 확인 결과:

| 명령 | 결과 |
|---|---|
| uv run --frozen python main.py check all | 16개 중 16개 통과 |
| uv run --frozen python main.py run compare, check compare | compare-fixture.json 저장, 4개 중 4개 통과 |
| uv run --frozen python main.py run compare --live | 추정 입력 전체 1999(한도 5000, 예산 4488), 최근 1744, 요약+최근 1744(두 조건 모두 한도 2300, 예산 1788). 답변 일치는 3, 0, 3 |
| uv run --frozen python main.py run cache, check cache | cache-fixture.json 저장, 3개 중 3개 통과 |
| uv run --frozen python main.py run cache --live | 캐시 쓰기 1228, 읽기 1228. 비용은 비사용 0.0003066, 첫 사용 0.000368, 재사용 0.00008556 |

run compare --live와 run cache --live 결과 중 눈여겨본 점은 다음과 같습니다.

| 구분 | 내용 |
|---|---|
| 전체 대화 | 한도 5000(예산 4488)으로 실행해 3개 모두 일치. 다만 추정 1999는 다른 두 조건의 한도 2300 기준 예산 1788을 넘어, 그 한도에서는 전체 대화를 넣을 수 없음 |
| 최근 대화 | 담당자, 마감일, 승인조건 3개 모두 틀림(0/3) |
| 요약+최근 | 최근 대화와 같은 추정 토큰(1744)에서 3개 모두 일치 |
| 캐시 첫 사용 | 쓰기 비용 때문에 비사용보다 오히려 비쌈 |
| 캐시 재사용 | 읽기 1228이 관측되어 비용 감소 |
| 오염 자료 | tainted-document와 unverified-tool이 최종 입력에 없음 |
| 한계 | 호출 횟수가 적고 지연 시간은 한 번의 차이로 일반화할 수 없음 |
