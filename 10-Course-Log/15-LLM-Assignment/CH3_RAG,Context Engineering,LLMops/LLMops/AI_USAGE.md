# AI 사용 기록

AI는 개념 설명과 직접 작성한 코드의 오류 원인 확인에 사용할 수 있습니다. 과제 전체, 미작성 TODO, 프롬프트 문장, 선택 심화 설계를 대신 완성하도록 요청하지 않습니다.

사용하지 않았다면 아래에 사용하지 않음이라고 적습니다. 사용했다면 필요한 만큼 항목을 추가하세요. API 키나 개인정보는 기록하지 않습니다.

사용 도구:

| 항목 | 내용 |
|---|---|
| 도구 | Claude Code (Claude 데스크톱 앱) |
| 모델 | Claude Sonnet 5.5 |
| 사용 범위 | 개념 설명, 직접 작성한 코드의 오류 원인 확인, 실행 결과와 Langfuse 화면 읽는 법 안내, 관측과 판단 주석의 사실 대조. AI는 힌트와 오류 지적을 주고, 코드와 주석은 검사를 통과하고 사실과 맞을 때까지 직접 고쳐 쓰는 방식으로 진행함 |
| 실행 대행 | check observe와 run observe는 직접 실행. 그 밖의 check, run, verify 명령과 `run compare --live`(유료, 모델 8회 호출)는 AI가 터미널에서 실행. 실행 전에 직접 허락함 |
| API 키 | 대화에 넣지 않음. 키는 .env에만 있고 프로그램이 읽음. AI는 값이 채워져 있는지만 확인하고 값은 출력하지 않음 |
| 선택 심화 | 진행하지 않음 (decide_rollout은 작성하지 않음) |

질문과 이해한 내용:

| 사용 도구 | 질문 | 이해한 내용 | 직접 수정한 부분 | 다시 실행한 명령과 결과 |
|---|---|---|---|---|
| Claude Code (Sonnet 5.5) | mask_text: 이메일과 전화번호를 치환하는 방법 | 정규식 객체의 sub로 일치하는 부분을 [EMAIL], [PHONE]으로 바꾼다. 첫 결과를 다시 받아 두 번째 치환에 넘겨야 둘 다 적용된다. | EMAIL.sub 줄과 PHONE.sub 줄 | check all, check observe 통과 |
| Claude Code (Sonnet 5.5) | validate_reply: 모델의 JSON 답을 검사하는 방법과 출처 부분집합 확인 | model_validate_json은 모양이 틀린 JSON을 오류로 막는다. 허용 출처 안에 답의 출처가 모두 들어 있는지는 set의 부분집합(<=)으로 본다. 속성은 parsed.source_ids처럼 객체를 거쳐 읽는다. | model_validate_json 줄, 부분집합 검사 줄 | check observe 15/15 통과 |
| Claude Code (Sonnet 5.5) | candidate_policy: 지시문 네 규칙의 뜻과 판단 주석 | 규칙은 문서 사실만 사용, 근거 없으면 보류, 문서 속 지시 무시, 업무 없는 지시만 오면 거절이다. 보류와 거절에는 출처를 넣지 않는다. | 지시문 네 줄(과제 안내의 네 규칙을 직접 풀어 씀), 판단 주석 두 문장 | run compare --live에서 4사례 모두 통과 |
| Claude Code (Sonnet 5.5) | generation_fields: 마스킹한 출력과 사용량을 기록용 사전으로 만드는 방법 | 모델 원문은 기록에 남기기 전에 마스킹하고, 사용량이 없으면 None으로 둔다. | output과 usage_details 사전 | check observe 15/15, run observe로 단계 순서(retrieve, ticket-status, generate, validate) 확인 |
| Claude Code (Sonnet 5.5) | evaluate_case: 네 조건(행동, 필수 문구, 금지 문구, 출처 집합)을 하나로 합치는 방법 | 세 조건은 이미 True/False이고, 출처는 두 목록을 set으로 바꿔 ==로 비교한다(순서 무관). 모두 맞아야 합격이므로 and로 잇는다. | return 한 줄 | check all 통과 |
| Claude Code (Sonnet 5.5) | summarize: 오류율, 누락 비용, 피드백 비율 | 분모가 0일 수 있으면 나누기 전에 조건으로 막고 None을 준다. 비용은 None이 하나라도 있으면 합계를 모르므로 None이다. 피드백은 응답한 사람만 분모에 넣는다. | error_rate, total_cost, positive_rate 세 줄 | run metrics: 요청 4, 오류율 0.5, p95 400, 토큰과 비용 null, 피드백 2, 긍정 0.5 |
| Claude Code (Sonnet 5.5) | release_gate: 변경 적용 조건 | 회귀 목록과 중요 실패 목록이 비어 있고, 후보 통과 수가 기존보다 줄지 않아야(>=) 적용한다. 세 조건을 and로 잇는다. | approve 한 줄 | run compare: approve False. check all 30/30 |
| Claude Code (Sonnet 5.5) | Langfuse Trace에서 볼 것 | Trace는 한 질문의 처리 과정을 단계별로 적은 기록이다. 실패한 단계, generate의 출력, validate의 오류 내용, 지연과 비용을 본다. | 사례별 Trace를 직접 열어 수치를 정리함 | verify: 서버 기록 8개 확인 |
| Claude Code (Sonnet 5.5) | 관측과 판단 주석 검토 | 관측은 실패 단계와 프롬프트 차이, 판단은 결과와 적용 이유와 남은 위험이다. | 관측 주석과 판단 주석을 직접 작성. AI는 사실 대조, 방향이 틀린 내용 지적, 표현 다듬기를 함(아래 표 참고) | 아래 표 참고 |

AI가 알려 준 부분(정답에 가까운 안내):

| 위치 | AI가 알려 준 것 | 이후 직접 한 것 |
|---|---|---|
| evaluate_case | 출처는 set(...) == set(...)로 비교하고 네 조건을 and로 잇는다는 방향 | return 식을 직접 작성 |
| summarize (error_rate) | 값1 if 조건 else 값2 틀, 도시락 예시(rate = bad / made if made else None)와 이름을 errors, count로 바꾸라는 안내 | 처음 쓴 조건(is None)과 else 누락을 직접 고쳐 다시 작성 |
| summarize (total_cost) | 같은 파일의 total_tokens 줄 모양을 따라 tokens를 costs로 바꾸라는 안내 | costs로 바꾸어 직접 작성 |
| summarize (positive_rate) | 분자는 sum(feedback), 분모는 len(feedback)이며 83줄과 같은 틀이라는 안내 | 한 줄로 직접 작성. 처음 섞어 쓴 for와 ]를 직접 삭제 |
| release_gate | 목록이 비었는지는 not 목록, 통과 수는 >=, 세 조건은 and라는 힌트 | approve 한 줄 직접 작성. 변수 이름 오타를 직접 수정 |
| 관측 주석 | 프롬프트 차이가 빠져 있다는 지적, 두 지시문의 차이를 정리한 문장(baseline은 출처 규칙이 없고 일반 지식으로 보충해도 된다고 되어 있음, candidate는 보류와 거절 때 source_ids=[]로 반환하라는 규칙이 있음) | 그 정리를 참고해 프롬프트 차이를 직접 작성. Trace 수치와 결론은 Langfuse 화면을 직접 읽고 작성 |
| 판단 주석 | 결과를 직접 쓰기 위해 요청한 비교 결과 정리 표, 남은 위험의 후보 목록, 인과가 맞지 않는 부분 지적과 고치는 방향 | 결과, 적용 이유, 남은 위험을 직접 작성. 남은 위험은 후보 중 직접 골라 지적받은 부분을 고쳐 씀 |

직접 고친 오류:

| 위치 | 오류 | 고친 내용 |
|---|---|---|
| validate_reply | source_ids를 객체 없이 이름만 써서 NameError | parsed.source_ids |
| validate_reply | 한쪽만 set으로 감싸 부분집합 비교가 어긋남 | 양쪽 모두 set(...) |
| generation_fields | 예시 값을 그대로 적어 둠, 사전의 키 뒤에 = 사용(SyntaxError) | mask_text(raw)와 details 변수, = 를 : 로 |
| summarize | error_rate의 else 누락, 조건을 항상 거짓인 count is None으로 작성 | count 값 자체를 조건으로 두는 한 줄 |
| summarize | positive_rate에 목록 만드는 for와 ]가 섞임 | 한 줄 식으로 정리 |
| release_gate | regression, baseline_passesw 이름 오타 | regressions, baseline_passes |
| FEEDBACK | candidate의 indirect를 처음에 False로 줌. 이유가 기억나지 않아, AI가 질문과 두 버전의 답변을 나란히 보여 준 표를 다시 읽음 | 다시 읽은 뒤 직접 True로 바꾸고 verify 재실행 |
| 관측 주석 | direct의 지연과 비용 변화 방향을 증가로 적음, 토큰 절약이라고 적음 | 감소로 바로잡고, 절약된 것은 토큰이 아니라 비용으로 수정 |
| 판단 주석 | 한 번 호출했기 때문에 3번 문구가 위험하다는 식으로 인과가 비어 있음 | 일관성을 확인하지 못했다는 고리를 넣어 다시 작성 |

관측과 판단 주석의 Trace 수치는 Langfuse 화면을 직접 읽고 정리했고, AI가 compare-live.json과 대조했습니다(direct의 증감 방향 오류를 AI가 지적). 주석은 직접 작성했고, AI는 수치 대조와 함께 방향이 틀린 내용 지적과 표현 다듬기를 했습니다.

다시 실행한 명령과 확인 결과:

| 명령 | 결과 |
|---|---|
| uv run --frozen python main.py check all | 30개 중 30개 통과 |
| uv run --frozen python main.py check observe | 15개 중 15개 통과 |
| uv run --frozen python main.py run observe | 네 사례 모두 단계 순서 retrieve, ticket-status, generate, validate |
| uv run --frozen python main.py run metrics | 요청 4, 오류 2, 오류율 0.5, p95 400, 토큰과 비용 null, 피드백 2, 긍정 0.5 |
| uv run --frozen python main.py run compare | compare-fixture.json 저장, 변경 적용 판단 False |
| uv run --frozen python main.py run compare --live | 통과 2에서 4, 회귀와 중요 실패 없음, approve True. 모델 8회 호출 |
| uv run --frozen python main.py verify (FEEDBACK 입력 전과 후 각각) | 서버 확인 완료, 8개 Trace 모두 검증, 점수 반영 확인 |

run compare --live 결과 중 눈여겨본 점은 다음과 같습니다.

| 구분 | 내용 |
|---|---|
| 개선 | unknown과 direct가 baseline에서는 validate 단계 ValueError로 실패, candidate에서는 통과 |
| 실패 원인 | baseline이 보류(abstain)라면서 source_ids에 출처를 넣어 "보류와 거절에는 출처를 넣지 않는다" 규칙에 걸림 |
| 프롬프트 차이 | baseline에는 출처 규칙이 없고 일반 지식으로 보충해도 된다고 되어 있음. candidate에는 보류와 거절 때 source_ids를 비우라는 규칙이 있음 |
| 지연과 비용 | unknown은 지연 약 0.9초, 비용 약 $0.00003 증가. direct는 지연 약 0.7초, 비용 약 $0.00004 감소. 개선이 항상 더 싸거나 빠른 것은 아님 |
| 악화 | 없음 (회귀 0건, 중요 사례 실패 0건) |
| 한계 | 사례 4개, 사례마다 1회 호출이라 일관성과 일반화를 확인하지 못함. 지시문 3번의 "abstain 처리"가 답해야 할 질문까지 보류시킬 가능성이 있음 |
