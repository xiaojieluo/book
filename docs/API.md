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


# 查询
## 基础查询
通过发送一个 GET 请求到类的 URL 上，不需要任何 URL 参数，你就可以一次获取多个对象。下面就是简单地获取所有微博：

```shell
curl -X GET \
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz" \
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl" \
  -H "Content-Type: application/json" \
  https://api.leancloud.cn/1.1/users
```
返回的值就是一个 JSON 对象包含了 results 字段，它的值就是对象的列表：
```json
{
  "results": [
    {
      "username": "llnhhy",
      "nickname": "llnhhys",
      "phone": "1234",
      "email": "",
      "age": 18,
      "tasks": [],
      "emailVerified": false,
      "mobilePhoneVerified": false,
      "createdAt": "2017-08-16T00:18:03.521000",
      "updatedAt": "2017-08-16T08:16:41.680744",
      "objectid": "59938f3b565b2731b01d513f"
    },
    {
      "username": "llnhhys",
      "phone": "",
      "email": "",
      "age": 18,
      "tasks": [],
      "emailVerified": false,
      "mobilePhoneVerified": false,
      "createdAt": "2017-08-16T08:28:06.206000",
      "updatedAt": "2017-08-16T08:28:06.206000",
      "objectid": "59940216565b27140f2b19e7"
    }
  ]
}
```
注：应用控制台对 createdAt 和 updatedAt 做了在展示优化，它们会依据用户操作系统时区而显示为本地时间；客户端 SDK 获取到这些时间后也会将其转换为本地时间；而通过 REST API 获取到的则是原始的 UTC 时间，开发者可能需要根据情况做相应的时区转换。

## 查询约束
通过 `where` 参数的形式可以对查询对象做出约束。

`where` 参数的值应该是 JSON 编码过的。就是说，如果你查看真正被发出的 URL 请求，它应该是先被 JSON 编码过，然后又被 URL 编码过。最简单的使用 `where` 参数的方式就是包含应有的 key 和 value。例如，如果我们想要看到「LeanCloud官方客服」发布的所有微博，我们应该这样构造查询:

```shell
curl -X GET \
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz" \
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl" \
  -H "Content-Type: application/json" \
  -G \
  --data-urlencode 'where={"pubUser":"LeanCloud官方客服"}' \
  https://api.leancloud.cn/1.1/classes/Post
```

除了完全匹配一个给定的值以外，`where` 也支持比较的方式，而且它还支持对 key 的一些 hash 操作，比如包含。`where` 参数支持如下选项：

Key | Operatopn
--- | ---------
$ne | 不等于
$lt | 小于
$lte | 小于等于
$gt | 大于
$gte | 大于等于
$regex | 正则表达式。$options指定 [全局修饰符](./)
$in | 包含任意一个数组值
$nin | 不包含任意一个数组值
$all | 包括所有数组值
$exists | 指定 key 有值
$select | 匹配另一个查询的返回值
$dontSelect | 排除另一个查询的返回值

例如获取在 2015-06-29 当天发布的微博：

```shell
curl -X GET
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz"
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl"
  -H "Content-Type: application/json"
  -G
  --data-urlencode 'where={"createdAt":{"$gte":{"__type":"Date","iso":"2015-06-29T00:00:00.000Z"},"$lt":{"__type":"Date","iso":"2015-06-30T00:00:00.000Z"}}}'
  https://api.leancloud.cn/1.1/classes/Post
```

求点赞次数少于 10 次，且该次数还是奇数的微博：
```shell
curl -X GET
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz"
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl"
  -H "Content-Type: application/json"
  -G
  --data-urlencode 'where={"upvotes":{"$in":[1,3,5,7,9]}}'
  https://api.leancloud.cn/1.1/classes/Post
```

获取不是「LeanCloud官方客服」发布的微博：
```shell
curl -X GET
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz"
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl"
  -H "Content-Type: application/json"
  -G
  --data-urlencode 'where={"pubUser":{"$nin":["LeanCloud官方客服"]}}'
  https://api.leancloud.cn/1.1/classes/Post
```

获取有人喜欢的微博：
```shell
curl -X GET
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz"
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl"
  -H "Content-Type: application/json"
  -G
  --data-urlencode 'where={"upvotes":{"$exists":true}}'
  https://api.leancloud.cn/1.1/classes/Post
```

获取没有被人喜欢过的微博：
```shell
curl -X GET
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz"
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl"
  -H "Content-Type: application/json"
  -G
  --data-urlencode 'where={"upvotes":{"$exists":false}}'
  https://api.leancloud.cn/1.1/classes/Post
```

微博有用户互相关注的功能，如果我们用 `_Followee`（用户关注的人） 和 `_Follower`（用户的粉丝） 这两个类来存储用户之间的关注关系（我们的 应用内社交组件 已经实现了这样的模型），我们可以创建一个查询来找到某个用户关注的人发布的微博（Post 表中有一个字段 author 指向发布者）：
```shell
curl -X GET
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz"
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl"
  -H "Content-Type: application/json"
  -G \
  --data-urlencode 'where={
    "author": {
      "$select": {
        "query": {
          "className":"_Followee",
           "where": {
             "user":{
               "__type": "Pointer",
               "className": "_User",
               "objectId": "55a39634e4b0ed48f0c1845c"
             }
           }
        },
        "key":"followee"
      }
    }
  }'
  https://api.leancloud.cn/1.1/classes/Post
```

order 参数指定一个字段的排序方式，前面加一个负号表示逆序。返回 Post 记录并按发布时间升序排列：
```shell
curl -X GET \
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz" \
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl" \
  -G \
  --data-urlencode 'order=createdAt' \
  https://api.leancloud.cn/1.1/classes/Post
```

降序排列：
```shell
curl -X GET \
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz" \
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl" \
  -G \
  --data-urlencode 'order=-createdAt' \
  https://api.leancloud.cn/1.1/classes/Post
```

对多个字段进行排序，要使用逗号分隔的列表。将 Post 以 createdAt 升序和 pubUser 降序进行排序：
```shell
curl -X GET \
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz" \
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl" \
  -G \
  --data-urlencode 'order=createdAt,-pubUser' \
  https://api.leancloud.cn/1.1/classes/Post
```

你可以用 `limit` 和 `skip` `来做分页。limit` 的默认值是 100，任何 1 到 1000 之间的值都是可选的，在 1 到 1000 范围之外的都强制转成默认的 100。比如为了获取排序在 400 到 600 之间的微博：
```shell
curl -X GET \
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz" \
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl" \
  -G \
  --data-urlencode 'limit=200' \
  --data-urlencode 'skip=400' \
  https://api.leancloud.cn/1.1/classes/Post
```

你可以限定返回的字段通过传入 `keys` 参数和一个逗号分隔列表。为了返回对象只包含 `pubUser` 和 `content` 字段（还有特殊的内置字段比如 `objectId`、`createdAt` 和 `updatedAt` ）：
```shell
curl -X GET \
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz" \
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl" \
  -G \
  --data-urlencode 'keys=pubUser,content' \
  https://api.leancloud.cn/1.1/classes/Post
```

`keys` 还支持反向选择，也就是不返回某些字段，字段名前面加个减号即可，比如我不想查询返回 `author` :
```shell
curl -X GET \
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz" \
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl" \
  -G \
  --data-urlencode 'keys=-author' \
  https://api.leancloud.cn/1.1/classes/Post
```

## 正则查询
获取标题以大写「WTO」开头的微博：
```shell
curl -X GET \
  -H "X-LC-Id: LjJDgnBwYAEqXk0dqz5Cm1nI-gzGzoHsz" \
  -H "X-LC-Key: HHyoOtOJJParOKJ3Bj0n9XHl" \
  -H "Content-Type: application/json" \
  -G \
  --data-urlencode 'where={"title":{"$regex":"^WTO.*","$options":"i"}}' \
  https://api.leancloud.cn/1.1/classes/Post
```

我们使用以下数据来演示如何使用 `$options` 匹配 title 字段值：
```json
{ "_id" : 100, "title" : "Single line description." },
{ "_id" : 101, "title" : "First line\nSecond line" },
{ "_id" : 102, "title" : "Many spaces before     line" },
{ "_id" : 103, "title" : "Multiple\nline description" },
{ "_id" : 103, "title" : "abc123" }
```

参数 | 说明 | 示例
--- | ---  | ---
i | *忽略大小写* | `{"$regex":"single", "$options":"i"}` 将匹配<br /> `{ "_id" : 100, "title" : "Single line description." }`
m | *多行匹配*<br />比如文本中包含了换行符 \n | `{"$regex":"^S", "$options":"m"}`（以大写字母 S 开头）将匹配 <br/> `{ "_id" : 100, "title" : "Single line description." },{ "_id" : 101, "title" : "First line\nSecond line" }`
x | *忽略空白字符*<br/>包括空格、tab、\n、# 注释等，但对 vertical tab（ASCII 码为 11）无效。 | `{"$regex":"abc #category code\n123 #item number", "$options":"x"}`（# 后面为注释）将匹配 <br/><br/>`{ "_id" : 103, "title" : "abc123" }`
s | *允许 . 匹配任意字符和换行* | `{"$regex":"m.*line", "$options":"si"}` 将匹配  | `{ "_id" : 102, "title" : "Many spaces before line" },{ "_id" : 103, "title" : "Multiple\nline description" }`

以上参数可以组合使用，如 `"$options":"sixm"`。
