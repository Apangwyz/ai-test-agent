# 编码任务清单

**版本**: 1.0

**生成时间**: 2026-04-29 08:35:58

## 任务 1: **Task ID**: `CRYPTO-SM4-PDF`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 2: **Task Name**: Implement SM4-GCM encryption/decryption for PDF/A-3 documents using Alibaba Cloud KMS

**描述**: Build a reusable utility that encrypts/decrypts PDF/A-3 files using SM4-GCM (128-bit key) via Alibaba Cloud KMS API. Must validate PDF/A-3 conformance *before* encryption and preserve embedded metadata (XMP, digital signatures).

**优先级**: **p0** (foundational for document vault & pipl/gb/t 35273 compliance)

**预估时间**: 4

---

## 任务 3: **Task ID**: `CONSENT-PIPL-LIFECYCLE`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 4: **Task Name**: Build consent state machine with opt-in/opt-out/withdrawal tracking and audit logging

**描述**: Implement a consent service that enforces PIPL Art. 28–30: granular purpose-based consent, explicit opt-in (no pre-ticked), withdrawal = immediate revocation, immutable audit trail. Supports natural/juridical persons.

**优先级**: **p0** (regulatory non-negotiable; blocks customer master)

**预估时间**: 4

---

## 任务 5: **Task ID**: `CUSTOMER-UNIFIED-VIEW`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 6: **Task Name**: Design and implement schema + REST API for unified natural/juridical customer profiles

**描述**: Create a canonical customer model supporting both individual (natural) and corporate (juridical) entities in one schema. Includes mandatory fields per CBIRC §3.5 (UBO disclosure) and PIPL (data minimization).

**优先级**: **p0** (core domain model; prerequisite for all downstream modules)

**预估时间**: 4

---

## 任务 7: **Task ID**: `UBO-REFINITIV-STUB`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 8: **Task Name**: Implement lightweight UBO resolution service calling Refinitiv World-Check API

**描述**: Build a synchronous service that submits juridical customer data to Refinitiv World-Check API for PEP/Sanctions screening and returns resolved UBOs. Includes fallback handling and CBIRC §3.5-compliant result mapping.

**优先级**: **p1** (critical for cbirc §3.5; requires external api credentials)

**预估时间**: 4

---

## 任务 9: **Task ID**: `VAULT-DOC-STORAGE`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 10: **Task Name**: Build secure document upload/retrieval API for SM4-encrypted PDF/A-3 files

**描述**: Implement REST endpoints to store/retrieve customer documents (e.g., ID scans, incorporation docs) with end-to-end SM4 encryption, access control, and PIPL-compliant retention.

**优先级**: **p1** (directly enables customer master’s document vault requirement)

**预估时间**: 4

---

## 任务 11: **Task ID**: `ACK-DEPLOY-CORE`

**描述**: 

**优先级**: medium

**预估时间**: 4

---

## 任务 12: **Task Name**: Author Helm charts and K8s manifests for deploying core services on Alibaba ACK

**描述**: Package all above services (`consent`, `customer`, `vault`, `ubo`) as Helm charts

**优先级**: medium

**预估时间**: 4

---

