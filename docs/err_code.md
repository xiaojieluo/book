# 错误码详解

本文档列举出服务端和 SDK 返回的错误码及相应说明。

## 0
    * 信息： `(无)`
    * 含义 - WebSocket 正常关闭，可能发生在服务器重启，或本地网络异常的情况。SDK 会自动重连，无需人工干预。

## 100
    * 信息 - `The connection to the AVOS servers failed.`
    * 含义 - 无法建立 TCP 连接到服务器，通常是因为网络故障，或者我们服务器故障引起的

## 101
    * 信息 - `Object doesn't exist, or has an incorrect password.`
    * 含义 - 查询的 Class 不存在，或者要关联的 Pointer 对象不存在。
