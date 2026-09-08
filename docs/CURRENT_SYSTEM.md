# TANGLE — Current System

## Version

v1.0-backend

## Purpose

TANGLE is an AI-powered financial reconciliation and investigation
engine designed to detect financial exceptions, investigate them,
assess risk, make decisions, and manage human review.

## Current Architecture

TANGLE currently consists of:

- Exception Detection
- AI Investigation
- Risk Assessment
- Decision Engine
- Review Management
- Case Lifecycle

## Agents

### exception_detector.py

Purpose:
Detect financial reconciliation exceptions.

### agent.py

Purpose:
Core investigation/agent logic.

### risk_engine.py

Purpose:
Assess risk associated with detected cases.

### decision_engine.py

Purpose:
Generate a decision based on investigation and risk information.

### review_manager.py

Purpose:
Manage cases requiring human review.

### case_lifecycle.py

Purpose:
Manage case status transitions.

### run_agent.py

Purpose:
Entry point for running the current TANGLE intelligence engine.

## Current Data

TANGLE currently works with synthetic financial datasets.

Primary datasets:

- Invoices
- Payments
- Bank transactions

## Current Database

Document current database implementation here.

## Current API

Document existing API endpoints here.

## Known Issues

Document known issues here.

## Current Limitations

Document current limitations here.

## Phase 0 Status

- [ ] Git repository created
- [ ] .gitignore configured
- [ ] v1.0-backend checkpoint created
- [ ] Dataset backup created
- [ ] Agents documented
- [ ] Database documented
- [ ] APIs documented
- [ ] Existing system tested