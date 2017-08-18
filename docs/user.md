# 用户

## 注册
注册一个新用户与创建一个新的普通对象之间的不同点在于 username 和 password 字段都是必需的。password 字段会以和其他的字段不一样的方式处理，它在储存时会被加密而且永远不会被返回给任何来自客户端的请求。
+

你可以让 LeanCloud 自动验证邮件地址，做法是进入 控制台 > 设置 > 应用选项，勾选 用户账号 下的 用户注册时，发送验证邮件。
+

这项设置启用了的话，所有填写了 email 的用户在注册时都会产生一个 email 验证地址，并发回到用户邮箱，用户打开邮箱点击了验证链接之后，用户表里 emailVerified 属性值会被设为 true。你可以在 emailVerified 字段上查看用户的 email 是否已经通过验证。
+

为了注册一个新的用户，需要向 user 路径发送一个 POST 请求，你可以加入一个新的字段，例如，创建一个新的用户有一个电话号码:

```shell
curl -X POST \
  -H "X-LC-Id: {{appid}}" \
  -H "X-LC-Key: {{appkey}}" \
  -H "Content-Type: application/json" \
  -d '{"username":"hjiang","password":"f32@ds*@&dsa","phone":"18612340000"}' \
  https://api.leancloud.cn/1.1/users
```

当创建成功时，HTTP返回为 201 Created，Location 头包含了新用户的 URL：

```shell
Status: 201 Created
Location: https://api.leancloud.cn/1.1/users/55a47496e4b05001a7732c5f
```

返回的主体是一个 JSON 对象，包含 objectId、createdAt 时间戳表示创建对象时间，sessionToken 可以被用来认证这名用户随后的请求：

```json
{
  "sessionToken":"qmdj8pdidnmyzp0c7yqil91oc",
  "createdAt":"2015-07-14T02:31:50.100Z",
  "objectId":"55a47496e4b05001a7732c5f"
}
```

## 帐号锁定
输入错误的密码或验证码会导致用户登录失败。如果在 15 分钟内，同一个用户登录失败的次数大于 6 次，该用户账户即被云端暂时锁定，此时云端会返回错误码 {"code":219,"error":"登录失败次数超过限制，请稍候再试，或者通过忘记密码重设密码。"}，开发者可在客户端进行必要提示。

锁定将在最后一次登录错误的15分钟之后由云端自动解除，开发者无法通过 SDK 或 REST API 进行干预。在锁定期间，即使用户输入了正确的验证信息也不允许登录。这个限制在 SDK 和云引擎中都有效。

## 使用手机号注册
see [短信验证 API](./SMS_API.md)
TODO

## 验证 Email
TODO

## 请求验证 Email
TODO

## 获取用户
你可以发送一个 GET 请求到 URL 以获取用户的账户信息，返回的内容就是当创建用户时返回的内容。比如，为了获取上面创建的用户:

```shell
curl -X GET \
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz" \
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl" \
  https://api.leancloud.cn/1.1/users/55a47496e4b05001a7732c5f
```
返回的 body 是一个 JSON 对象，只有一个 updatedAt 字段表明更新发生的时间.

```shell
{
  "updatedAt": "2015-07-14T02:35:50.100Z"
}
```

## 安全地修改用户密码
修改密码，可以直接使用上面的PUT /1.1/users/:objectId的 API，但是很多开发者会希望让用户输入一次旧密码做一次认证，旧密码正确才可以修改为新密码，因此我们提供了一个单独的 API PUT /1.1/users/:objectId/updatePassword 来安全地更新密码：

```shell
curl -X PUT
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz"
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl"
  -H "X-LC-Session: qmdj8pdidnmyzp0c7yqil91oc"
  -H "Content-Type: application/json"
  -d '{"old_password":"the_old_password", "new_password":"the_new_password"}'
  https://api.leancloud.cn/1.1/users/55a47496e4b05001a7732c5f/updatePassword
```

* old_password：用户的老密码
* new_password：用户的新密码

注意：仍然需要传入 X-LC-Session，也就是登录用户才可以修改自己的密码。

## 查询

你可以一次获取多个用户，只要向用户的根 URL 发送一个 GET 请求。没有任何 URL 参数的话，可以简单地列出所有用户：
```shell
curl -X GET \
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz" \
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl" \
  https://api.leancloud.cn/1.1/users
```

返回的值是一个 JSON 对象包括一个 results 字段，值是包含了所有对象的一个 JSON 数组。
```json
{
  "results":[
    {
      "updatedAt":"2015-07-14T02:31:50.100Z",
      "phone":"18612340000",
      "objectId":"55a47496e4b05001a7732c5f",
      "username":"hjiang",
      "createdAt":"2015-07-14T02:31:50.100Z",
      "emailVerified":false,
      "mobilePhoneVerified":false
    }
  ]
}
```

所有的对普通对象的查询选项都适用于对用户对象的查询，所以可以查看 查询 部分来获取详细信息。

## 删除用户
为了在 LeanCloud 上删除一个用户，可以向它的 URL 上发送一个 DELETE 请求。同样的，你必须提供一个 X-LC-Session 在 HTTP 头上以便认证。例如：
```shell
curl -X DELETE \
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz" \
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl" \
  -H "X-LC-Session: qmdj8pdidnmyzp0c7yqil91oc" \
  https://api.leancloud.cn/1.1/users/55a47496e4b05001a7732c5f
```
