# Users 表

```json
{
    "objectid" : "主键索引",
    "name" : "用户名称 <string>",
    "nickname" : "昵称 <string>",
    "age" : "年龄 <int>",
    "tasks" : [
        {"id":"<tasks.objectid>"},
        {"id":"<tasks.objectid>"}
        "接取的任务 id, "
    ],
}
```


# Tasks 表

```json
{
    "objectid" : "主键索引",
    "name" : "名称 <string>",
    "desc" : "任务介绍 <string>",
    "tags" : "任务标签 <list>",
    "exp" : "完成任务获得的经验 <int>",
    "money" : "完成任务获得的奖励 <int>",
    "expire" : "任务的过期时间 <int>(秒数)",
    "expire_type" : "过期时间有两种，一种是自发布起到某一刻过期， 一种是接取任务后到某一刻过期 <int>(0:第一种， 1:第二种)",
    "status" : "任务当前的状态， 0:关闭， 1:正常, 2:已完成 <int>",
    "announcer" : " 任务发布者 objectid, <users.objectid>",
    "own" : "成功接取任务的用户 objectid, <users.objectid>",
    "comments" : [
        {
            "author":"评论者 id <ReferenceField>(objectid)",
            "content" : "评论内容 <StringField>",
            "voteup": "赞 <IntField>"
        },
        "<ListField>(DictField)"
    ]
}
```
