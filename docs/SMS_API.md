# 短信服务 API

## 短信验证

URL | HTTP | 功能
--- | ---- | ---
/requestSmsCode | POST | 请求发送短信验证码
/verifySmsCode/`<code>` | POST | 验证短信验证码

## 用户

URL | HTTP | 功能
--- | ---- | ---
/usersByMobilePhone | POSt | 使用手机号码注册或登录
/requestMobilePhoneVerify | POST | 请求发送用户手机号码验证短信
/verifyMobilePhone/`<code>` | POST | 使用「验证码」验证用户手机号码
/requestLoginSmsCode | POST | 请求发送手机号码短信登录验证码
/requestPasswordResetBySmsCode | POST | 请求发送手机短信验证码重置用户密码
/resetPasswordBySmsCode/`<code>` | PUT |  验证手机短信验证码并重置密码

## 请求和响应格式

详情可参考  REST API 文档的 请求格式 和 响应格式。

通常情况下，如果返回的 HTTP 状态码为 200、结果为 {} 则代表请求成功完成。
