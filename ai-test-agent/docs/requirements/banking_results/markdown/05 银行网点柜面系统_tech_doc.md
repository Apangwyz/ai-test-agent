# 技术方案文档

**版本**: 1.0

**生成时间**: 2026-04-29 08:35:58

## 系统架构

A[Front-End Kiosk Terminal] -->|HTTPS + Mutual TLS| B[Edge Gateway Cluster]


## 技术栈

| **Database** | **PostgreSQL 15 + TimescaleDB** | Row-level security, native encryption at rest (pgcrypto), time-series audit log optimization | MySQL: Lacks built-in row-level security for multi-tenant branch isolation | JR/T 0171-2020 §6.4.3 (data minimization enforcement) |


## 核心模块

- | Tier | Components | Location | Residency Requirement | Uptime SLA |
- |--------|------------|----------|-------------------------|-------------|
- | **Kiosk Edge** | Embedded Linux (Yocto), Chromium Kiosk Mode, Local Policy Engine, SQLite Offline DB | Branch Workstation (x86_64) | On-premises only; no cloud sync of PII/biometrics | N/A (local) |

## 接口设计

---


## 数据流

To be defined

## 技术挑战

- To be defined

## 实施计划

**Date**: 2024-10-25


## 部署策略

| **Compliance Sentinel** | • Real-time OFAC/UN/MOFC

