# 编码任务清单

**版本**: 1.0

**生成时间**: 2026-04-29 08:35:58

## 任务 1: **Task ID**: `AUDIT-JFR-SIGN-001`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 2: **Task Name**: Enable cryptographically signed JFR recordings for audit log metadata per CBIRC 2022-8 §4

**描述**: Configure Spring Boot 3.2 (Java 17) to emit JFR recordings with SHA-256+RSA-2048 signatures embedded in recording metadata, ensuring tamper-evident audit trails for all transactional and authorization events.

**优先级**: 🔴 **p0 (critical)** — directly satisfies cbirc 2022-8 §4.2.3

**预估时间**: 4

---

## 任务 3: **Task ID**: `PIPL-CONSENT-002`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 4: **Task Name**: Build granular, revocable, purpose-limited consent scopes using Spring Security OAuth2 Resource Server

**描述**: Extend Spring Security to enforce dynamic, user-granted consent scopes (e.g., `card:balance:read`, `transaction:history:export`) with audit logging of grant/revocation, expiry, and PIPL-required purpose justification.

**优先级**: 🔴 **p0 (critical)** — required for pipl article 13–14 compliance

**预估时间**: 4

---

## 任务 5: **Task ID**: `DATA-CASS-003`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 6: **Task Name**: Create immutable, TTL-governed Cassandra tables for hotlist records and consent audits per CBIRC 2020-12 §3

**描述**: Define CQL schema for `hotlist_records` (card PAN + reason + timestamp) and `consent_audit_log` with `USING TTL = 155520000` (5 years), `default_time_to_live = 0`, and `compaction = {'class': 'TimeWindowCompactionStrategy'}`. Enforce immutability via application-layer write-only DAO.

**优先级**: 🟠 **p1 (high)** — core to cbirc 2020-12 §3.1 & scalability requirement

**预估时间**: 4.0

---

## 任务 7: **Task ID**: `INTG-KAFKA-SINK-004`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 8: **Task Name**: Deploy and configure Debezium-based Kafka sink to replicate hotlist updates from PostgreSQL 15 → Cassandra 5

**描述**: Implement CDC pipeline: PostgreSQL `hotlist_events` table → Kafka topic `hotlist.updates` → Cassandra `hotlist_records`. Use Kafka Connect with `cassandra-sink-connector` v2.5.0, configured for idempotent writes and tombstone handling.

**优先级**: medium

**预估时间**: 8

---

## 任务 9: **Task ID**: `DATA-PG-005`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 10: **Task Name**: Create and optimize `hotlist_events` table in PostgreSQL 15 for low-latency lookups (<5s @ 10B+ rows) per CBIRC 2020-12

**描述**: Design partitioned, indexed table for PAN-based hotlist queries: range-partition by `created_at`, BRIN index on `pan_hash`, GIN index on `reason_codes`, and covering index for `SELECT status WHERE pan_hash = ? AND created_at > ?`.

**优先级**: medium

**预估时间**: 4

---

