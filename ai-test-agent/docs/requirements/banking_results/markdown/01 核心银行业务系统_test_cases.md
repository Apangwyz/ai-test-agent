# 测试案例文档

**版本**: 1.0

**生成时间**: 2026-04-29 08:35:58

## 测试案例

### 1. Submit POST `/api/v1/customers` with natural person payload: `{ "name": "Zhang San", "idCardNo": "11010119900307271X", "mobile": "+8613800138000", "consent": {"optIn": true, "purpose": ["KYC", "marketing"], "validUntil": "2027-06-15"} }`

- **类型**: functional
- **优先级**: medium
- **测试环境**: Standard test environment

**测试步骤**:

**预期结果**:

---

### 2. Verify system generates unique `customerID` and `consentID`

- **类型**: functional
- **优先级**: high
- **测试环境**: - Staging environment with live SM4 HSM (e.g., Huawei Cloud KMS or Zhongchuang SM4 module);

**测试步骤**:
  

**预期结果**:
  - 

---

### 1. Submit POST `/api/v1/customers` with juridical payload: `{ "legalName": "Shanghai Tech Co

- **类型**: functional
- **优先级**: medium
- **测试环境**: Standard test environment

**测试步骤**:

**预期结果**:

---

### 2. Trigger UBO resolution engine manually via `/api/v1/customers/{id}/resolve-ubo`

- **类型**: functional
- **优先级**: critical
- **测试环境**: 

**测试步骤**:
  

**预期结果**:
  - 

---

### 1. Create customer with consent (as in TC-CM-FUNC-001)

- **类型**: functional
- **优先级**: medium
- **测试环境**: Standard test environment

**测试步骤**:

**预期结果**:

---

### 2. PATCH `/api

- **类型**: functional
- **优先级**: medium
- **测试环境**: Standard test environment

**测试步骤**:

**预期结果**:

---

