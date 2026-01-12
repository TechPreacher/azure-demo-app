# Tasks: Telemetry Simulation Buttons

**Input**: Design documents from `/specs/003-telemetry-simulation-buttons/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[US1]**: User Story 1 - Simulate High Latency Response
- **[US2]**: User Story 2 - Simulate Server Error Response
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No setup tasks required - leverages existing project infrastructure

> This feature extends existing FastAPI backend and Streamlit frontend. No new project initialization needed.

**Checkpoint**: Proceed directly to Foundational phase

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared components that both user stories depend on

- [X] T001 Create simulation response models in backend/src/models/simulation.py
- [X] T002 Create simulation router module skeleton in backend/src/api/simulation.py
- [X] T003 Register simulation router in backend/src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Simulate High Latency Response (Priority: P1) 🎯 MVP

**Goal**: Add "Latency" button that triggers a 10-20 second backend delay with proper UI feedback

**Independent Test**: Click "Latency" button → see spinner → receive response after 10-20s → view trace in Application Insights

### Implementation for User Story 1

- [X] T004 [US1] Implement POST /api/v1/simulate/latency endpoint with async sleep in backend/src/api/simulation.py
- [X] T005 [US1] Add simulate_latency() method to API client in frontend/src/api_client.py
- [X] T006 [US1] Add "Latency" button with spinner to sidebar in frontend/src/app.py

**Checkpoint**: Latency simulation fully functional and independently testable

---

## Phase 4: User Story 2 - Simulate Server Error Response (Priority: P1)

**Goal**: Add "Error" button that triggers HTTP 500 with rotating realistic error messages

**Independent Test**: Click "Error" button → see error message displayed → view exception in Application Insights Failures

### Implementation for User Story 2

- [X] T007 [US2] Define ERROR_MESSAGES pool constant in backend/src/api/simulation.py
- [X] T008 [US2] Implement POST /api/v1/simulate/error endpoint with HTTPException in backend/src/api/simulation.py
- [X] T009 [US2] Add simulate_error() method to API client in frontend/src/api_client.py
- [X] T010 [US2] Add "Error" button with error display to sidebar in frontend/src/app.py

**Checkpoint**: Error simulation fully functional and independently testable

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and validation

- [X] T011 [P] Add simulation section header and styling to sidebar in frontend/src/app.py
- [ ] T012 Run quickstart.md validation steps to verify telemetry in Application Insights

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Skipped - existing infrastructure
- **Foundational (Phase 2)**: Must complete before user stories
- **User Story 1 (Phase 3)**: Depends on Foundational
- **User Story 2 (Phase 4)**: Depends on Foundational; can run in parallel with US1
- **Polish (Phase 5)**: Depends on both user stories complete

### Within Each Phase

```
Phase 2 (Foundational):
  T001 (models) ─┬─► T002 (router skeleton) ─► T003 (register router)
                 │
                 └─► Can start T002 after T001 creates response model

Phase 3 (User Story 1):
  T004 (backend endpoint) ─► T005 (API client) ─► T006 (frontend button)

Phase 4 (User Story 2):
  T007 (error messages) ─► T008 (backend endpoint) ─► T009 (API client) ─► T010 (frontend button)

Phase 5 (Polish):
  T011 [P] and T012 can run after both stories complete
```

### Parallel Opportunities

User Stories 1 and 2 can be developed in parallel once Foundational is complete:

```bash
# Developer A (User Story 1):
T004 → T005 → T006

# Developer B (User Story 2 - in parallel):
T007 → T008 → T009 → T010

# Note: T006 and T010 both modify frontend/src/app.py
# If parallel, coordinate to avoid merge conflicts (add buttons in separate commits)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (T001-T003)
2. Complete Phase 3: User Story 1 (T004-T006)
3. **STOP and VALIDATE**: Test latency button independently
4. Deploy/demo latency simulation

### Full Feature Delivery

1. Complete Phase 2: Foundational
2. Complete Phase 3: User Story 1 → Test independently
3. Complete Phase 4: User Story 2 → Test independently
4. Complete Phase 5: Polish
5. Final validation with Application Insights

---

## Notes

- Both user stories are P1 priority - implement both for complete feature
- T004 and T008 modify same file (simulation.py) - implement sequentially or coordinate
- T006 and T010 modify same file (app.py) - implement sequentially or coordinate
- T011 can be combined with T006/T010 if implementing sequentially
- No tests explicitly requested in spec - test tasks omitted per template guidance
