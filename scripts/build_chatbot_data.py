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
    replacements += (
        ("저는 ", "팀은 "),
        ("제 결론은", "팀이 함께 정리한 결론은"),
        ("제가 내린 결론", "팀이 함께 정리한 결론"),
        ("제가 현장에서 내린 결론", "팀이 함께 정리한 결론"),
        ("이렇게 판단했습니다", "이와 같이 정리했습니다"),
        ("이렇게 판단했다", "이와 같이 정리했다"),
        ("잡아내는", "탐지하는"),
        ("잡아냅니다", "탐지합니다"),
        ("잡아낸다", "탐지한다"),
        ("반칙", "위반 행위"),
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


def update_editorial_tone(entries: list[dict]) -> None:
    """Use a restrained, professional register throughout the knowledge base."""
    by_id = {entry.get("id"): entry for entry in entries}

    if entry := by_id.get("base-rate"):
        entry["short"] = "한국은행이 통화정책을 운용할 때 기준으로 삼는 정책금리."
        entry["detail"] = (
            "기준금리는 한국은행이 금융기관과의 7일물 환매조건부증권(RP) 거래에 적용하는 "
            "정책금리다. 변화는 콜금리와 예금·대출금리, 환율, 자산가격을 거쳐 소비와 투자에 "
            "영향을 미친다. 한국은행은 물가안정과 성장, 금융안정 여건을 함께 고려해 결정한다."
        )

    if entry := by_id.get("inflation"):
        entry["detail"] = (
            "인플레이션은 상품과 서비스의 전반적인 가격 수준이 지속해서 상승하는 현상이다. "
            "같은 금액으로 구입할 수 있는 재화가 줄어 화폐의 구매력이 낮아진다. 완만한 물가상승은 "
            "경제활동과 함께 나타날 수 있지만, 상승 속도가 소득 증가를 웃돌면 가계의 실질 구매력이 약화된다."
        )

    if entry := by_id.get("gdp"):
        entry["detail"] = (
            "GDP는 일정 기간 한 나라 안에서 생산된 최종 재화와 서비스의 시장가치를 합산한 지표다. "
            "소비·투자·정부지출과 순수출로 구성되며, 경제 규모와 성장 흐름을 파악하는 데 활용된다. "
            "다만 분배, 삶의 질, 환경비용까지 직접 보여 주는 지표는 아니다."
        )

    if entry := by_id.get("quantitative-easing"):
        entry["short"] = (
            "정책금리 인하 여력이 제한될 때 중앙은행이 국채 등 자산을 매입해 금융여건을 완화하는 비전통적 통화정책."
        )

    if entry := by_id.get("stock"):
        entry["short"] = "기업에 대한 소유권의 일부와 이에 수반되는 권리를 나타내는 증권."

    if entry := by_id.get("bond"):
        entry["short"] = "정부나 기업이 자금을 조달하며 원금과 이자 지급을 약정해 발행하는 증권."
        entry["detail"] = (
            "채권은 정부나 기업이 자금을 빌리기 위해 발행하는 증권이다. 발행자는 정해진 조건에 따라 "
            "이자와 원금을 지급한다. 시장금리가 오르면 기존 채권의 상대적 매력이 낮아져 가격이 하락하고, "
            "시장금리가 내리면 기존 채권의 가격은 상승하는 것이 일반적이다."
        )

    if entry := by_id.get("short-selling"):
        entry["detail"] = (
            "공매도는 주식을 차입해 먼저 매도한 뒤 나중에 매수해 상환하는 거래다. 가격 하락 시 차익을 "
            "얻을 수 있으며 가격발견과 유동성 공급에 기여할 수 있다. 다만 주식을 빌리지 않고 매도하는 "
            "무차입 공매도는 금지되며, 개인과 기관 사이의 차입 여건과 정보 격차도 주요 쟁점이다."
        )
        entry["conclusion"] = (
            "팀은 공매도 논의를 허용과 금지의 이분법보다 시장감시의 투명성 문제로 정리했다. NSDS를 "
            "비롯한 전산 점검, 개인의 대차 접근성 개선, 정보 격차 완화가 함께 이루어져야 시장 신뢰를 "
            "높일 수 있다고 보았다. 제도 개선이 투자수익을 보장하지 않는다는 점도 함께 확인했다."
        )

    if entry := by_id.get("false-positive"):
        entry["short"] = (
            "탐지 기준을 강화하면 정상 거래를 이상으로 판단하는 오탐이 늘고, 완화하면 이상 거래를 놓치는 미탐이 늘어나는 상충관계."
        )

    if entry := by_id.get("carbon-tax"):
        entry["detail"] = (
            "기업이나 개인이 화석연료를 사용하며 배출하는 탄소에 가격을 부과해, "
            "시장가격에 반영되지 않던 사회적 비용을 배출자의 비용으로 전환하는 제도다. "
            "감축 유인을 만들지만 에너지 비용과 산업 경쟁력에 영향을 줄 수 있어 "
            "도입 속도와 범위가 주요 쟁점이 된다."
        )

    if entry := by_id.get("financial-statements"):
        entry["detail"] = (
            "재무제표는 기업의 재무상태와 경영성과를 체계적으로 보여 주는 보고서다. "
            "손익계산서는 일정 기간의 수익과 비용, 재무상태표는 특정 시점의 자산·부채·자본, "
            "현금흐름표는 실제 현금의 유입과 유출을 기록한다. 회계상 이익이 발생해도 "
            "현금흐름이 악화되면 유동성 위험이 커질 수 있으므로 세 표를 함께 살펴야 한다. "
            "수치는 당시 보도 기준이며 확정치는 DART 사업보고서를 참조한다."
        )
        for faq in entry.get("faqs", []):
            if faq.get("question") == "흑자도산이 뭔가요?":
                faq["question"] = "흑자도산이란 무엇인가요?"
                faq["answer"] = (
                    "장부상 이익이 발생하더라도 현금 유입이 부족해 채무를 제때 상환하지 못하고 "
                    "유동성 위기에 처하는 상황입니다. 현금흐름표를 함께 살펴야 하는 이유입니다."
                )

    if entry := by_id.get("mm-wacc"):
        entry["detail"] = (
            "MM이론은 세금과 거래비용이 없는 이상적 시장에서는 자본구조가 기업가치에 "
            "영향을 주지 않는다는 출발점을 제시한다. 세금을 고려한 수정이론에서는 "
            "부채 이자비용의 절세효과로 적정 수준의 부채가 기업가치를 높일 수 있다고 본다. "
            "WACC는 자기자본과 부채의 조달비용을 비중에 따라 가중평균한 자본비용이다."
        )

    if entry := by_id.get("stablecoin"):
        entry["detail"] = (
            "스테이블코인은 달러·원화 등 기준자산에 가치를 연동하도록 설계한 디지털 자산이다. "
            "가격 안정성과 환매 가능성은 준비자산의 구성과 보관, 발행사의 건전성, 공시와 감사의 "
            "신뢰도에 좌우된다. 발행 구조가 부실하거나 환매 요구가 집중되면 연동 가격이 이탈할 수 있다."
        )
        issues = entry.get("issues", [])
        if len(issues) > 1:
            issues[1] = (
                "준비자산 투명성 : 발행사가 공시한 비율에 맞춰 준비자산을 보유하는지, "
                "감사와 공시를 통해 확인할 수 있는지가 신뢰의 핵심."
            )
        entry["conclusion"] = (
            "팀은 스테이블코인의 본질을 준비자산과 환매 가능성으로 정리했다. 이를 증권·예금·전자화폐 중 "
            "어떤 체계로 규율할 것인지 검토하고, 지급결제 인프라로 확장될수록 금융안정을 위한 규율이 "
            "선행되어야 한다고 보았다. 디지털금융포럼에서 확인한 논의도 이 관점에 반영했다."
        )

    if entry := by_id.get("regtech"):
        entry["detail"] = (
            "레그테크는 규제(Regulation)와 기술(Technology)을 결합해 금융회사의 규정 준수 업무를 "
            "지원하는 체계다. 거래 모니터링, 고객확인(KYC), 자금세탁방지(AML), 보고 업무의 일부를 "
            "자동화해 이상 징후를 조기에 탐지한다. 정확도뿐 아니라 오탐 관리, 판단 근거의 설명, "
            "사람의 재검토 절차가 함께 마련되어야 한다."
        )
        entry["conclusion"] = (
            "팀은 레그테크의 핵심을 오탐과 미탐 사이의 균형으로 정리했다. 자동화의 효율성과 함께 "
            "탐지 근거를 설명하고 사람이 재검토할 수 있는 절차가 규제 신뢰를 좌우한다. 이에 따라 "
            "컴플라이언스 인재에게는 규제 지식과 데이터 이해를 함께 갖추는 역량이 중요하다고 보았다."
        )

    if entry := by_id.get("t_기업 밸류업·주주환원"):
        entry["short"] = (
            "기업 밸류업은 단순한 주가 부양이 아니라, 경영진이 투자·배당·자사주 정책의 근거를 "
            "투명하게 제시하고 자본을 효율적으로 배분하도록 유도하는 정책이다."
        )

    if entry := by_id.get("t_알고리즘 의사결정의 공정성·금융윤리"):
        entry["short"] = (
            "AI가 대출심사에 관여할수록 결정 근거를 설명하고 오류에 이의를 제기할 수 있는 "
            "절차가 중요해진다."
        )

    if entry := by_id.get("fab-value-chain"):
        entry["detail"] = (
            "엔비디아처럼 반도체 설계를 전문으로 하는 기업이 팹리스, TSMC처럼 외부 설계를 "
            "위탁받아 생산하는 기업이 파운드리다. HBM 같은 첨단 메모리는 여러 칩을 적층하는 "
            "패키징 기술이 경쟁력을 좌우한다. 이 가치사슬을 이해하면 반도체 기업의 실적과 "
            "경쟁구도를 보다 정확히 해석할 수 있다."
        )

    interview_tips = {
        "carbon-tax": (
            "[국책은행 직무 연결] CBAM의 영향을 받는 수출 중소·중견기업에 장기·저리 전환금융을 공급하고, "
            "저탄소 설비투자와 공시 역량을 함께 지원하는 정책금융의 역할을 검토할 수 있다."
        ),
        "short-selling": (
            "[KRX·KSD 직무 연결] 공매도 정상화는 시장 접근성과 투자자 보호를 함께 다루는 과제다. "
            "NSDS 고도화, 대차 인프라 개선, 전산 점검의 한계를 균형 있게 설명할 수 있다."
        ),
        "derivatives": (
            "[증권사 리스크관리 직무 연결] 파생상품의 꼬리위험을 VaR와 스트레스테스트로 측정하고, "
            "상품 설계와 판매 과정의 투자자 보호를 함께 점검하는 접근이 중요하다."
        ),
        "financial-statements": (
            "[기업금융·여신심사 직무 연결] 시장배수뿐 아니라 현금흐름과 대안데이터를 함께 검토해 "
            "기업의 실질 상환능력과 유동성 위험을 입체적으로 평가할 수 있다."
        ),
        "stablecoin": (
            "[한국은행·금융결제원 직무 연결] CBDC와 스테이블코인을 지급결제 효율성, 통화주권, "
            "준비자산과 환매 위험의 관점에서 비교해 설명할 수 있다."
        ),
        "alt-data-credit": (
            "[인터넷전문은행·핀테크 직무 연결] 대안데이터로 금융이력이 부족한 고객의 평가 공백을 줄이되, "
            "간접차별을 점검하는 정기 검증과 이의제기 절차를 함께 설계해야 한다."
        ),
        "ai-fraud-detection": (
            "[KRX·금융감독 직무 연결] 이상거래 탐지의 정확도뿐 아니라 SHAP·LIME 등을 활용한 설명, "
            "감사기록, 사람의 재검토를 포함하는 모델 거버넌스를 제시할 수 있다."
        ),
        "regtech": (
            "[은행 AML 직무 연결] AI 기반 모니터링은 오탐률과 내부통제 비용을 낮출 수 있으나, "
            "고영향 AI 해당 여부와 설명·감독·문서화 요건을 함께 검토해야 한다."
        ),
        "esg-disclosure": (
            "[은행·국책은행 ESG 직무 연결] ESG 데이터를 공시 작성에 그치지 않고 기후위험의 측정, "
            "여신심사, 금리 산정과 연결하는 기후금융 체계를 검토할 수 있다."
        ),
        "yellow-envelope": (
            "[경제·시사 토론 연결] 노동권 보장과 함께 노사 불확실성이 투자와 위험 프리미엄에 미치는 영향을 살피고, "
            "예측 가능한 적용 기준과 분쟁 조정 절차의 필요성을 논의할 수 있다."
        ),
        "t_복수거래소": (
            "[증권사 IT·기획 직무 연결] 복수거래소 환경에서는 최선집행의무를 뒷받침하는 SOR, "
            "통합 시세, 체결 품질 측정 역량이 중요하다."
        ),
        "t_자본시장 인프라": (
            "[KRX·KSD 직무 연결] 시장 변동성이 확대될수록 권리관리와 결제 안정성이 중요해진다. "
            "새 제도를 뒷받침할 데이터 표준화와 인프라 고도화 과제를 제시할 수 있다."
        ),
        "t_블록체인·가상자산": (
            "[은행·증권 디지털 직무 연결] 가상자산의 제도권 편입을 위험관리 과제와 함께 디지털 수탁, "
            "토큰화 자산 관리 등 신사업 기회의 관점에서도 검토할 수 있다."
        ),
        "t_기업 밸류업·주주환원": (
            "[리서치·자산운용 직무 연결] 밸류업을 단기 주가 재료보다 자본배분과 지배구조 개선의 문제로 보고, "
            "배당·자사주·투자계획의 지속가능성을 함께 평가할 수 있다."
        ),
        "t_기업 지배구조·책임경영": (
            "[은행 디지털 직무 연결] 알고리즘 여신의 책임 소재를 명확히 하기 위해 모델 검증, "
            "설명책임, 승인과 변경관리 절차를 포함한 AI 거버넌스가 필요하다."
        ),
        "t_알고리즘 의사결정의 공정성·금융윤리": (
            "[금융 IT·데이터 직무 연결] 예측력과 함께 간접차별 요소, 집단별 오류율, 설명과 이의제기 절차를 "
            "점검하는 모델 거버넌스를 설계할 수 있다."
        ),
        "t_빅테크 독점과 플랫폼 규제": (
            "[금융 전략 직무 연결] 플랫폼의 규모보다 자사우대·데이터 잠금 등 구체적 행위를 중심으로 규율하고, "
            "금융회사의 규제 준수와 신뢰 역량을 서비스 전략에 반영할 수 있다."
        ),
        "t_세대갈등": (
            "[금융감독 직무 연결] 고령층의 금융소외와 금융사기 위험을 낮추는 동시에 청년층의 자산형성 기회를 넓혀, "
            "세대 간 형평과 제도의 지속가능성을 함께 살펴야 한다."
        ),
        "t_학생인권 vs 교권": (
            "[조직 갈등관리 연결] 권리의 우열보다 생활지도 기준, 민원 처리, 책임 분담의 공백을 진단하고 "
            "예측 가능한 절차를 마련하는 관점으로 설명할 수 있다."
        ),
        "t_반도체·HBM 경쟁": (
            "[산업금융 직무 연결] HBM 경쟁은 설비투자, 공급망, 고객 인증, 환위험이 결합된 산업금융 과제다. "
            "신디케이트론과 정책자금의 역할을 기업별 현금흐름과 함께 검토할 수 있다."
        ),
        "t_관세·보호무역": (
            "[무역금융 직무 연결] 보호무역의 영향을 업종별 원산지와 공급망 구조로 구분하고, "
            "수출금융·환위험 관리·공급망 다변화 지원 방안을 함께 제시할 수 있다."
        ),
    }
    for entry_id, text in interview_tips.items():
        if entry := by_id.get(entry_id):
            entry["interview_tip"] = text

    for entry in entries:
        for faq in entry.get("faqs", []):
            if "question" in faq:
                faq["question"] = faq["question"].replace("뭔가요?", "무엇인가요?")


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
        faq["q"] = faq.get("q", "").replace("뭔가요?", "무엇인가요?")
        if faq.get("q") in replacements:
            faq["a"] = replacements[faq["q"]]
        if faq.get("q") == "흑자도산이 무엇인가요?":
            faq["a"] = (
                "장부상 이익이 발생하더라도 현금 유입이 부족해 채무를 제때 상환하지 못하고 "
                "유동성 위기에 처하는 상황입니다."
            )


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
    update_editorial_tone(kb)
    update_faqs(faqs)

    write_data(kb, faqs, ROOT / "assets" / "chatbot-data.js")
    write_data(kb, faqs, STANDALONE / "assets" / "chatbot-data.js")
    link_shared_data(MAIN_HTML)
    link_shared_data(STANDALONE / "index.html")
    print(f"Shared chatbot data built: terms={len(kb)}, faqs={len(faqs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
