# Project Guidelines

본 문서는 Python 3.14 기반으로 Heroku에서 동작하는  
Salesforce 데이터 조회 서비스의 **공통 개발 규칙 및 운영 원칙**을 정의한다.

---

## 1. 프로젝트 개요

- Python 버전: **3.14**
- 배포 환경: **Heroku**
- Salesforce 연동: **simple-salesforce**
- simple-salesforce library is included.
- 목적:
  - Salesforce 데이터를 조회(Read-only)
  - 조회 결과를 가공하여 API 또는 배치 작업으로 제공
---

## 2. 기본 원칙

### 2.1 Stateless 원칙
- Heroku 환경 특성상 **서버는 항상 Stateless**로 동작해야 한다.
- 로컬 파일 시스템에 영구 데이터를 저장하지 않는다.
- 모든 상태 정보는 아래 중 하나를 사용한다:
  - Salesforce
  - 외부 DB (Postgres 등)
---

### 2.2 Ephemeral File System 규칙
- 임시 파일은 허용.
- 임시 파일 경로는 `/tmp` 디렉토리만 사용한다.

```python
TEMP_DIR = "/tmp"