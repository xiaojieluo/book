def fab(max):
    a = 1
    print("hello")
    a += 1
    yield a

if __name__ == '__main__':
    for k in fab(5):
        print(k)

    for v in fab(6):
        print(v)
