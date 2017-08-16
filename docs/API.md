# API 要求
* 使用 HTTPS
* 版本号放在 Header 中


# 请求格式

对于 POST 与 PUT 请求， 请求的主体必须是 JSON 格式， 而且 HTTP header 的 Content-Type 需要设置为 `application/json`

用户验证通过 HTTP Header 来进行，X-LC-Id 标明正在运行的是哪个应用， X-LC-Key 用来授权鉴定 endpoint:

```shell
curl -X PUT \
  -H "X-LC-Id: FFnN2hso42Wego3pWq4X5qlu" \
  -H "X-LC-Key: UtOCzqb67d3sN12Kts4URwy8" \
  -H "Content-Type: application/json" \
  -d '{"content": "更新一篇博客的内容"}' \
  https://api.leancloud.cn/1.1/classes/Post/558e20cbe4b060308e3eb36c
```

# 更安全的鉴权方式

我们还支持一种新的 API 鉴权方式，即在 HTTP header 中使用 X-LC-Sign 来代替 X-LC-Key，以降低 App Key 的泄露风险。例如：

```shell
curl -X PUT \
  -H "X-LC-Id: FFnN2hso42Wego3pWq4X5qlu" \
  -H "X-LC-Sign: d5bcbb897e19b2f6633c716dfdfaf9be,1453014943466" \
  -H "Content-Type: application/json" \
  -d '{"content": "在 HTTP header 中使用 X-LC-Sign 来更新一篇博客的内容"}' \
  https://api.leancloud.cn/1.1/classes/Post/558e20cbe4b060308e3eb36c
```

X-LC-Sign 的值是由 `sign,timestamp[,master]` 组成的字符串：

取值 | 约束 | 描述
--- | ---  | ---
sign | 必须 | 将 timestamp 加上 App Key 或 Master Key 组成的字符串，再对它做 MD5 签名后的结果。
timestamp | 必须 | 客户端产生本次请求的 unix 时间戳（UTC），精确到毫秒。
master | 可选 | 字符串 `"master"`，当使用 master key 签名请求的时候，必须加上这个后缀明确说明是使用 master key。

举例来说，假设应用的信息如下：

Key | Value
--- | ---
App Id | FFnN2hso42Wego3pWq4X5qlu
App Key	| UtOCzqb67d3sN12Kts4URwy8
Master Key | DyJegPlemooo4X1tg94gQkw1
请求时间	| 2016-01-17 15:15:43.466
timestamp |	1453014943466

**使用 App Key 来计算 sign：**
    > md5( timestamp + App Key )
    >    = md5( 1453014943466UtOCzqb67d3sN12Kts4URwy8 )
    >    = d5bcbb897e19b2f6633c716dfdfaf9be

```shell
-H "X-LC-Sign: d5bcbb897e19b2f6633c716dfdfaf9be,1453014943466" \
```

**使用 Master Key 来计算 sign：**

    > md5( timestamp + Master Key )
    >    = md5( 1453014943466DyJegPlemooo4X1tg94gQkw1 )
    >    = e074720658078c898aa0d4b1b82bdf4b

```shell
-H "X-LC-Sign: e074720658078c898aa0d4b1b82bdf4b,1453014943466,master" \
```
（最后加上 master 来告诉服务器这个签名是使用 master key 生成的。）
> 使用 master key 将绕过所有权限校验，应该确保只在可控环境中使用，比如自行开发的管理平台，并且要完全避免泄露。因此，以上两种计算 sign 的方法可以根据实际情况来选择一种使用。

# 响应格式
对于所有的请求，响应格式都是一个 JSON 对象。

一个请求是否成功是由 HTTP 状态码标明的。一个 2XX 的状态码表示成功，而一个 4XX 表示请求失败。当一个请求失败时响应的主体仍然是一个 JSON 对象，但是总是会包含 code 和 error 这两个字段，你可以用它们来进行调试。举个例子，如果尝试用非法的属性名来保存一个对象会得到如下信息：

```json
{
  "code": 105,
  "error": "invalid field name: bl!ng"
}
```
错误代码请看 [错误代码详解](./err_code.md)



# 对象

## 对象格式

假如我们要实现一个类似于微博的社交 App，主要有三类数据：账户、帖子、评论，一条微博帖子可能包含下面几个属性：

```json
{
  "content": "每个 Java 程序员必备的 8 个开发工具",
  "pubUser": "LeanCloud官方客服",
  "pubTimestamp": 1435541999
}
```
Key（属性名）必须是字母和数字组成的字符串，Value（属性值）可以是任何可以 JSON 编码的数据。

每个对象都有一个类名，你可以通过类名来区分不同的数据。例如，我们可以把微博的帖子对象称之为 Post。我们建议将类和属性名分别按照 NameYourClassesLikeThis 和 nameYourKeysLikeThis 这样的惯例来命名，即区分第一个字母的大小写，这样可以提高代码的可读性和可维护性。

当你从服务器中获取对象时，一些字段会被自动加上，如 createdAt、updatedAt 和 objectId。这些字段的名字是保留的，值也不允许修改。我们上面设置的对象在获取时应该是下面的样子：

```json
{
  "content": "每个 Java 程序员必备的 8 个开发工具",
  "pubUser": "官方客服",
  "pubTimestamp": 1435541999,
  "createdAt": "2015-06-29T01:39:35.931Z",
  "updatedAt": "2015-06-29T01:39:35.931Z",
  "objectId": "558e20cbe4b060308e3eb36c"
}
```

createdAt 和 updatedAt 都是 UTC 时间戳，以 ISO 8601 标准和毫秒级精度储存：YYYY-MM-DDTHH:MM:SS.MMMZ。objectId 是一个字符串，在类中可以唯一标识一个实例。 在 REST API 中，class 级的操作都是通过一个带类名的资源路径（URL）来标识的。例如，如果类名是 Post，那么 class 的 URL 就是：

## 对象 HTTP 方法

URL | HTTP | 功能
--- | ---- | ---
/classes/`<className>` | GET | 查询对象
/classes/`<className>` | POST | 创建对象
/classes/`<className>`/`<objectId>` | GET | 获取对象
/classes/`<className>`/`<objectId>` | PUT | 更新对象
/cloudQuery | GET | 使用 CQL 查询对象
/classes/`<className>`/`<objectId>` | DELETE | 删除对象
/scan/classes/`<className>` | GET | 按照特定顺序遍历 Class

# 用户
URL | HTTP | 功能
--- | ---- | ---
/users | POST | 用户注册<br />用户连接
/users | GET | 查询用户
/users/`<objectId>` | GEt | 获取用户
/users/`<objectId>` | POST | 更新用户<br />用户连接<br />验证 Email
/users/`<objectId>` | DELETE | 删除用户
/usersByMobilePhone | POST | 使用手机号码登录或者注册
/login | POST | 用户登录
/users/me | GET | 根据 sessionToken 获取用户信息
/users/`<objectId>`/refreshSessionToken | PUT | 重置用户 sessionToken
/users/`<objectId>`/updatePassword      | PUT | 更新密码，要求输入旧密码
/requestPasswordReset | POST | 请求密码重设
/requestEmailVerify   | POST | 请求验证用户邮箱
/requestMobilePhoneVerify   | POST | 请求发送用户手机号码验证短信
/verifyMobilePhone/`<code>`    | POST | 使用"验证码"验证用户手机号码
/requestLoginSmsCode | POST | 请求发送手机号码登录短信。
/requestPasswordResetBySmsCode | POST | 请求发送手机短信验证码重置用户密码。
/resetPasswordBySmsCode/`<code>` | PUT  | 验证手机短信验证码并重置密码。
