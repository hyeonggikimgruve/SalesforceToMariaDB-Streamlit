# ☁️ Salesforce Data ETL Manager

Salesforce 데이터를 효율적으로 추출(Extract), 변환(Transform), 적재(Load)하고 자동화할 수 있는 관리 대시보드입니다. Streamlit을 기반으로 구축되어 직관적인 UI를 제공하며, Heroku 환경에 최적화되어 있습니다.

## 🚀 데모 접속 (Demo URL)
실행 중인 서비스는 아래 링크에서 확인할 수 있습니다:
👉 [https://hk-salesforce-etl-v1-47a73e491c1a.herokuapp.com/](https://hk-salesforce-etl-v1-47a73e491c1a.herokuapp.com/)

---

## ✨ 주요 기능 (Key Features)

### 1. 🔐 Salesforce 연결 관리
- Salesforce API 연동을 위한 인증 설정 (Username, Password, Security Token 등).
- 간편한 로그인 및 접속 상태 확인.

### 2. 📊 데이터 추출 설정 (Extract)
- Salesforce 내의 모든 객체(Object) 및 필드(Field) 목록 자동 조회.
- 추출하고자 하는 데이터셋(Mapping) 정의 및 데이터 미리보기(Preview) 기능 제공.

### 3. 🛠️ 데이터 변환 및 매핑 (Transform)
- **Source to Target Mapping**: Salesforce 필드와 MariaDB 컬럼 간의 1:1 매핑.
- **Data Transformation**:
  - 데이터 타입 변환 (Number, Date, DateTime, Boolean).
  - 날짜/시간 형식 지정 및 타임존 변환 (UTC <-> Asia/Seoul).
  - Enum Mapping (JSON 기반 값 치환).

### 4. 🚀 데이터 적재 전략 (Load)
- **로드 순서 제어**: 객체 간의 종속성을 고려한 실행 순서 설정.
- **다양한 적재 방식**:
  - `INSERT`: 단순 행 삽입.
  - `BULK LOAD / COPY`: 대량 데이터 고속 적재.
  - `MERGE (UPSERT)`: 매칭 키 기준 중복 업데이트.
  - `OVERWRITE`: 테이블 초기화 후 데이터 적재.

### 5. ⏰ 스케줄링 및 자동화 (Schedule)
- APScheduler를 활용한 ETL 작업 주기 설정.
- 주기적인 데이터 동기화 자동화.

### 6. 🗄️ MariaDB/MySQL 연동
- 타겟 데이터베이스(MariaDB)의 연결 정보 관리 및 테스트.

---

## 🛠️ 기술 스택 (Tech Stack)

- **Language:** Python 3.14
- **UI Framework:** [Streamlit](https://streamlit.io/)
- **SF Integration:** [simple-salesforce](https://github.com/simple-salesforce/simple-salesforce)
- **Data Handling:** Pandas
- **Scheduling:** APScheduler
- **Database:** MariaDB (Postgres 지원 가능)
- **Deployment:** Heroku

---

## ⚙️ 로컬 실행 방법 (Setup & Installation)

1. **저장소 클론**
   ```bash
   git clone <repository_url>
   cd New_Salesforce_Data_App
   ```

2. **가상환경 설정 및 패키지 설치**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **애플리케이션 실행**
   ```bash
   streamlit run app.py
   ```

---

## 📄 라이선스
이 프로젝트는 교육 및 관리 목적으로 제작되었습니다.
