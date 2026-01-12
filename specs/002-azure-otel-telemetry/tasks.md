# Tasks: Azure Monitor OpenTelemetry Integration

**Input**: Design documents from `/specs/002-azure-otel-telemetry/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Not explicitly requested in the feature specification—basic telemetry module tests included for coverage.

**Organization**: Tasks grouped by user story (P1 → P2 → P3) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Remove deprecated dependencies and add new SDK across both projects

- [X] T001 [P] Update backend/pyproject.toml: remove `opencensus-ext-azure>=1.1.13`, add `azure-monitor-opentelemetry>=1.0.0`
- [X] T002 [P] Update frontend/pyproject.toml: remove `opencensus-ext-azure>=1.1.13`, add `azure-monitor-opentelemetry>=1.0.0`
- [X] T003 Run `uv sync` in backend/ to update lock file and install dependencies
- [X] T004 Run `uv sync` in frontend/ to update lock file and install dependencies

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infrastructure configuration required for ALL user stories

**⚠️ CRITICAL**: Telemetry environment variables must be in place before any user story can emit telemetry

- [X] T005 Update infrastructure/modules/app_service/main.tf: add `OTEL_SERVICE_NAME=azure-service-catalog-backend` to backend app_settings
- [X] T006 Update infrastructure/modules/app_service/main.tf: add `OTEL_SERVICE_NAME=azure-service-catalog-frontend` to frontend app_settings
- [X] T007 Run `terraform plan` to verify infrastructure changes in infrastructure/
- [X] T008 Update backend/.env.example with OTEL_SERVICE_NAME and APPLICATIONINSIGHTS_CONNECTION_STRING
- [X] T009 Update frontend/.env.example with OTEL_SERVICE_NAME and APPLICATIONINSIGHTS_CONNECTION_STRING

**Checkpoint**: Foundation ready—user story implementation can begin

---

## Phase 3: User Story 1 - Backend API Telemetry (Priority: P1) 🎯 MVP

**Goal**: FastAPI backend sends telemetry to Application Insights with cloud role name "azure-service-catalog-backend"

**Independent Test**: Deploy backend, call GET /api/v1/services, verify traces in App Insights with correct cloud role

### Implementation for User Story 1

- [X] T010 [US1] Create backend/src/telemetry.py with `configure_telemetry()` function using `configure_azure_monitor(enable_live_metrics=True, sampling_ratio=1.0)`
- [X] T011 [US1] Update backend/src/main.py: remove ALL OpenCensus imports (lines 30-51)
- [X] T012 [US1] Update backend/src/main.py: import and call `configure_telemetry()` at module top BEFORE FastAPI imports
- [X] T013 [US1] Update backend/src/main.py: update logger namespace to use structured logging compatible with OpenTelemetry
- [X] T014 [P] [US1] Create backend/tests/unit/test_telemetry.py with tests for configure_telemetry() function
- [X] T015 [US1] Run backend tests: `cd backend && uv run pytest tests/unit/test_telemetry.py -v`
- [X] T016 [US1] Verify backend starts locally: `cd backend && uv run uvicorn src.main:app --reload`
- [X] T017 [US1] Update backend/pyproject.toml coverage exclusions: remove opencensus lines, add telemetry graceful degradation

**Checkpoint**: Backend telemetry functional—verify in App Insights Application Map

---

## Phase 4: User Story 2 - Frontend Streamlit Telemetry (Priority: P2)

**Goal**: Streamlit frontend sends telemetry with cloud role name "azure-service-catalog-frontend"

**Independent Test**: Deploy frontend, navigate UI, verify traces in App Insights with frontend cloud role and backend connection

### Implementation for User Story 2

- [X] T018 [US2] Create frontend/src/telemetry.py with `configure_telemetry()` function (same pattern as backend)
- [X] T019 [US2] Update frontend/src/app.py: remove ALL OpenCensus imports (lines 24-37)
- [X] T020 [US2] Update frontend/src/app.py: import and call `configure_telemetry()` BEFORE streamlit import
- [X] T021 [US2] Update frontend/src/app.py: ensure logging uses structured format compatible with OpenTelemetry
- [X] T022 [P] [US2] Create frontend/tests/test_telemetry.py with tests for configure_telemetry() function
- [X] T023 [US2] Run frontend tests: `cd frontend && uv run pytest tests/test_telemetry.py -v`
- [X] T024 [US2] Verify frontend starts locally: `cd frontend && uv run streamlit run src/app.py --server.headless true`

**Checkpoint**: Frontend telemetry functional—Application Map shows both nodes with connection

---

## Phase 5: User Story 3 - Storage Layer Telemetry (Priority: P3)

**Goal**: Storage operations instrumented with custom spans showing operation type and duration

**Independent Test**: Perform CRUD via API, verify storage.* spans appear as children in App Insights traces

### Implementation for User Story 3

- [X] T025 [US3] Update backend/src/services/storage.py: add OpenTelemetry tracer import `from opentelemetry import trace`
- [X] T026 [US3] Update backend/src/services/storage.py: create module-level tracer `tracer = trace.get_tracer(__name__)`
- [X] T027 [US3] Instrument `list_services()` in LocalFileStorageAdapter with span "storage.list_services" and attributes
- [X] T028 [US3] Instrument `get_service()` in LocalFileStorageAdapter with span "storage.get_service" and service_name attribute
- [X] T029 [US3] Instrument `create_service()` in LocalFileStorageAdapter with span "storage.create_service"
- [X] T030 [US3] Instrument `update_service()` in LocalFileStorageAdapter with span "storage.update_service"
- [X] T031 [US3] Instrument `delete_service()` in LocalFileStorageAdapter with span "storage.delete_service"
- [X] T032 [US3] Instrument AzureBlobStorageAdapter methods with matching spans (list, get, create, update, delete)
- [X] T033 [US3] Add span error handling: mark spans as failed on exceptions with error details
- [X] T034 [US3] Run full backend test suite: `cd backend && uv run pytest -v`

**Checkpoint**: Storage spans visible in App Insights traces as children of HTTP request spans

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and deployment

- [X] T035 [P] Update backend/README.md with telemetry configuration section
- [X] T036 [P] Update frontend/README.md with telemetry configuration section
- [ ] T037 Apply Terraform changes: `cd infrastructure && terraform apply`
- [ ] T038 Deploy backend to Azure: `./scripts/deploy.sh` (backend portion)
- [ ] T039 Deploy frontend to Azure: `./scripts/deploy.sh` (frontend portion)
- [ ] T040 Validate quickstart.md: verify all commands and steps work as documented
- [ ] T041 Verify Application Map shows two distinct nodes (frontend, backend) in Azure Portal
- [ ] T042 Verify end-to-end traces from frontend through backend to storage in Transaction Search
- [ ] T043 Verify exceptions captured in Failures view with full stack traces
- [X] T044 Run `grep -r "opencensus" backend/ frontend/` to confirm zero OpenCensus references remain

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies—can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion—BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational—MVP delivery point
- **User Story 2 (Phase 4)**: Depends on Foundational—can run parallel to US1
- **User Story 3 (Phase 5)**: Depends on User Story 1 (backend telemetry must be working)
- **Polish (Phase 6)**: Depends on all user stories

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (Backend Telemetry) | Foundational | US2 |
| US2 (Frontend Telemetry) | Foundational | US1 |
| US3 (Storage Spans) | US1 | - |

### Within Each User Story

1. Telemetry module creation first
2. Remove old OpenCensus code
3. Integrate new telemetry
4. Test locally
5. Story checkpoint validation

### Parallel Opportunities

```bash
# Phase 1 - all parallel:
T001, T002  # Update both pyproject.toml files simultaneously

# Phase 2 - Terraform updates parallel:
T005, T006  # Both app_settings changes in same file but different blocks

# Phase 3 & 4 - User Stories 1 & 2 can run in parallel:
# Developer A: T010-T017 (Backend)
# Developer B: T018-T024 (Frontend)

# Phase 6 - Documentation parallel:
T035, T036  # Both README updates
```

---

## Parallel Example: User Stories 1 & 2

```bash
# Two developers can work simultaneously after Foundational phase:

# Developer A (US1 - Backend):
Task: T010 Create backend/src/telemetry.py
Task: T011 Remove OpenCensus from backend/src/main.py
Task: T012 Integrate configure_telemetry() in backend
Task: T014 Create backend/tests/unit/test_telemetry.py

# Developer B (US2 - Frontend):
Task: T018 Create frontend/src/telemetry.py
Task: T019 Remove OpenCensus from frontend/src/app.py
Task: T020 Integrate configure_telemetry() in frontend
Task: T022 Create frontend/tests/test_telemetry.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T009)
3. Complete Phase 3: User Story 1 (T010-T017)
4. **STOP and VALIDATE**: Backend telemetry in App Insights
5. Deploy backend only if needed

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Backend Telemetry) → Deploy → **MVP with backend observability**
3. Add US2 (Frontend Telemetry) → Deploy → **Full distributed tracing**
4. Add US3 (Storage Spans) → Deploy → **Complete observability**
5. Polish phase → Final validation

### Single Developer Strategy (Sequential)

1. T001-T009: Setup + Foundational
2. T010-T017: User Story 1 (Backend)
3. T018-T024: User Story 2 (Frontend)
4. T025-T034: User Story 3 (Storage)
5. T035-T044: Polish & Validation

---

## Notes

- All telemetry modules use identical `configure_telemetry()` pattern
- `OTEL_SERVICE_NAME` environment variable sets cloud role (no code changes needed for renaming)
- OpenCensus removal is complete replacement—no migration path, no coexistence
- Storage spans (US3) build on backend telemetry (US1)—cannot be done in isolation
- SC-006 success criteria: `grep -r "opencensus"` returns zero results
