"""
LeadScraper & AuditPulse - 在地商家數位體質審計與 B2B 接案潛在客源獲利引擎
================================================================================
【功能特性】
1. 商家數位足跡評估 (Google 商家評分、評論數、有無專屬獨立網站、SSL 支援、社群連結)。
2. 數位成熟度指數計算 (Digital Readiness Score, 0-100 分)。
3. 接案價值與商機評級 (高價值成交對象判斷：有預算需求但數位化不足的店家)。
4. 自動化生成客製化接案 Proposal / 健檢診斷書 (Markdown 格式)，供接案者直接發送給業主。
5. 支援模擬批次掃描或即時手動檢測，無須龐大依賴套件即可執行。
"""

import json
import math
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional


class BusinessLead:
    """商家潛在客戶資料實體"""
    def __init__(
        self,
        name: str,
        category: str,
        phone: str,
        rating: float,
        review_count: int,
        website_url: Optional[str] = None,
        has_ssl: bool = False,
        is_mobile_friendly: bool = False,
        has_fb_ig: bool = False,
        estimated_monthly_turnover: int = 200000  # 預估月營業額 (新台幣)
    ):
        self.name = name
        self.category = category
        self.phone = phone
        self.rating = rating
        self.review_count = review_count
        self.website_url = website_url
        self.has_ssl = has_ssl
        self.is_mobile_friendly = is_mobile_friendly
        self.has_fb_ig = has_fb_ig
        self.estimated_monthly_turnover = estimated_monthly_turnover

        # 衍生評估數據
        self.score = 0
        self.lead_tier = "C"  # A (高成交機率高回報), B (中度潛力), C (低潛力或已過度成熟)
        self.vulnerabilities: List[str] = []
        self.recommended_services: List[Dict[str, any]] = []

    def evaluate(self):
        """計算數位成熟度分數 (0~100) 與診斷弱點"""
        score = 0
        self.vulnerabilities.clear()
        self.recommended_services.clear()

        # 1. Google 商家評價面向 (滿分 30)
        if self.rating >= 4.5:
            score += 15
        elif self.rating >= 4.0:
            score += 10
        else:
            score += 5
            self.vulnerabilities.append(f"Google 商家評分偏低 ({self.rating} 星)，影響新客到店決策。")

        # 評論熱度
        if self.review_count >= 150:
            score += 15
        elif self.review_count >= 50:
            score += 10
        elif self.review_count >= 10:
            score += 5
        else:
            self.vulnerabilities.append(f"累積評論數過少 ({self.review_count} 則)，缺乏足夠社群背書。")
            self.recommended_services.append({
                "service": "Google 商家評價增長與口碑管理策略",
                "estimated_quote": 12000
            })

        # 2. 獨立品牌官網面向 (滿分 40)
        if self.website_url:
            score += 20
            if self.has_ssl:
                score += 10
            else:
                self.vulnerabilities.append("官網缺少 SSL 安全憑證 (HTTP)，瀏覽器會標記為不安全。")
                self.recommended_services.append({
                    "service": "全站安全性升級與 SSL 部署",
                    "estimated_quote": 6000
                })

            if self.is_mobile_friendly:
                score += 10
            else:
                self.vulnerabilities.append("網站未針對智慧型手機 (RWD) 進行最佳化，手機瀏覽體驗欠佳。")
                self.recommended_services.append({
                    "service": "現代化響應式 (RWD) 官網改版與 SEO 體質重構",
                    "estimated_quote": 38000
                })
        else:
            self.vulnerabilities.append("完全缺少獨立品牌官網，流量與潛在客源無法留存與自主變現。")
            self.recommended_services.append({
                "service": "高轉換率品牌形象官網架設 (含線上預約/菜單系統)",
                "estimated_quote": 45000
            })

        # 3. 社群運營面向 (滿分 30)
        if self.has_fb_ig:
            score += 30
        else:
            self.vulnerabilities.append("未整合 Facebook / Instagram 等社群漏斗，缺乏再行銷觸點。")
            self.recommended_services.append({
                "service": "社群自媒體品牌矩陣與在地廣告投放設定",
                "estimated_quote": 18000
            })

        self.score = min(100, score)

        # 判定接案價值等級 (Lead Tier)
        # 最優質的接案客戶：生意不差 (評價數或營業額有基礎)，但數位化嚴重不足
        if not self.website_url and self.review_count >= 20:
            self.lead_tier = "A (黃金級潛在客戶 - 痛點深、成交率極高)"
        elif self.score <= 50 and self.estimated_monthly_turnover >= 150000:
            self.lead_tier = "A (高價值客戶 - 具備預算但數位資產落後)"
        elif 50 < self.score <= 75:
            self.lead_tier = "B (成長型客戶 - 需局部升級與維護服務)"
        else:
            self.lead_tier = "C (成熟型店家 - 數位建設完備，外包機會較少)"


class LeadAuditPulseEngine:
    def __init__(self):
        self.leads: List[BusinessLead] = []

    def add_lead(self, lead: BusinessLead):
        lead.evaluate()
        self.leads.append(lead)

    def print_pipeline_dashboard(self):
        """終端機圖形化業務商機儀表板"""
        print("\n" + "=" * 80)
        print(" 🎯 LeadScraper & AuditPulse — 在地商家數位審計與接案商機看板")
        print("=" * 80)
        print(f"{'店家名稱':<18}{'業態分類':<12}{'評分':<6}{'成熟度':<10}{'商機潛力等級':<24}")
        print("-" * 80)

        total_potential_revenue = 0
        for l in self.leads:
            score_bar = "■" * (l.score // 10)
            score_display = f"{l.score}分 [{score_bar:<10}]"
            print(f"{l.name:<18}{l.category:<12}{l.rating:<6}{score_display:<14}{l.lead_tier:<24}")
            total_potential_revenue += sum(s["estimated_quote"] for s in l.recommended_services)

        print("-" * 80)
        print(f"📌 當前追蹤潛在客戶數 : {len(self.leads)} 間店家")
        print(f"💰 估算總可承攬接案規模 : NT$ {total_potential_revenue:,} 元")
        print("=" * 80)

    def export_sales_pitch_proposal(self, lead: BusinessLead, output_file: str):
        """將指定商家的審計結果轉換為可以直接寄發/提案的專業 Markdown 商業提案書"""
        total_quote = sum(s["estimated_quote"] for s in lead.recommended_services)
        
        md_content = f"""# 【數位體質診斷與品牌升級建議書】
**受評單位**：{lead.name} ({lead.category})  
**聯絡電話**：{lead.phone}  
**評估日期**：{datetime.now().strftime('%Y年%m月%d日')}  
**診斷機構**：AuditPulse 數位商譽與能見度顧問工作室  

---

## 一、 數位成熟度總結

- **綜合數位體質得分**：`{lead.score} / 100 分`
- **Google 商家狀態**：`{lead.rating} ⭐` (累積 `{lead.review_count}` 則顧客真實評價)
- **品牌官網建置**：{'已具備 (' + (lead.website_url or '') + ')' if lead.website_url else '❌ 尚未建置專屬獨立網站'}
- **行動裝置友善度 (RWD)**：{'✅ 良好' if lead.is_mobile_friendly else '❌ 未通過手機相容檢核'}
- **資料安全傳輸 (SSL)**：{'✅ 安全連線' if lead.has_ssl else '❌ 缺乏 HTTPS 加密保護'}

---

## 二、 核心營運與營收痛點發現 (Critical Vulnerabilities)

根據在地商圈競爭對手分析，貴店目前在數位接觸點上存在以下主要機會點：
"""
        for idx, v in enumerate(lead.vulnerabilities, start=1):
            md_content += f"{idx}. **{v}**\n"

        md_content += f"""
> **顧問觀點**：  
> 當前超過 83% 的消費者在前往實體店（特別是 {lead.category}）之前，會透過 Google 搜尋官網查看菜單、環境與線上訂位。缺少官網或手機體驗不良，將使貴店每日無形中流失大量過路客與觀光客源。

---

## 三、 客製化數位轉型改善專案與報價預算 (Recommended Solutions)

為解決上述痛點並直接提高來客成交率，我們建議採取以下分階段升級方案：

| 項目序號 | 建議導入服務名稱 | 核心產出與效益 | 預估投資預算 (NTD) |
|:---:|:---|:---|:---:|
"""
        for idx, s in enumerate(lead.recommended_services, start=1):
            md_content += f"| {idx} | **{s['service']}** | 建立可留存客群之數位資產，提升搜尋排名 | NT$ {s['estimated_quote']:,} |\n"

        md_content += f"""
**建議專案總投資金額**：**NT$ {total_quote:,} 元整**

---

## 四、 下一步行動 (Next Steps)
1. 雙方預約 15 分鐘線上或實體會議，確認版型風格與商業需求。
2. 簽署合約並支付 30% 訂金，預計 14 個工作天內完成上線與全面部署。
3. 歡迎隨時聯繫顧問團隊進行細節討論！
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f" [成功產出商業提案書] -> {output_file}")


def build_sample_dataset() -> List[BusinessLead]:
    """建立真實商務情境的示範資料（含金門/在地實體店常見樣態）"""
    return [
        BusinessLead(
            name="浯島風情老街民宿",
            category="觀光旅宿",
            phone="082-311234",
            rating=4.7,
            review_count=180,
            website_url=None,  # 典型黃金級客戶：評價極高、客源好，但沒有獨立官網被訂房平台抽成
            has_ssl=False,
            is_mobile_friendly=False,
            has_fb_ig=True,
            estimated_monthly_turnover=450000
        ),
        BusinessLead(
            name="金門古法牛肉麵旗艦店",
            category="餐飲美饌",
            phone="082-322567",
            rating=3.8,
            review_count=35,
            website_url="http://kinmen-beef-example.com",
            has_ssl=False,  # 沒有 SSL
            is_mobile_friendly=False, # 手機版破碎
            has_fb_ig=False,
            estimated_monthly_turnover=300000
        ),
        BusinessLead(
            name="太武山在地手作伴手禮",
            category="特產名店",
            phone="082-333890",
            rating=4.9,
            review_count=520,
            website_url="https://taiwu-gift-modern.com",
            has_ssl=True,
            is_mobile_friendly=True,
            has_fb_ig=True,
            estimated_monthly_turnover=800000
        ),
        BusinessLead(
            name="浯江日式手作咖啡坊",
            category="咖啡甜點",
            phone="082-355678",
            rating=4.2,
            review_count=42,
            website_url=None,
            has_ssl=False,
            is_mobile_friendly=False,
            has_fb_ig=True,
            estimated_monthly_turnover=180000
        )
    ]


if __name__ == "__main__":
    engine = LeadAuditPulseEngine()
    
    # 載入示範資料庫
    for lead in build_sample_dataset():
        engine.add_lead(lead)

    # 1. 輸出商機儀表板
    engine.print_pipeline_dashboard()

    # 2. 自動針對最具價值的 A 級客戶匯出商業提案書
    golden_lead = engine.leads[0]  # 浯島風情老街民宿
    engine.export_sales_pitch_proposal(golden_lead, "PROPOSAL_浯島風情老街民宿.md")
    
    # 再輸出第二間有技術漏洞的餐飲店
    restaurant_lead = engine.leads[1] # 金門古法牛肉麵旗艦店
    engine.export_sales_pitch_proposal(restaurant_lead, "PROPOSAL_金門古法牛肉麵旗艦店.md")