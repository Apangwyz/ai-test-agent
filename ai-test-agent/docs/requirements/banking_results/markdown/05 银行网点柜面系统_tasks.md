# 编码任务清单

**版本**: 1.0

**生成时间**: 2026-04-29 08:35:58

## 任务 1: **Task ID**: `DB-01`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 2: **Task name**: Provision secure PostgreSQL 15 + TimescaleDB instance with encryption-at-rest and RLS skeleton

**描述**: Install PostgreSQL 15.5 + TimescaleDB 2.14 on Ubuntu 22.04 LTS; configure native `pgcrypto`, enable transparent data encryption (TDE) via `pg_tde` (or filesystem-level LUKS if `pg_tde` unavailable); define minimal RLS policies for tenant isolation (`branch_id` column required on all PII-audited tables).

**优先级**: **p0** (foundational data layer)

**预估时间**: 2.0

---

## 任务 3: **Task ID**: `DB-02`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 4: **Task name**: Implement TimescaleDB hypertable for GDPR/JR/T-compliant audit logging

**描述**: Create `audit_log` hypertable partitioned by `event_time` (1-day chunks); add compression policy (7-day retention); enforce JR/T 0171-2020 §6.4.3 via `data_minimization_trigger()` that strips non-essential fields (e.g., full biometric hash → salted SHA-256 truncated to 32 chars) before insert.

**优先级**: **p0**

**预估时间**: 1.0

---

## 任务 5: **Task ID**: `GW-01`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 6: **Task name**: Configure NGINX-based Edge Gateway to require and validate kiosk client certificates

**描述**: Deploy NGINX 1.24+ as reverse proxy; configure mTLS with CA-signed client certs issued per branch; reject requests missing `SSL_CLIENT_VERIFY: SUCCESS` or invalid `SSL_CLIENT_S_DN_CN` (must match registered branch ID regex `^BR-[0-9]{4}$`). Log validation failures to `audit_log`.

**优先级**: **p0**

**预估时间**: 4

---

## 任务 7: **Task ID**: `EDGE-01`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 8: **Task name**: Build Yocto Kirkstone (4

**描述**: Create custom Yocto layer (`meta-kiosk`) adding `chromium-ozone-wayland`, disabling screen blanking, enabling kiosk mode (`--kiosk --no-sandbox --disable-features=Translate,PasswordGeneration`), and auto-starting via `systemd` service (`kiosk.service`). Enforce read-only rootfs.

**优先级**: medium

**预估时间**: 8

---

## 任务 9: **Task ID**: `EDGE-02`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 10: **Task name**: Implement local SQLite policy engine enforcing offline PII/biometric residency rules

**描述**: Develop Python 3.11 CLI tool (`policy-engine.py`) that:

**优先级**: **p1**

**预估时间**: 4

---

## 任务 11: **Task ID**: `BACK-01`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 12: **Task name**: Build Python FastAPI service to auto-generate RLS policies per branch registration

**描述**: Create REST endpoint `POST /v1/branches` accepting `{ "branch_id": "BR-5678", "tenant_name": "Shanghai Branch" }`. Service:

**优先级**: medium

**预估时间**: 4

---

