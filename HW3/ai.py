"""
LocalLeadPulse - 在地商家口碑監控與流失客群挽回引擎 (Commercial Grade)
Copyright (c) 2026 LocalLeadPulse Solution
"""

import json
import os
import re
from datetime import datetime
from collections import Counter


class ReputationAnalyticsEngine:
    def __init__(self, avg_ticket_size=350, repeat_visits_per_year=12):
        """
        :param avg_ticket_size: 每位顧客平均客單價 (新台幣 NTD)
        :param repeat_visits_per_year: 滿意顧客一年平均回訪次數 (計算 LTV 終身價值)
        """
        self.avg_ticket_size = avg_ticket_size
        self.repeat_visits_per_year = repeat_visits_per_year
        self.customer_ltv = self.avg_ticket_size * self.repeat_visits_per_year

        # 商業風險與正面關鍵詞庫 (支援實體店、餐飲、民宿、專業服務)
        self.negative_lexicon = {
            "等太久": ("服務效率", 2.0),
            "態度差": ("服務態度", 3.0),
            "不耐煩": ("服務態度", 2.5),
            "蟑螂": ("衛生安全", 5.0),
            "不乾淨": ("衛生安全", 3.5),
            "難吃": ("產品質量", 2.5),
            "變質": ("食品安全", 4.5),
            "踩雷": ("綜合體驗", 2.0),
            "太貴": ("價格性價比", 1.5),
            "CP值低": ("價格性價比", 1.5),
            "不推薦": ("口碑流失", 2.0),
            "蚊蟲": ("環境品質", 2.0),
            "冷掉了": ("出餐品質", 2.0),
            "算錯錢": ("帳務爭端", 3.0),
            "吵雜": ("環境品質", 1.5),
        }

        self.positive_lexicon = [
            "好吃", "美味", "親切", "乾淨", "推薦", "CP值高",
            "超棒", "回訪", "熱情", "專業", "舒適", "貼心", "驚艷"
        ]

    def analyze_single_review(self, review):
        text = review.get("comment", "")
        rating = review.get("rating", 3)
        author = review.get("author", "匿名顧客")
        date = review.get("date", datetime.now().strftime("%Y-%m-%d"))

        # 檢測負面標籤與嚴重程度
        detected_issues = []
        severity_score = 0.0

        for keyword, (category, weight) in self.negative_lexicon.items():
            if keyword in text:
                detected_issues.append({"keyword": keyword, "category": category, "weight": weight})
                severity_score += weight

        # 檢測正面標籤
        detected_positives = [kw for kw in self.positive_lexicon if kw in text]

        # 計算急迫性等級 (Urgency Level)
        if rating <= 2 or severity_score >= 4.0:
            urgency = "HIGH (紅色緊急公關客訴)"
        elif rating == 3 or severity_score > 0:
            urgency = "MEDIUM (中度關注)"
        else:
            urgency = "LOW (正常/滿意評價)"

        # 自動生成公關回覆草稿 (PR Response Generator)
        reply_draft = self._generate_pr_reply(author, rating, detected_issues, detected_positives)

        return {
            "author": author,
            "rating": rating,
            "date": date,
            "comment": text,
            "urgency": urgency,
            "severity_score": round(severity_score, 1),
            "issues": detected_issues,
            "positives": detected_positives,
            "suggested_reply": reply_draft
        }

    def _generate_pr_reply(self, author, rating, issues, positives):
        """根據評價評級與問題分類，自動組裝高情商公關回函"""
        if rating >= 4:
            highlight = "、".join(positives[:2]) if positives else "整體用餐與消費"
            return (
                f"您好 {author}！非常感謝您的五星鼓勵！"
                f"很高興您對我們門市的【{highlight}】感到滿意。"
                f"團隊會持續堅持品質，熱烈期待很快能再次為您服務！"
            )
        elif rating == 3:
            return (
                f"親愛的 {author} 您好，感謝您撥冗留下寶貴指教。"
                f"我們非常重視您的反饋，相關改進建議已同步給現場主管檢視與優化，"
                f"希望能有機會再次為您提供更完美的服務體驗！"
            )
        else:
            # 負面評論針對核心問題進行同理心回覆
            issue_names = "、".join(list({iss['category'] for iss in issues})) if issues else "服務細節"
            return (
                f"{author} 您好，非常抱歉此次未能給您滿意的體驗！"
                f"針對您所反映的【{issue_names}】相關問題，店長已第一時間召集團隊檢討改善。"
                f"為表誠意並進一步了解狀況，誠摯邀請您致電門市或私訊粉專聯繫主管，"
                f"我們希望能親自向您致歉並提供妥善的補償方案，謝謝您願意給予我們進步的機會。"
            )

    def generate_executive_report(self, reviews):
        """產生具備商業決策價值的高階診斷報告"""
        total = len(reviews)
        if total == 0:
            return "無評價資料。"

        analyzed_list = [self.analyze_single_review(r) for r in reviews]
        ratings = [r["rating"] for r in analyzed_list]
        avg_rating = sum(ratings) / total

        high_risk_count = sum(1 for r in analyzed_list if "HIGH" in r["urgency"])
        medium_risk_count = sum(1 for r in analyzed_list if "MEDIUM" in r["urgency"])

        # 統計所有問題類別
        all_categories = []
        for r in analyzed_list:
            for iss in r["issues"]:
                all_categories.append(iss["category"])
        category_dist = Counter(all_categories)

        # 財務流失風險預估 (Financial At-Risk Revenue)
        # 假設每則 1~2 星差評若未妥善處理，將直接導致該客群與其親友共約 3 人次停止回訪
        estimated_churned_customers = high_risk_count * 2.5
        potential_revenue_loss = estimated_churned_customers * self.customer_ltv

        return {
            "total_reviews": total,
            "average_rating": round(avg_rating, 2),
            "high_risk_alerts": high_risk_count,
            "medium_risk_alerts": medium_risk_count,
            "category_distribution": dict(category_dist.most_common(5)),
            "estimated_churned_customers": round(estimated_churned_customers, 1),
            "potential_revenue_loss_ntd": int(potential_revenue_loss),
            "reviews_analyzed": analyzed_list
        }


def print_dashboard(report):
    print("\n" + "=" * 70)
    print(" 🚀 LocalLeadPulse - 在地商家口碑商情與流失營收分析看板")
    print("=" * 70)
    print(f" 監控評論總數   : {report['total_reviews']} 則")
    print(f" 平均星級分數   : ⭐ {report['average_rating']} / 5.0")
    print(f" 緊急客訴警報   : 🚨 {report['high_risk_alerts']} 件 (需在 24 小時內處理)")
    print(f" 一般改進建議   : ⚠️  {report['medium_risk_alerts']} 件")
    print("-" * 70)
    print(f" ⚠️  預估年度流失顧客數 : 約 {report['estimated_churned_customers']} 位顧客")
    print(f" 💸 預估商譽流失營業額 : NT$ {report['potential_revenue_loss_ntd']:,} 元 (基於 LTV 模型)")
    print("-" * 70)
    print(" 📌 前五大核心客訴焦點分佈:")
    for cat, cnt in report['category_distribution'].items():
        bar = "█" * (cnt * 4)
        print(f"   - {cat:<8} : {cnt} 次 {bar}")
    print("=" * 70)


def export_markdown_audit(report, store_name="金門特色餐廳旗艦店", filename="audit_report.md"):
    """自動將分析結果輸出成可交付給客戶的付費等級諮詢 Markdown 診斷書"""
    lines = [
        f"# 【LocalLeadPulse】門市商譽健檢與潛在客源挽回報告書",
        f"**受測商家**：{store_name}  ",
        f"**診斷時間**：{datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**報告編號**：LLP-{datetime.now().strftime('%Y%m%d%H%M')}\n",
        "---",
        "## 1. 核心指標摘要",
        f"- **監測評價數**：{report['total_reviews']} 則",
        f"- **平均顧客評分**：`{report['average_rating']} / 5.0`",
        f"- **高風險投訴件數**：`{report['high_risk_alerts']}` 件",
        f"- **年化流失營收風險估計**：**NT$ {report['potential_revenue_loss_ntd']:,} 元**\n",
        "## 2. 營運痛點分類排行榜",
    ]
    for rank, (cat, count) in enumerate(report["category_distribution"].items(), start=1):
        lines.append(f"{rank}. **{cat}**：累計提及 `{count}` 次")

    lines.append("\n## 3. 待處理緊急評價與高情商公關回覆範本 (可直接複製使用)\n")

    for idx, r in enumerate(report["reviews_analyzed"], start=1):
        if "HIGH" in r["urgency"]:
            lines.append(f"### 警報案例 #{idx} - 顧客：{r['author']} (給予 {r['rating']} 星)")
            lines.append(f"> **原始評論**：\"{r['comment']}\"")
            lines.append(f"- **診斷警報**：`{r['urgency']}` | 嚴重度指數: `{r['severity_score']}`")
            lines.append(f"- **推薦公關回覆 (Copy-Paste Ready)**：")
            lines.append(f"```text\n{r['suggested_reply']}\n```\n")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n[報表匯出] 已成功生成高階諮詢診斷書：{filename}")


if __name__ == "__main__":
    # 模擬真實商家評價資料集 (含金門/觀光與餐飲常見實務情境)
    sample_reviews = [
        {"author": "陳先生", "rating": 1, "date": "2026-11-02", "comment": "等太久了！點了套餐等了快一小時，店員態度差而且臉很臭，極度不推薦。"},
        {"author": "Linda K.", "rating": 2, "date": "2026-11-03", "comment": "餐點冷掉了，吃起來感覺難吃，而且店內居然看到蟑螂爬過，衛生安全堪憂！"},
        {"author": "張先生", "rating": 3, "date": "2026-11-04", "comment": "料理味道普通，但價格有點太貴，CP值低，沒有想像中驚豔。"},
        {"author": "王小佩", "rating": 5, "date": "2026-11-05", "comment": "服務超級親切！牛肉麵肉質美味軟嫩，份量超大，一定會再回訪！"},
        {"author": "Jason Wu", "rating": 5, "date": "2026-11-06", "comment": "環境非常乾淨舒適，店員很熱情介紹金門當地特色，大推！"},
        {"author": "李小姐", "rating": 1, "date": "2026-11-07", "comment": "結帳時店員算錯錢還不耐煩，說話很衝，踩雷一次就不會再去！"}
    ]

    # 初始化引擎 (設定顧客平均客單價 450 元，常客一年平均消費 8 次)
    engine = ReputationAnalyticsEngine(avg_ticket_size=450, repeat_visits_per_year=8)
    audit_report = engine.generate_executive_report(sample_reviews)

    # 輸出終端機圖形化看板
    print_dashboard(audit_report)

    # 自動輸出可做為接案交付產出的 Markdown 健檢報告
    export_markdown_audit(audit_report, store_name="金門金豐在地觀光餐廳", filename="client_audit_report.md")