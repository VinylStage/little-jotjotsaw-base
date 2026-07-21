# finance-tracker 개요

## 1. 프로젝트 한 줄 요약
개인 가계부 웹앱으로, Google Sheets/Excel 대체를 목표로 하며 실시간 그래프와 카테고리 자동 제안 기능을 제공하는 단일 프로세스 로컬 앱 (로컬 디렉토리명: `finace-tracker` 오타 주의).

## 2. 기술 스택
| 구성 요소       | 기술 스택                          | 비고                                  |
|----------------|----------------------------------|-------------------------------------|
| 백엔드          | Node.js, Express                  | REST API 및 정적 파일 서빙              |
| 데이터베이스     | SQLite (better-sqlite3)           | 로컬 파일 DB, `data/` 디렉토리에 저장 (git 제외) |
| 프론트엔드      | React + Vite, Tailwind CSS        | Recharts 차트, 다크 테마 지원           |
| 기타            | npm start (localhost:3000)         | 인증/클라우드 없이 단일 명령어로 실행      |

## 3. 아키텍처 흐름
```
브라우저 → localhost:3000 → Express → [API 경로 → SQLite, 정적 경로 → React 빌드]
```

## 4. 디렉토리 구조 핵심
- `src/server.js`: Express 진입점
- `src/db/init.js`: SQLite 스키마/연결 초기화
- `src/routes/`: `transactions.js`, `categories.js`, `paymentMethods.js`
- `scripts/migrate-xlsx.js`: 1회성 엑셀 마이그레이션 스크립트
- `client/`: React/Vite 소스 (페이지/컴포넌트)
- `data/`: SQLite DB 파일 (git 제외)
- `ref/`: 원본 XLSX 파일 (git 제외)

## 5. 개발 로드맵 진행 현황
| 단계                     | 상태       | 세부 내용                                                                 |
|------------------------|----------|-------------------------------------------------------------------------|
| Phase 0 (기반 구축)      | ✅ 완료    | Express/SQLite 스캐폴딩, 7개 테이블 스키마, XLSX 마이그레이션(219건), REST API CRUD |
| Phase 1 (핵심 UI)        | ✅ 완료    | 대시보드(수입/지출/가용현금), 거래 내역 리스트, 카테고리 자동제안, 다크 테마       |
| Phase 2 (할부·리볼빙)    | ⏳ 진행 예정 | 할부 등록 화면, 리볼빙 원장, 부채 현황 (이중 계산 방지 검증 중)                |
| Phase 3 (카테고리 고도화) | ⏳ 미완료   | UX 개선, 최근 가맹점 자동완성, 가맹점 별칭 관리                                |
| Phase 4 (현금흐름 그래프) | ⏳ 미완료   | `/api/cashflow`, Recharts LineChart, 카테고리별 막대그래프, React Query 실시간 갱신 |
| Phase 5 (시뮬레이터)     | ⏳ 미완료   | 예상잔액 시뮬레이터, 적금/저축성보험 원장, 만기 처리                          |
| Phase 6 (마무리)         | ⏳ 미완료   | CSV/JSON 내보내기, 설정 화면, 모바일 반응형, 성능 테스트(5,000건 1초 이내)     |

## 6. 관련 문서
- **트러블슈팅**: [2026-07 트러블슈팅 로그](../../troubleshooting/2026-07-finance-tracker.md) (better-sqlite3 ELF 헤더 오류 등 6건 수록)
