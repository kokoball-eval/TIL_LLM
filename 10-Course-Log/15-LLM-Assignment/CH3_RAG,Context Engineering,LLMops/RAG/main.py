"""KANT NEXT DevDesk RAG. 이 파일의 빈칸만 작성하세요."""
from qdrant_client import models

import support


def todo(message):
    raise NotImplementedError(message)


# 필수 1. 문서를 저장하고 현행 자료만 검색하기
def prepare_chunks(documents):
    chunks = []
    for document in documents:
        seen = set()
        number = 0
        for paragraph in document["paragraphs"]:
            text = " ".join(paragraph.split()) # TODO1 문단의 연속 공백을 한 칸으로 정리
            if not text or text == "KANT NEXT | 내부 문서" or text in seen:
                continue
            seen.add(text)
            # TODO2 문서 정보 5개와 chunk_id, text를 담은 사전을 만듬
            chunk = {"document_id" : document["document_id"],
                     "title" : document["title"],
                     "category" : document["category"],
                     "status" : document["status"],
                     "source" : document["source"],
                     "text" : text,
                     "chunk_id" : f"{document["document_id"]}:{number}"
            }
            chunks.append(chunk)
            number += 1
    # 이유: 문단을 유지하는 이유와 보존해야 할 메타데이터를 한두 줄로 적으세요.
    # 문단을 유지하는 이유 : 너무 길거나 짧지 않은 양으로 청킹되어야 추후 근거와 출처를 찾을 때 좀 더 정확한 검색을 기대할 수 있기 때문입니다.
    # 보존해야 할 메타데이터 : status, category는 검색 필터, chunk_id는 출처, document_id는 필요한 문서인지 확인을 위해 보존되어야 합니다.
    return chunks


def build_index(chunks, embedder):
    texts = ["passage: " + row["title"] + "\n" + row["text"] for row in chunks]
    vectors = embedder.encode(texts, normalize_embeddings=True)
    # TODO2 texts를 정규화된 문서 벡터로 바꾸세요.
    client = support.empty_store(len(vectors[0]))
    points = []
    for i, (row, vector) in enumerate(zip(chunks, vectors, strict=True)):
        point = models.PointStruct(id=i, vector=list(vector), payload=row)
        # TODO3 i, vector, row를 Qdrant PointStruct에 연결하세요.
        points.append(point)
    client.upsert(collection_name="devdesk", points=points, wait=True)
    return client


def search(client, embedder, question, category, top_k=2):
    if type(top_k) is not int or not 1 <= top_k <= 5:
        raise ValueError("top_k는 1~5의 정수여야 합니다.")
    vector = embedder.encode(["query: " + question], normalize_embeddings=True)[0]
    condition_a = models.FieldCondition(key="status", match=models.MatchValue(value="current"))
    condition_b = models.FieldCondition(key="category", match=models.MatchValue(value=category))
    scope = models.Filter(must=[condition_a, condition_b])
    # TODO3 현행 문서이면서 지정한 category인 Qdrant 필터를 만드세요.
    hits = client.query_points(collection_name="devdesk", query=list(vector),
                               query_filter=scope, limit=top_k, with_payload=True).points
    return [{**hit.payload, "score": hit.score} for hit in hits]


# 필수 2. 별칭 검색을 개선하고 답변을 비교하기
def rewrite_query(question, aliases):
    rewritten = question
    for alias, formal_name in aliases.items():
        rewritten = rewritten.replace(alias, formal_name)
        # TODO4 현재 문자열에서 alias를 formal_name으로 바꾸세요.
    return rewritten


def answer_question(question, rows, generate):
    if not rows:
        return {"answer": "확인할 문서가 없습니다.", "citations": [], "needs_human": True}
    context = "\n\n".join([f"[{row["chunk_id"]}] {row["text"]}" for row in rows])
    # TODO5 각 검색 결과를 [chunk_id] 본문으로 묶고 빈 줄로 연결하세요.
    reply = support.validate_shape(generate(question, context))
    allowed = {row["chunk_id"] for row in rows}
    # TODO6 검색 결과에 없는 출처가 하나라도 있는지 검사하세요.
    if any(citation not in allowed for citation in reply["citations"]):
        raise ValueError("검색하지 않은 출처가 있습니다.")
    if reply["needs_human"] == bool(reply["citations"]):
        raise ValueError("답변에는 출처가 필요하며 담당자 확인에는 출처를 비웁니다.")
    return reply


def make_golden():
    # 답이 있는 사례와 자료가 없는 사례를 하나씩 작성하세요.
    return [{"question_id": "given-firewall", "question": "초록문 사용 승인은 누구에게 요청하나요?", "category": "access",
 "reference_answer": "VPN 원격 접속은 보안팀에 승인을 요청합니다.", "relevant_document_ids": ["vpn"], "required_terms": ["보안팀"]},
    {"question_id": "given-unknown", "question": "회사 주변 맛집은 어딘가요?", "category": "overseas",
 "reference_answer": "관련 자료가 없어 답변이 제한됩니다.", "relevant_document_ids": [], "required_terms": []}]

def measure(case, rows, reply):
    expected = set(case["relevant_document_ids"])
    found = {row["document_id"] for row in rows}
    recall = len(expected & found) / len(expected) if expected else None
    # TODO7 필요한 문서 중 찾은 비율을 계산하세요. 필요한 문서가 없으면 None입니다.
    answer_ok = (all(term in reply["answer"] for term in case["required_terms"])
                 and not reply["needs_human"]) if expected else reply["needs_human"]
    failure = "없음"
    if expected and recall < 1:
        failure = "검색 누락"
    elif not answer_ok:
        failure = "답변 확인 필요" if expected else "보류 실패"
    # 관측: 실제 evaluate 결과에서 개선, 악화 질문과 답변 본문을 확인해 기록합니다.
    # given-firewall 사례에서 검색 누락이 개선되었습니다. 문서 검색 비율(0.67->1.0)과 답변 확인율(0.75->1.0)이 상승했고, 악화된 사례는 없으며 given-unknown은 대상 문서가 없어 정상적으로 보류되었습니다.
    # 검색 누락률의 감소를 위해 변환을 적용할 수 있겠다 생각할 수 있지만, 실험 사례가 적고 특정 조건(top-k=1)이 걸려있어 일반화하기 어렵고, 변환 후 질문의 문법이 어색해지는 한계가 확인됐으며, answer_check가 사실성까지는 판정하지 못하는 보조 지표라는 점도 함께 봐야 합니다.
    return {"document_recall": recall, "answer_check": bool(answer_ok), "failure": failure}


# 선택 심화 1. 두 검색 순위를 합쳐 근거를 모으기
def fuse_rankings(rankings, top_k=2):
    # 선택 심화: 문제의 RRF 규칙에 맞춰 직접 작성하세요.
    return todo("검색 순위 목록을 RRF 점수로 합치세요.")


if __name__ == "__main__":
    support.cli(globals())
