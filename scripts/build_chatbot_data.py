#!/usr/bin/env python3
"""Build the shared FinLog chatbot dataset from the current main chatbot.

The main site and the standalone deployment both load this generated file so
the knowledge base cannot silently drift between two copies.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_HTML = ROOT / "chatbot.html"
STANDALONE = ROOT.parent / "금융챗봇" / "배포_finlog-chatbot"


def extract(source: str) -> tuple[list[dict], list[dict]]:
    match = re.search(
        r"const KB = (\[.*?\]);\s*const FAQS = (\[.*?\]);\s*const IMG",
        source,
        flags=re.DOTALL,
    )
    if not match:
        data_file = ROOT / "assets" / "chatbot-data.js"
        data_source = data_file.read_text(encoding="utf-8")
        match = re.search(
            r"const KB = (\[.*?\]);\s*const FAQS = (\[.*?\]);",
            data_source,
            flags=re.DOTALL,
        )
    if not match:
        raise RuntimeError("Could not locate the chatbot data blocks")
    return json.loads(match.group(1)), json.loads(match.group(2))


def replace_text(value):
    """Keep collaborative wording consistent across nested chatbot records."""
    if isinstance(value, dict):
        return {key: replace_text(item) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_text(item) for item in value]
    if not isinstance(value, str):
        return value
    replacements = (
        ("저는 이렇게 판단했다", "팀 토론에서는 그렇게 정리했다"),
        ("제 결론은", "팀 토론의 결론은"),
        ("제가 얻은 결론", "팀이 함께 정리한 결론"),
        ("제가 현장에서 얻은 결론", "팀이 현장에서 함께 정리한 결론"),
    )
    for old, new in replacements:
        value = value.replace(old, new)
    return value


def update_time_sensitive(entries: list[dict]) -> None:
    """Apply reviewed wording to claims that are easy to overstate or date."""
    by_id = {entry.get("id"): entry for entry in entries}

    if entry := by_id.get("kospi"):
        entry["example"] = (
            "2026년 6월 18일 코스피는 9,063.84로 마감해 사상 처음 종가 기준 9,000선을 넘었다. "
            "자료: 한국거래소(대한민국 공식 해외홍보 포털 재인용), 기준일 2026-06-18, 확인일 2026-07-15. "
            "지수는 계속 변하므로 최신 수치는 한국거래소에서 다시 확인해야 한다."
        )

    if entry := by_id.get("wgbi"):
        entry["short"] = "주요국 국채로 구성된 글로벌 채권지수로, 편입되면 지수 추종 수요가 늘어날 수 있다."
        entry["detail"] = (
            "FTSE Russell이 산출하는 대표적 국채지수다. 글로벌 연기금·펀드 중 이 지수를 추종하는 자금은 "
            "편입 비중을 참고해 국채 보유량을 조정하므로 채권 수요가 늘 수 있다. 실제 유입 규모와 시점은 "
            "환율·금리·운용전략에 따라 달라진다."
        )
        entry["example"] = (
            "한국 국채의 WGBI 편입은 2026년 4월 지수부터 시작해 11월까지 "
            "8개월에 걸쳐 단계적으로 진행된다. FTSE Russell은 완전 편입 시 "
            "한국 비중을 WGBI 기준 약 1.75%로 제시했다."
        )

    if entry := by_id.get("nxt-ats"):
        entry["example"] = (
            "넥스트레이드는 2025년 3월 영업을 시작해 국내 복수거래소 시대를 열었다. "
            "거래량 수치는 계속 변하므로 비중보다 최선집행과 통합 감시 구조를 중심으로 본다."
        )

    if entry := by_id.get("msci"):
        entry["example"] = (
            "MSCI는 2026년 시장분류 검토에서 한국 시장 접근성 개선 조치를 계속 모니터링한다고 밝혔다. "
            "향후 분류 변경 여부와 시점은 확정된 사실이 아니다."
        )

    if entry := by_id.get("base-rate"):
        entry["example"] = (
            "한국은행은 2026년 5월 28일 기준금리를 연 2.50%로 유지했다. "
            "금리 판단은 물가·성장·환율·금융안정을 함께 고려한 결과다."
        )

    if entry := by_id.get("inflation"):
        entry["example"] = (
            "국가데이터처가 발표한 2026년 5월 소비자물가는 전년 동월보다 3.1% 상승했다. "
            "금리 판단에는 이 수치 외에도 성장과 금융안정 여건이 함께 반영된다."
        )

    if entry := by_id.get("gdp"):
        entry["example"] = (
            "GDP는 소비·투자·정부지출과 순수출을 함께 반영한다. 수출이 크게 늘어도 내수나 투자가 약하면 "
            "GDP 성장과 체감경기가 다르게 움직일 수 있다."
        )

    if entry := by_id.get("exchange-rate"):
        entry["detail"] = (
            "보통 원/달러 환율을 말하며, 1달러를 받으려면 원화를 얼마 줘야 하는지를 나타낸다. 환율이 오르면 "
            "달러가 비싸지고 원화가 약해진다. 수입·여행·유학비와 수입물가 부담이 커질 수 있고, 수출기업에는 "
            "가격 경쟁력 개선 요인이 될 수 있지만 원재료 수입·환헤지·해외생산 구조에 따라 효과가 달라진다."
        )
        entry["example"] = (
            "2026년 6월 원/달러 환율은 장중 1,530원대를 기록했다. "
            "환율 상승은 수입물가 부담과 수출기업의 가격 경쟁력에 서로 다른 영향을 준다."
        )

    if entry := by_id.get("quantitative-easing"):
        entry["detail"] = (
            "정책금리가 매우 낮아 추가 인하 여력이 작을 때 중앙은행이 국채 등 자산을 사들여 금융여건을 "
            "완화하는 수단이다. 자산가격과 물가에 영향을 줄 수 있지만 결과는 재정정책·공급 충격·수요 여건과 함께 봐야 한다."
        )

    if entry := by_id.get("protectionism"):
        entry["example"] = (
            "핀로그 현직자 인터뷰에서는 보호무역이 강화될수록 원산지 분석·관세 컨설팅·공급망 다변화의 중요성이 커진다고 정리했다."
        )
        entry["example"] = (
            "코로나19 이후의 물가 상승은 완화적 통화·재정정책뿐 아니라 공급망 차질과 에너지 가격 상승 등이 함께 작용했다."
        )

    if entry := by_id.get("stock"):
        entry["detail"] = (
            "주식을 사면 회사의 일부를 소유하는 주주가 된다. 보통주는 의결권을 가질 수 있고, 배당은 회사의 "
            "이익과 이사회·주주총회 결정에 따라 받을 수 있다. 회사 성과와 시장 상황에 따라 주가가 오르거나 내려 손익이 발생한다."
        )
        entry["example"] = (
            "배당과 자사주 소각은 대표적인 주주환원 방식이다. 다만 소각이 주가 상승을 보장하는 것은 아니며, "
            "사업 전망과 자본배분의 지속 가능성을 함께 봐야 한다."
        )

    if entry := by_id.get("dividend-buyback"):
        entry["detail"] = (
            "배당은 이익의 일부를 현금으로 주주에게 나눠 주는 것이고, 자사주 소각은 회사가 보유한 자기주식을 "
            "없애 발행주식 수를 줄이는 것이다. 소각은 주당 지표를 개선할 수 있지만 시장가격 상승을 자동으로 보장하지 않는다."
        )
        entry["example"] = (
            "2026년 3월 시행된 개정 상법은 자기주식을 원칙적으로 1년 안에 소각하도록 하고, 예외적으로 보유할 때에는 "
            "주주총회 승인을 받은 처분계획을 요구한다. 기업별 실제 환원 규모는 공시로 확인해야 한다."
        )

    if entry := by_id.get("bond"):
        entry["example"] = (
            "한국의 WGBI 편입은 지수 추종 수요를 늘릴 수 있지만 실제 국채가격과 금리는 환율·통화정책·글로벌 금리 등 여러 요인에 함께 좌우된다."
        )

    if entry := by_id.get("ipo"):
        entry["example"] = (
            "파두 사건은 상장 전후 실적과 공시를 둘러싼 분쟁으로 IPO 실사와 추정치 검증의 중요성을 보여 준다. "
            "검찰은 관련자를 기소했고 회사는 은폐 의혹을 부인하고 있어 판결 확정 전에는 혐의를 사실로 단정하지 않는다."
        )

    if entry := by_id.get("short-selling"):
        entry["example"] = (
            "2025년 3월 31일 공매도가 전면 재개되면서 한국거래소의 "
            "공매도 중앙점검시스템(NSDS)도 가동됐다. NSDS는 기관 잔고와 주문내역을 "
            "대조해 무차입 공매도 의심 거래를 사후 상시 점검한다."
        )

    if entry := by_id.get("esg-disclosure"):
        entry["example"] = (
            "금융위원회의 2026년 7월 최종안은 2028년부터 연결자산 10조원 이상 "
            "코스피 상장사의 지속가능성 공시를 시작하고, Scope 3는 대상별로 3년 유예한다."
        )

    if entry := by_id.get("ai-basic-law"):
        entry["short"] = "권리·안전에 큰 영향을 주는 AI에 위험관리·설명·감독·문서화 등 신뢰성 조치를 요구하는 법."
        entry["detail"] = (
            "채용·의료·신용평가처럼 사람의 권리나 안전에 중대한 영향을 줄 수 있는 영역은 고영향 AI 해당 여부를 "
            "검토해야 한다. 해당 사업자는 위험관리, 기술적으로 가능한 설명 방안, 이용자 보호, 사람의 관리·감독, "
            "문서화 등 법이 정한 신뢰성 조치를 마련해야 한다."
        )
        entry["example"] = (
            "2026년 1월 22일 시행됐다. 금융 AI에서는 법 적용 여부를 먼저 확인하고, 설명·검증·이의제기 절차를 "
            "관련 금융법과 내부통제 기준까지 함께 설계하는 것이 안전하다."
        )

    if entry := by_id.get("alt-data-credit"):
        entry["example"] = (
            "통신비·공과금 같은 대안데이터는 금융 이력이 부족한 고객을 평가하는 보조 신호가 될 수 있다. "
            "다만 간접차별과 과도한 수집을 막기 위해 필요성·동의·집단별 결과·설명과 정정 절차를 함께 점검해야 한다."
        )
        entry["issues"] = [
            "금융 포용 : 대안 신용평가로 사회초년생·자영업자의 금융 접근성 확대.",
            "편향 위험 : 거주지·소비패턴이 지역·계층 차별로 이어질 수 있다.",
            "설명책임 : 법 적용 여부와 별개로 거절 사유 확인·이의제기·데이터 정정 경로를 설계.",
        ]

    if entry := by_id.get("ai-fraud-detection"):
        entry["short"] = "대규모 주문·거래 데이터에서 이상 패턴을 찾아 조사 대상을 좁히는 시장감시 기술."
        entry["example"] = (
            "2025년 3월 공매도 재개와 함께 KRX가 공매도중앙점검시스템(NSDS)을 가동했다. NSDS는 기관의 "
            "잔고와 매매 자료를 대조해 무차입 의심 거래를 사후 상시 점검하며, 주문 전 차단은 각 기관의 "
            "내부 잔고관리시스템이 맡는다. NSDS 자체를 AI 시스템과 동일시하지 않는다."
        )
        entry["conclusion"] = (
            "팀 토론의 결론은 ‘잡는 능력만큼 설명하는 능력’이다. 분석 도구는 조사 대상을 좁히는 보조 수단이고, "
            "최종 판단과 책임은 사람이 진다. 설명가능성은 감사·검토 가능성을 높이지만 제재의 법적 근거 자체를 대신하지 않는다."
        )
        entry["faqs"][1]["answer"] = (
            "경보의 근거를 사람이 재검토하고 오류에 이의를 제기할 수 있게 해 감사 가능성과 수용성을 높이기 때문입니다."
        )

    if entry := by_id.get("short-resume"):
        entry["example"] = (
            "핀로그는 2~3주차에 공매도의 순기능·역기능과 NSDS의 사후 상시 점검 구조, "
            "개인투자자 접근성 문제를 함께 다뤘다."
        )


def write_data(kb: list[dict], faqs: list[dict], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        "/* Generated by scripts/build_chatbot_data.py. Do not edit by hand. */\n"
        f"const KB = {json.dumps(kb, ensure_ascii=False, separators=(',', ':'))};\n"
        f"const FAQS = {json.dumps(faqs, ensure_ascii=False, separators=(',', ':'))};\n"
    )
    destination.write_text(payload, encoding="utf-8")


def update_faqs(faqs: list[dict]) -> None:
    """Remove unsupported figures and distinguish law from good practice."""
    replacements = {
        "파두 사태의 교훈은?": (
            "검찰이 상장 과정의 주요 매출 정보가 충분히 반영되지 않았다고 보고 기소한 사건으로, "
            "회사는 은폐 의혹을 부인하고 있습니다. 판결 확정 전에는 혐의를 사실처럼 단정하지 않아야 합니다."
        ),
        "왜 설명가능성(XAI)이 필요한가요?": (
            "경보와 판단의 근거를 사람이 재검토하고 오류에 이의를 제기할 수 있게 해 감사 가능성과 수용성을 높이기 때문입니다."
        ),
        "AI 기본법이 왜 중요한가요?": (
            "고영향 AI 해당 여부에 따라 위험관리·설명방안·이용자보호·사람의 감독·문서화 같은 신뢰성 조치를 요구하기 때문입니다."
        ),
    }
    for faq in faqs:
        if faq.get("q") in replacements:
            faq["a"] = replacements[faq["q"]]


def link_shared_data(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    source = re.sub(
        r"const KB = \[.*?\];\s*const FAQS = \[.*?\];\s*",
        "",
        source,
        count=1,
        flags=re.DOTALL,
    )
    marker = "<script src=\"assets/chatbot-data.js\"></script>"
    if marker not in source:
        source = source.replace("<script>\nconst IMG", f"{marker}\n<script>\nconst IMG", 1)
    path.write_text(source, encoding="utf-8")


def main() -> int:
    source = MAIN_HTML.read_text(encoding="utf-8")
    kb, faqs = extract(source)
    kb = replace_text(kb)
    faqs = replace_text(faqs)
    update_time_sensitive(kb)
    update_faqs(faqs)

    write_data(kb, faqs, ROOT / "assets" / "chatbot-data.js")
    write_data(kb, faqs, STANDALONE / "assets" / "chatbot-data.js")
    link_shared_data(MAIN_HTML)
    link_shared_data(STANDALONE / "index.html")
    print(f"Shared chatbot data built: terms={len(kb)}, faqs={len(faqs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
