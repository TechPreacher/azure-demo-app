# Contracts: Azure Monitor OpenTelemetry Integration

This feature does not introduce API changes.

Telemetry is a cross-cutting concern that instruments existing APIs without modifying their contracts.

## Existing Contracts (Unchanged)

- Backend REST API: `/api/v1/services` endpoints remain unchanged
- Frontend-Backend communication: Same HTTP requests

## Telemetry Contracts

Telemetry data follows OpenTelemetry semantic conventions exported to Azure Monitor:

- **Traces**: W3C Trace Context format
- **Logs**: Correlated with trace context
- **Metrics**: Auto-collected by Azure Monitor SDK

See [data-model.md](../data-model.md) for telemetry entity definitions.
