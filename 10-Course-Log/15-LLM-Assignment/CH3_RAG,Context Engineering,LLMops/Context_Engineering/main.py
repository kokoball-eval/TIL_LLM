"""main.py의 todo(...) 부분을 작성하세요. support.py와 checks.py는 그대로 사용합니다."""
import copy
import hashlib
import json
import sys

import support


def todo(message):
    raise NotImplementedError(message)


# 필수 1. 필요한 자료와 사용자 기억 관리하기
def select_context(items, user_id, now):
    kept = []
    for item in items:
        allowed = (
            (item["user_id"] == "public" or item["user_id"] == user_id)
            and item["trusted"] and item["active"] 
            and (item["expires_at"] is None or item["expires_at"] > now)
        )
        # TODO1 접근 범위, 신뢰, 현행 여부와 만료 조건
        if allowed:
            kept.append(copy.deepcopy(item))
    # 이유: 높은 우선순위의 자료를 먼저 고르면 어떤 문제가 생기는지 적으세요.
    # 정상 자료보다 높은 우선순위를 가진 접근하면 안 되는 자료나 이미 만료된 정보를 가져올 수 있기 때문입니다.
    return sorted(kept, key=lambda item: (-item["priority"], item["id"]))


def memory_action(records, user_id, action, name, value=None):
    support.validate_memory_input(user_id, action, name, value)
    key = f"{user_id}:{name}"
    if action == "read":
        return copy.deepcopy(records.get(key))
        # TODO2 현재 사용자의 기억 조회
    if action == "create":
        if key in records:
            raise ValueError("이미 있는 기억입니다. update를 사용하세요.")
        records[key] = copy.deepcopy(value)
        # TODO3 새 기억 저장
    elif action == "update":
        if key not in records:
            raise KeyError("수정할 기억이 없습니다.")
        records[key] = copy.deepcopy(value)
        # TODO4 기존 기억 수정
    elif action == "delete":
        return records.pop(key, None)
        # TODO5 현재 사용자의 기억 삭제
    return copy.deepcopy(records[key])


def build_messages(prefix, question, context, turns, summary):
    data = json.dumps({"reference_data": context, "summary": summary}, ensure_ascii=False)
    history = [message for turn in turns for message in turn["messages"]]
    # 이유: 장기 기억과 세션 상태의 차이, 자료와 지시를 나누는 이유를 적으세요.
    # 장기 기억은 사용자 별로 오래 남는 records이고, 세션 상태는 대화가 끝나면 사라지는 turns입니다.
    # 자료 안에 "이전 지시를 무시해라" 같은 문장이 섞여 있더라도 고정된 지시를 분리함으로써 자료 속 문장이 지시를 덮어쓰지 못하게 하는 것으로 답변의 품질 신뢰성을 지키기 위해서입니다. 
    return [
        {"role": "developer", "content": prefix}, 
        {"role": "user", "content": data}, *history, 
        {"role": "user", "content": question}
    ]
    # TODO6 고정 지시, 참고 자료, 대화, 현재 질문 순서의 메시지"


# 필수 2. 긴 대화를 줄이고 반복 입력 재사용하기
def summarize(turns):
    summary = {}
    for turn in turns:
        for name, value in support.fact_lines(turn["messages"][0]["content"]):
            summary[name] = {"value": value, "source_turn_id": turn["id"]}
    return summary


def select_window(turns, limit, reserve, margin, make_messages, count):
    support.validate_budget(limit, reserve, margin)
    budget = limit - reserve - margin
    #TODO7 입력에 쓸 수 있는 예산
    if budget <= 0 or count(make_messages([])) > budget:
        raise ValueError("고정 입력만으로 예산을 넘었습니다.")
    kept = []
    for turn in reversed(turns):
        candidate = [turn, *kept]
        if count(make_messages(candidate)) > budget:
        #TODO8 전체 후보 입력이 예산을 넘는지
            break
        kept = candidate
    # 관측: 압축 비교 후 토큰 수, 빠진 사실, 선택한 한도를 기록합니다.
    # 전체 대화는 약 1999개, 최근 대화는 약 1744개, 요약+최근 대화는 약 1744개의 토큰을 사용했다.
    # 전체 대화는 기준치인 1788개보다 토큰 사용량이 초과되었고, 최근 대화는 "담당자·마감일·승인조건" 3개를 모두 틀리는 것으로 확인되어 요약+최근 방법이 채택되었다.
    return kept


def cache_key(prefix, user_id):
    return hashlib.sha256(f"{user_id}\n{prefix}".encode("utf-8")).hexdigest()
    # TODO9 사용자와 고정 지시로 만드는 캐시 키
    # 관측: 실제 캐시 읽기/쓰기와 비용을 확인하고 미관측이면 그대로 적습니다.
    # 캐시 쓰기(첫 사용)와 읽기(재사용) 모두 1228개로 측정되었습니다.
    # 비사용 0.0003066, 첫 사용 0.000368, 재사용 0.00008556입니다.
    # 첫 사용에서는 캐시를 쓰는 값 때문에 비용이 오히려 늘었고, 재사용에서는 줄었습니다.
    # tainted-document와 unverified-tool이 최종 입력에 없었습니다.

# 선택 심화 1. 새 대화만 반영하고 변경 이력 남기기
def merge_summary(previous, turns):
    return todo("선택 심화: 새 턴의 요약과 변경 이력")


if __name__ == "__main__":
    raise SystemExit(support.cli(sys.modules[__name__]))
