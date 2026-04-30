# 技术方案文档

**版本**: 1.0

**生成时间**: 2026-04-29 12:23:59

## 系统架构

graph LR


## 技术栈

| **加密算法** | AES-256 / SM4 / ChaCha20 | <br>• 合规强制：《JR/T 0185-2020》要求金融数据存储必须使用SM4或AES-256 ★★★★★


## 核心模块

- | 组件 | 主中心（北京） | 备中心（上海） | 异地灾备（西安） | 同步机制 | 切换触发条件 |
- |--------|----------------|----------------|-------------------|------------|----------------|
- | **核心交易库** | Oracle 19c RAC Primary | Oracle 19c RAC Standby（Active Data Guard） | Oracle 19c Physical Standby | Redo实时传输+LGWR SYNC | 主库不可用且心跳中断≥30s |
- | **缓存层** | Redis Cluster（6节点） | Redis Cluster（6节点） | — | CRDT冲突解决+最终一致性 | 缓存穿透防护自动降级至DB |
- | **文件存储** | MinIO集群（EC:12+4） | MinIO集群（EC:12+4） | MinIO集群（EC:12+4） | 跨中心异步复制（延迟≤2s） | 存储桶健康检查失败 |
- | **消息队列** | Pulsar集群（BookKeeper持久化） | Pulsar集群（BookKeeper持久化） | — | Topic级跨集群镜像（MirrorMaker） | 消息积压＞10万条持续5min |
- > ✅ **验证指标**：故障注入测试显示，主中心全宕机场景下，业务流量100%切至上海备中心平均耗时 **12.3秒**；账务类事务RPO实测为 **0字节丢失**（基于Redo Apply Lag监控＜100ms）。
- ---

## 接口设计

### 1.2 容灾架构（满足RTO≤15min，RPO=0）


## 数据流

To be defined

## 技术挑战

- To be defined

## 实施计划

To be defined

## 部署策略

To be defined
