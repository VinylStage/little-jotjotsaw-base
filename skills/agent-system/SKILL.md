---
name: agent-system
description: 이 조직의 에이전트 역할 분담(EVA/AXEL/FORGE/VANCE/NEXUS/ORACLE)과 컨펌 체인, ORACLE 호출 규칙을 안내한다. 사용자가 "에이전트 조직", "agent roles", "누가 뭐 담당" 등을 물을 때 사용한다.
---

**참고**: 이 요약은 `docs/process/PROCESS_GUIDE.md`(구체적 역할명이 정의된 원본)와 `docs/process/AGENT_SYSTEM.md`(위임 기준·ORACLE 호출 규칙·세션 위생 원칙)를 함께 반영한 것이다. 역할 이름(EVA/AXEL 등)은 AGENT_SYSTEM.md에는 없고 PROCESS_GUIDE.md에만 정의되어 있으므로, 최신 상태는 두 문서를 직접 확인할 것.

## 조직도

```
User (총사령관, 최종 컨펌)
 └── EVA (Claude Cowork, 오케스트레이터)
      ├── AXEL (Claude Code, bash 실행 + 로직 설계)
      │    ├── FORGE (qwen3-coder:30b, 코드/UI 구현)
      │    └── VANCE (qwen3-30b-32k, 문서/범용 실무)
      ├── NEXUS (보조 Cowork, 계획 수립 + 스케줄링)
      └── ORACLE (deepseek-r1:70b, 고난이도 추론 — 단독 동기 호출만)
```

## 역할별 담당

| 에이전트 | 담당 | 금지 사항 |
|---|---|---|
| EVA | 요구사항 명세화, 에이전트 할당, 컨펌 체인 관리 | 코드 직접 작성 금지 |
| AXEL | bash 실행, 로직 설계, FORGE/VANCE에 명세 위임 | 직접 구현 금지 (명세 전달만) |
| FORGE | 코드/UI 구현 (속도 우선) | — |
| VANCE | 문서 작성, 이메일, 분석 (균형형 32K ctx) | — |
| NEXUS | 계획 수립, 스케줄링 (보조 Cowork) | — |
| ORACLE | 복잡한 추론, 아키텍처 결정, 심층 분석 | **동시 다중 호출 절대 금지** (순차 실행만) |

## 컨펌 체인

```
FORGE/VANCE/ORACLE (구현)
  → AXEL/NEXUS (1차 검증)
    → EVA (2차 컨펌 + 사용자 보고)
      → User (최종 승인)
```

## ORACLE 호출 규칙 (중요)

- **병렬 호출 절대 금지** — 과거 동시 다중 호출로 메모리 부족(OOM)·처리 지연/블로킹 사고가 있었음. 반드시 한 번에 하나씩 순차 실행.
- 호출 전 시스템/GPU 메모리 여유를 확인할 것.
- VANCE/서브에이전트로 해결 가능한 작업이면 ORACLE을 쓰지 말 것 — 사전에 대체 가능 여부를 점검.

## 세션 위생

- 새 세션 시작 전 동일 작업에 대해 이미 실행 중인 세션이 없는지 먼저 확인 (재사용 vs 신규 판단).
- 작업 종료 후 불필요한 세션은 정리.

## 참고 문서

- 구체적 역할명(EVA/AXEL 등)과 컨펌 체인: `docs/process/PROCESS_GUIDE.md`
- 위임 기준·ORACLE 규칙·세션 위생 원칙(일반화된 버전): `docs/process/AGENT_SYSTEM.md`
- 시각 자료: `docs/diagrams/agent-org-confirm-chain.md`, `docs/diagrams/session-management-flow.md`
