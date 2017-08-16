# mongoengine 使用指南

---

##  ListField
# 注意： 避免使用  dbrefs

```python
    class Task(Document):
        name = StringField()

    class User(Document):
        name = StringField()
        tasks = ListField(ReferenceField(Task))

    task = Task(name='give me a book')
    john = User(name="John")
    john.tasks.append(task)
    john.save()

    for user in User.objects:
        for task in user.tasks:
            print(task.id)

```
