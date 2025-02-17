from cs50 import get_int


def main():
    height = get_height()

    for i in range(1, height + 1):
        print(" " * (height - i), "#" * i, "  ", "#" * i, sep="")


def get_height():
    while True:
        n = get_int("Height: ")
        if n > 0 and n <= 8:
            return n


main()
