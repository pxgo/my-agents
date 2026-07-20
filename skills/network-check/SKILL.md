---
name: network-check
description: 当出现网络问题（包括但不限于无法连接、超时、DNS 解析失败等）时使用此 skill。帮助诊断网络问题并提供代理配置等解决方案。
---

# 网络问题检查

## 1. 确认错误类型

根据错误信息判断：无法连接、超时、DNS 解析失败、TLS/SSL 错误、HTTP 状态码异常。

## 2. 设置代理

代理地址：`http://127.0.0.1:10801`

### Linux / macOS

```sh
export http_proxy=http://127.0.0.1:10801
export https_proxy=http://127.0.0.1:10801
```

### Windows (CMD)

```cmd
set http_proxy=http://127.0.0.1:10801
set https_proxy=http://127.0.0.1:10801
```

### Windows (PowerShell)

```powershell
$env:http_proxy="http://127.0.0.1:10801"
$env:https_proxy="http://127.0.0.1:10801"
```

## 3. 其他

- 确认代理软件（Clash、V2Ray 等）已在本地运行
- 检查 VPN、防火墙、URL 正确性、API Key 有效性