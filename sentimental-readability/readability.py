from cs50 import get_string


index = 0


def main():
    words = get_string("Text: ")
    counts(words)


def counts(words):
    print(len(words))
    letter_count = 0
    word_count = 1
    sentence_count = 0
    for i in words:
        print(i)
        if i.isalpha():
            letter_count += 1
        elif i == " ":
            word_count += 1
        elif i == "." or i == "?" or i == "!":
            sentence_count += 1
    print(letter_count, word_count, sentence_count)
    indices(letter_count, word_count, sentence_count)


def indices(letter_count, word_count, sentence_count):
    index = (
        5.88 * (letter_count / word_count) - (29.6 * sentence_count / word_count) - 15.8
    )
    grade = round(index)
    print_grade(grade)


def print_grade(grade):
    if grade >= 1 and grade <= 16:
        print("Grade ", grade)
    elif grade < 1:
        print("Before Grade 1\n")
    elif grade > 16:
        print("Grade 16+\n")


main()
