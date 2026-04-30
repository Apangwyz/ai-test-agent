# 编码任务清单

**版本**: 1.0

**生成时间**: 2026-04-29 08:35:58

## 任务 1: **Task ID**: `DB-001`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 2: **Task Name**: Initialize PostgreSQL 15 Financial Schema with ACID-Enforced Constraints

**描述**: Create a minimal but production-hardened PostgreSQL 15 schema for financial transactions, including tables for accounts, ledgers, and transfers — with explicit DDL enforcing atomicity, consistency, isolation, and durability (e.g., `SERIALIZABLE` isolation where needed, `CHECK` constraints, `NOT NULL`, foreign keys with `ON DELETE RESTRICT`, and `DEFERRABLE` constraints for complex invariants).

**优先级**: p0 (foundational — required before any financial operation)

**预估时间**: 4

---

## 任务 3: **Task ID**: `DB-002`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 4: **Task Name**: Implement Idempotent Transaction Ledger with ACID-Safe Upsert & Balance Validation

**描述**: Build a stored procedure (`ledger_post_transfer()`) that atomically records a transfer between two accounts *and* validates pre-transfer balances using `SELECT ... FOR UPDATE` and raises exception on insufficient funds — ensuring strict serializability without application-level locks. Includes unit tests via `pgTAP`.

**优先级**: p0 (core financial correctness guarantee)

**预估时间**: 4

---

## 任务 5: **Task ID**: `DB-003`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 6: **Task Name**: Containerize & Configure TiDB 7

**描述**: Provision a local 3-node TiDB 7.5 cluster (TiDB + TiKV + PD) using Docker Compose, configured for strong consistency (`tidb_txn_mode = 'optimistic'` + `tidb_enable_async_commit = ON`) and compatible with PostgreSQL schema subset (e.g., accounts/ledgers). Include health checks, backup script stub, and connection pooling via `tidb-server` config.

**优先级**: p1 (secondary datastore — enables scalability & analytics; not required for core acid writes)

**预估时间**: 4

---

## 任务 7: **Task ID**: `DB-004`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 8: **Task Name**: Build Cross-Database Schema Sync Utility (PostgreSQL ↔ OceanBase 4

**描述**: Develop a Python CLI tool (`db-sync`) that compares schema objects (tables, columns, constraints) between PostgreSQL 15 and OceanBase 4.3 (via OBProxy), reports compatibility gaps (e.g., `NUMERIC` precision limits, missing `DEFERRABLE`), and generates safe DDL translation patches (e.g., `TEXT` → `VARCHAR(1024)`). Uses `psycopg3` and `mysql-connector-python` (OceanBase uses MySQL protocol).

**优先级**: p1 (enables future multi-database operational flexibility; critical for vendor lock-in mitigation)

**预估时间**: 4

---

## 任务 9: **Task ID**: `DB-005`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 10: **Task Name**: Deploy ACID Compliance Test Harness for Financial Workloads

**描述**: Implement a concurrent stress test suite that validates ACID properties across all three databases under financial workload patterns:

**优先级**: p0 (final gate

**预估时间**: 4

---

