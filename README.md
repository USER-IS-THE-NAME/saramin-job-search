# saramin-job-search

사람인(Saramin) 오픈 API를 이용해 신입 채용 공고를 조회하는 개인용 프로젝트입니다.

- 소개 페이지: https://user-is-the-name.github.io/saramin-job-search/

## 개요

신입 채용 시장에서 관심 직군의 공고를 사람인 API로 조회해 로컬 파일(JSON/CSV)로 정리하는
개인 구직 활동 보조 도구입니다. 조회할 직군·지역·고용형태는 아래 `SEARCHES` 목록에서
자유롭게 바꿀 수 있습니다.

## 사용 API

- [사람인 채용정보 API](https://oapi.saramin.co.kr) — `job-search` 엔드포인트
- 조회 조건(업종 코드, 지역, 고용형태, 키워드)은 `job_scraper_github.py`의
  `SEARCHES` 목록에서 직접 정의합니다.

## 실행 방법

```bash
pip install requests
export SARAMIN_API_KEY="발급받은 access-key"   # Windows PowerShell: $env:SARAMIN_API_KEY="..."
python job_scraper_github.py
```

실행하면 다음 위치에 결과가 저장됩니다.

```
~/saramin_job_search_output/saramin_jobs_YYYYMMDD.json
~/saramin_job_search_output/saramin_jobs_YYYYMMDD.csv
```

## 이용 목적 및 준수 사항

- 개인 구직 활동을 위한 비상업적 용도로만 사용합니다.
- 조회한 데이터를 재판매하거나 제3자에게 제공하지 않습니다.
- API 호출에는 사람인 이용약관(호출 건수 제한 등)을 따릅니다.

## 연락처

문의: 2001insoo@gmail.com
