def verify_json(method):
    def wrapper(*args, **kw):
        print("verify_js")
        print(args[0])
        print(dir(args[0]))
        print(kw)
        return method(*args, **kw)

    return wrapper
