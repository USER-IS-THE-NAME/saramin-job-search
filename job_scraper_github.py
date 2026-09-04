#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
saramin-job-search (job_scraper_github.py)

사람인(Saramin) 오픈 API만을 사용해 신입 채용 공고를 조회하고 로컬 파일로
저장하는 개인 프로젝트용 데모 스크립트입니다.

- 다른 채용 사이트(잡코리아/CATCH/링커리어 등)에 대한 코드는 포함하지 않습니다.
- Notion 등 외부 서비스 연동이 없습니다 — 결과는 로컬 JSON/CSV로만 저장합니다.
- API 키는 하드코딩하지 않고 환경변수(SARAMIN_API_KEY)에서 읽습니다.
- 실행 경로는 모두 상대경로/사용자 홈 기준이며, 특정 개인 환경에 종속된
  값(절대경로, 실명, 이메일 등)은 들어있지 않습니다.

사용 전 필수:
  1. https://oapi.saramin.co.kr 에서 이용신청 → 승인 후 access-key 발급
  2. 환경변수 설정
       (macOS/Linux) export SARAMIN_API_KEY="발급받은키"
       (Windows PowerShell) $env:SARAMIN_API_KEY="발급받은키"
  3. pip install requests
  4. python job_scraper_github.py

검색 조건(직군/지역/신입 여부 등)은 아래 SEARCHES 리스트에서 자유롭게 바꿀 수
있습니다.
"""

import os
import sys
import json
import time
import csv
from datetime import datetime

import requests

# ──────────────────────────────────────────────
# 설정 — 개인 식별 정보 없음, 전부 환경변수/상대경로 기반
# ──────────────────────────────────────────────

SARAMIN_API_KEY = os.environ.get("SARAMIN_API_KEY", "")
SARAMIN_BASE_URL = "https://oapi.saramin.co.kr/job-search"

# 지역 코드(사람인 loc_mcd 기준), 필요에 맞게 조정
# 예시: 101000=서울, 102000=경기, 108000=인천, 115000=충북
SARAMIN_LOC = "101000,102000,108000,115000"

# 고용형태: 1=정규직, 4=인턴
JOB_TYPES = [("정규직", "1"), ("인턴", "4")]

# 검색 조건 목록: (표시용 라벨, 업종 코드, 키워드)
# 업종 코드는 사람인 API 문서(oapi.saramin.co.kr/guide/job-search)의
# industry 코드표를 참고해 원하는 값으로 바꾸면 됩니다.
SEARCHES = [
    ("제약/바이오 품질", "703", "품질 QA QC 생산관리"),
    ("식품 품질",        "214", "품질 QA QC 생산관리"),
    ("은행/금융 신입",   "401", ""),
]

OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "saramin_job_search_output")
TODAY = datetime.now().strftime("%Y%m%d")


def fetch_saramin_jobs():
    """사람인 API로 SEARCHES에 정의된 조건을 전부 조회해 리스트로 반환."""
    if not SARAMIN_API_KEY:
        print("[오류] 환경변수 SARAMIN_API_KEY가 설정되지 않았습니다.")
        print("       export SARAMIN_API_KEY=\"발급받은키\" 로 설정한 뒤 다시 실행하세요.")
        sys.exit(1)

    jobs = []
    for label, industry_code, keywords in SEARCHES:
        for jt_label, jt_code in JOB_TYPES:
            params = {
                "access-key":  SARAMIN_API_KEY,
                "industry":    industry_code,
                "loc_mcd":     SARAMIN_LOC,
                "career_type": "1",   # 신입
                "job_type":    jt_code,
                "edu_lv":      "3",
                "sort":        "pd",  # 등록일순
                "count":       "50",
                "start":       "1",
            }
            if keywords:
                params["keywords"] = keywords

            try:
                res = requests.get(SARAMIN_BASE_URL, params=params, timeout=12)
                res.raise_for_status()
                data = res.json()
                job_list = data.get("jobs", {}).get("job", [])
                if not isinstance(job_list, list):
                    job_list = [job_list] if job_list else []

                for job in job_list:
                    company = job.get("company", {}).get("detail", {}).get("name", "")
                    position = job.get("position", {})
                    jobs.append({
                        "category":  f"{label} ({jt_label})",
                        "company":   company,
                        "title":     position.get("title", ""),
                        "location":  position.get("location", {}).get("name", ""),
                        "career":    position.get("experience-level", {}).get("name", "신입"),
                        "job_type":  jt_label,
                        "deadline":  job.get("active", {}).get("close-date", "상시"),
                        "url":       job.get("url", ""),
                    })

                print(f"[사람인] {label} / {jt_label}: {len(job_list)}건")
                time.sleep(0.5)  # 과도한 요청 방지

            except requests.exceptions.RequestException as e:
                print(f"[오류] {label} / {jt_label}: {e}")

    return jobs


def save_json(jobs):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"saramin_jobs_{TODAY}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"[저장] {path} ({len(jobs)}건)")
    return path


def save_csv(jobs):
    if not jobs:
        return None
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"saramin_jobs_{TODAY}.csv")
    fieldnames = list(jobs[0].keys())
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)
    print(f"[저장] {path} ({len(jobs)}건)")
    return path


if __name__ == "__main__":
    print("=" * 50)
    print(f" saramin-job-search: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    all_jobs = fetch_saramin_jobs()
    print(f"\n총 {len(all_jobs)}건 수집")

    save_json(all_jobs)
    save_csv(all_jobs)
