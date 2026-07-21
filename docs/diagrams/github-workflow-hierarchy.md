---
title: GitHub 프로젝트 관리 계층 흐름
date: 2026-07
status: draft
---

이 문서는 GitHub 프로젝트 관리 계층(Project → Milestone → Issue → Task)과 이슈 생명주기, release-please 자동화 흐름을 시각화한 교육 자료입니다.

```mermaid
flowchart TD
    Project["Project (VinylStage 전체)"] --> Milestone["Milestone (레포별 릴리스, 예: v0.3.0)"]
    Milestone --> Issue["Issue ([feat]/[fix]/[docs] 접두사)"]
    Issue --> Task["Task (Issue 내 체크리스트 하위 작업)"]
    
    Issue --> Create["생성 (배경/재현방법 또는 요구사항/완료기준 포함)"]
    Create --> Work["작업 진행"]
    Work --> Complete["완료기준 충족"]
    Complete --> Link["Milestone에 연결 (종료)"]
    
    Work --> Conventional["Conventional Commits (feat/fix/docs)"]
    Conventional --> ReleasePlease["release-please"]
    ReleasePlease --> ReleasePR["릴리스 PR 생성"]
    ReleasePR --> Merge["PR 머지"]
    Merge --> Changelog["CHANGELOG.md/버전 태그 갱신"]
```

GitHub 프로젝트 관리 계층은 VinylStage 조직 전체 Project에서 레포별 Milestone, 기능/버그 단위 Issue, 체크리스트 Task로 계층화되며, 이슈는 생성 → 작업 진행 → 완료기준 충족 → Milestone 연결의 생명주기를 거칩니다. Conventional Commits 규칙 준수 시 release-please가 릴리스 PR을 자동 생성해 CHANGELOG와 버전 태그를 갱신합니다.
