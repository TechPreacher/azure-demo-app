# Tasks: Initial App Infrastructure

**Input**: Design documents from `/specs/001-initial-app-infrastructure/`
**Prerequisites**: plan.md ✅, spec.md ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and basic structure

- [X] T001 Create root project structure with backend/, frontend/, infrastructure/, data/, scripts/ directories
- [X] T002 [P] Initialize backend Python project with uv in backend/pyproject.toml (FastAPI, Pydantic, uvicorn, azure-storage-blob, opencensus-ext-azure, httpx)
- [X] T003 [P] Initialize frontend Python project with uv in frontend/pyproject.toml (Streamlit, httpx, opencensus-ext-azure)
- [X] T004 [P] Copy services.json to data/services.json as default seed data
- [X] T005 [P] Create README.md with project overview and local development instructions
- [X] T006 [P] Create scripts/dev.sh for local development startup
- [X] T007 [P] Create scripts/test.sh for running all tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core backend infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create backend configuration module in backend/src/config.py (environment variables, storage type selection)
- [X] T009 [P] Create Service Pydantic model in backend/src/models/service.py
- [X] T010 Create storage adapter interface in backend/src/services/storage.py (abstract base class)
- [X] T011 Implement LocalFileStorageAdapter in backend/src/services/storage.py (reads/writes data/services.json)
- [X] T012 Implement AzureBlobStorageAdapter in backend/src/services/storage.py (reads/writes Azure Blob)
- [X] T013 Create storage factory function in backend/src/services/storage.py (selects adapter based on STORAGE_TYPE)
- [X] T014 [P] Create FastAPI dependencies in backend/src/api/dependencies.py (storage dependency injection)
- [X] T015 Create FastAPI main app in backend/src/main.py with CORS, health endpoint, and structured logging
- [X] T016 [P] Create pytest configuration in backend/tests/conftest.py with fixtures for test storage
- [X] T017 [P] Create frontend configuration in frontend/src/config.py (API base URL)
- [X] T018 [P] Create frontend API client in frontend/src/api_client.py (httpx client with error handling)
- [X] T019 Create Streamlit main app skeleton in frontend/src/app.py (page config, layout structure)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 5 - Deploy Infrastructure (Priority: P1) 🎯 MVP-Foundation

**Goal**: Provision all Azure resources using Terraform so the application can be deployed

**Independent Test**: Run `terraform apply` and verify all resources are created in Azure portal

### Implementation for User Story 5

- [X] T020 [P] [US5] Create Terraform providers configuration in infrastructure/providers.tf (azurerm provider)
- [X] T021 [P] [US5] Create Terraform variables in infrastructure/variables.tf (environment, location, resource names)
- [X] T022 [US5] Create resource group module in infrastructure/modules/resource_group/main.tf
- [X] T023 [US5] Create storage account module in infrastructure/modules/storage/main.tf (blob container for services.json)
- [X] T024 [US5] Create Application Insights module in infrastructure/modules/monitoring/main.tf
- [X] T025 [US5] Create App Service module in infrastructure/modules/app_service/main.tf (plan + 2 app services)
- [X] T026 [US5] Create main Terraform configuration in infrastructure/main.tf (compose all modules)
- [X] T027 [US5] Create Terraform outputs in infrastructure/outputs.tf (URLs, connection strings)
- [X] T028 [US5] Add Terraform deployment instructions to README.md

**Checkpoint**: Infrastructure can be deployed independently with `terraform apply`

---

## Phase 4: User Story 1 - View Azure Services (Priority: P1) 🎯 MVP

**Goal**: Users can browse the Azure service catalog through a web interface

**Independent Test**: Open http://localhost:8501, see list of Azure services displayed in a table

### Tests for User Story 1

- [X] T029 [P] [US1] Unit test for storage service list_services() in backend/tests/unit/test_storage.py
- [X] T030 [P] [US1] Integration test for GET /api/v1/services endpoint in backend/tests/integration/test_api.py
- [X] T031 [P] [US1] Test for API client get_services() in frontend/tests/test_api_client.py

### Implementation for User Story 1

- [X] T032 [US1] Implement list_services() in storage adapters in backend/src/services/storage.py
- [X] T033 [US1] Implement get_service_by_name() in storage adapters in backend/src/services/storage.py
- [X] T034 [US1] Create API routes file in backend/src/api/routes.py with router setup
- [X] T035 [US1] Implement GET /api/v1/services endpoint in backend/src/api/routes.py
- [X] T036 [US1] Implement GET /api/v1/services/{service_name} endpoint in backend/src/api/routes.py
- [X] T037 [US1] Register routes in backend/src/main.py
- [X] T038 [US1] Create service list component in frontend/src/components/service_list.py (table display)
- [X] T039 [US1] Create filter component in frontend/src/components/filters.py (search by name/category)
- [X] T040 [US1] Integrate list and filter components in frontend/src/app.py
- [X] T041 [US1] Add loading states and error handling to frontend views

**Checkpoint**: User Story 1 complete - users can view and search Azure services

---

## Phase 5: User Story 2 - Create New Azure Service (Priority: P2)

**Goal**: Users can add new Azure services to the catalog

**Independent Test**: Fill in service form, submit, see new service appear in the list

### Tests for User Story 2

- [X] T042 [P] [US2] Unit test for storage service create_service() in backend/tests/unit/test_storage.py
- [X] T043 [P] [US2] Integration test for POST /api/v1/services endpoint in backend/tests/integration/test_api.py
- [X] T044 [P] [US2] Test for API client create_service() in frontend/tests/test_api_client.py

### Implementation for User Story 2

- [X] T045 [US2] Implement create_service() in storage adapters in backend/src/services/storage.py
- [X] T046 [US2] Add duplicate service name validation in create_service()
- [X] T047 [US2] Implement POST /api/v1/services endpoint in backend/src/api/routes.py
- [X] T048 [US2] Create service form component in frontend/src/components/service_form.py (create mode)
- [X] T049 [US2] Integrate create form in frontend/src/app.py with success/error feedback

**Checkpoint**: User Story 2 complete - users can create new services

---

## Phase 6: User Story 3 - Update Existing Azure Service (Priority: P3)

**Goal**: Users can modify existing Azure services

**Independent Test**: Select a service, edit its description, save, verify changes persist

### Tests for User Story 3

- [X] T050 [P] [US3] Unit test for storage service update_service() in backend/tests/unit/test_storage.py
- [X] T051 [P] [US3] Integration test for PUT /api/v1/services/{name} endpoint in backend/tests/integration/test_api.py
- [X] T052 [P] [US3] Test for API client update_service() in frontend/tests/test_api_client.py

### Implementation for User Story 3

- [X] T053 [US3] Implement update_service() in storage adapters in backend/src/services/storage.py
- [X] T054 [US3] Implement PUT /api/v1/services/{service_name} endpoint in backend/src/api/routes.py
- [X] T055 [US3] Add edit mode to service form component in frontend/src/components/service_form.py
- [X] T056 [US3] Add edit button and modal trigger to service list in frontend/src/components/service_list.py
- [X] T057 [US3] Integrate edit workflow in frontend/src/app.py

**Checkpoint**: User Story 3 complete - users can edit services

---

## Phase 7: User Story 4 - Delete Azure Service (Priority: P4)

**Goal**: Users can remove Azure services from the catalog

**Independent Test**: Select a service, click delete, confirm, verify service is removed

### Tests for User Story 4

- [X] T058 [P] [US4] Unit test for storage service delete_service() in backend/tests/unit/test_storage.py
- [X] T059 [P] [US4] Integration test for DELETE /api/v1/services/{name} endpoint in backend/tests/integration/test_api.py
- [X] T060 [P] [US4] Test for API client delete_service() in frontend/tests/test_api_client.py

### Implementation for User Story 4

- [X] T061 [US4] Implement delete_service() in storage adapters in backend/src/services/storage.py
- [X] T062 [US4] Implement DELETE /api/v1/services/{service_name} endpoint in backend/src/api/routes.py
- [X] T063 [US4] Add delete button with confirmation dialog to service list in frontend/src/components/service_list.py
- [X] T064 [US4] Integrate delete workflow in frontend/src/app.py

**Checkpoint**: User Story 4 complete - full CRUD functionality available

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T065 [P] Add OpenAPI schema validation contract test in backend/tests/contract/test_openapi.py
- [X] T066 [P] Configure pytest-cov and add coverage reporting in backend/pyproject.toml
- [X] T067 [P] Add Application Insights integration to backend in backend/src/main.py
- [X] T068 [P] Add Application Insights integration to frontend in frontend/src/app.py
- [X] T069 [P] Add correlation ID logging middleware in backend/src/main.py
- [X] T070 Update README.md with complete documentation (setup, testing, deployment)
- [X] T071 Run full test suite and verify 80% coverage threshold
- [X] T072 Test local development workflow end-to-end

**Checkpoint**: Phase 8 complete - all polish tasks done

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 5 (Phase 3)**: Can run in parallel with Phase 2 (infrastructure is independent)
- **User Stories 1-4 (Phases 4-7)**: All depend on Phase 2 completion
- **Polish (Phase 8)**: Depends on desired user stories being complete

### User Story Dependencies

| Story | Priority | Depends On | Can Parallelize With |
|-------|----------|------------|---------------------|
| US5 (Infrastructure) | P1 | Phase 1 only | Phase 2, all others |
| US1 (View) | P1 | Phase 2 | US5 |
| US2 (Create) | P2 | Phase 2, builds on US1 | US5 |
| US3 (Update) | P3 | Phase 2, builds on US1 | US5 |
| US4 (Delete) | P4 | Phase 2, builds on US1 | US5 |

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Backend storage methods before API endpoints
3. API endpoints before frontend components
4. Frontend components before integration

### Parallel Opportunities

```bash
# Phase 1 - all parallel:
T002, T003, T004, T005, T006, T007

# Phase 2 - some parallel:
T009, T014, T016, T017, T018 can run in parallel after T008

# Phase 3 (US5) - can run entirely in parallel with Phase 2:
T020, T021 parallel, then T022-T027 sequential (module dependencies)

# Phase 4+ - tests can be parallel within each story:
T029, T030, T031 parallel (US1 tests)
T042, T043, T044 parallel (US2 tests)
```

---

## Implementation Strategy

### MVP First (US1 + US5)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (backend/frontend infrastructure)
3. Complete Phase 3: US5 Infrastructure (can be parallel with Phase 2)
4. Complete Phase 4: US1 View Services
5. **VALIDATE**: Test locally, deploy to Azure, demo read-only catalog

### Incremental Delivery

| Milestone | Stories Complete | Value Delivered |
|-----------|-----------------|-----------------|
| MVP | US1 + US5 | Browse Azure service catalog |
| v1.1 | + US2 | Add new services |
| v1.2 | + US3 | Edit existing services |
| v1.0 | + US4 + Polish | Full CRUD, production-ready |

---

## Notes

- All tasks include exact file paths based on plan.md structure
- [P] tasks can run in parallel (different files, no dependencies)
- [Story] labels enable filtering tasks by user story
- Tests are included as specified in FR-022 through FR-029
- Local development prioritized (FR-021a, FR-021b, FR-021c)
- Commit after each task or logical group
