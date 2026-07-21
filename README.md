# little-jotjotsaw-base

A shared knowledge base for VinylStage's side projects, containing cross-project documentation, troubleshooting logs, and AI assistant operating guides. **This is not an application code repository**—it holds no executable code, only documentation to prevent repeated problem-solving across projects.

This repository is read and updated by VinylStage (the owner) and Claude Code sessions working in sibling project repositories (e.g., `finance-tracker`, `discord-mcp-alert`). It enables teams to reference prior incidents, conventions, and agent workflows instead of re-solving the same problems.

## Repository Structure
```
├── README.md                 # This file (current document)
├── CLAUDE.md                 # Guide for Claude Code on how to interact with this repo
├── docs/                     # Core documentation
│   ├── DOCUMENT_GUIDE.md     # Contribution conventions (naming, structure, metadata)
│   ├── process/              # Development process standards
│   │   ├── PROCESS_GUIDE.md  # Common dev process across projects
│   │   ├── AGENT_SYSTEM.md   # Agent delegation rules & session hygiene
│   │   └── GITHUB_WORKFLOW.md# GitHub Project/Milestone/Issue conventions
│   ├── troubleshooting/      # Incident logs
│   │   ├── INDEX.md          # Index of all troubleshooting entries
│   │   └── 2026-07-finance-tracker.md # Example dated incident log
│   └── projects/             # Project overviews
│       ├── finance-tracker/OVERVIEW.md
│       └── discord-mcp-alert/OVERVIEW.md
```

## How to Use This Repo
- **For human owners**: Reference `docs/` for project conventions, troubleshooting, and process guides.
- **For Claude Code sessions**: Follow the operating rules in [`CLAUDE.md`](CLAUDE.md) before updating or searching this repo.
- **To contribute**: Adhere to conventions in [`docs/DOCUMENT_GUIDE.md`](docs/DOCUMENT_GUIDE.md).

## Conventions at a Glance
- **English README**: This file is in English for clarity in GitHub.
- **Korean internal docs**: All content in `docs/` (e.g., `OVERVIEW.md`, `PROCESS_GUIDE.md`) is written in Korean for VinylStage’s internal use.  
  *Example: `finance-tracker/OVERVIEW.md` contains Korean technical summaries.*

## Ownership & License
Private personal knowledge base for VinylStage. **Not for external contribution or public use.**
