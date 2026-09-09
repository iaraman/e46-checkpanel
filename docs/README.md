# Documentation

| Path | What it is |
|------|-----------|
| `REQ-001-requirements.md` | Development requirements sheet. The controlling document — scope, functional and non-functional requirements, interface spec, signal decodes, verification plan, open questions |
| `reference/` | Primary-source captures from the project's own vehicles. Evidence behind the decode claims in REQ-001 §8 |

## Where things go

- **Requirements, design decisions, specs** → `docs/`
- **Raw captures, logs, screenshots, datasheets** → `docs/reference/`
- **Code** → `tools/` (host-side Python), firmware directory (embedded)
- **Test fixtures and sample data** → `sample_data/`

Reference material is append-only. Requirements are versioned in the revision history
table at the bottom of REQ-001 rather than by filename, so links don't rot.
