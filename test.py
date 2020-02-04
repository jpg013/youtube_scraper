
def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1

if __name__ == "__main__":
    gen = infinite_sequence()
    print(next(gen))
    print(next(gen))
    print(next(gen))
    print(next(gen))
    print(next(gen))
    print(next(gen))
    # main()
