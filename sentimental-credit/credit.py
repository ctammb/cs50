from cs50 import get_string


def main():
    card = get_string("Number: ")
    n = int(card)
    if check_sum(card):
        if len(card) == 15 and (
            card.startswith("34") == True or card.startswith("37") == True
        ):
            print("AMEX\n")
        elif (len(card) == 13 or len(card) == 16) and card.startswith("4") == True:
            print("VISA\n")
        elif len(card) == 16 and (n > (50 * 10**14) and n < (56 * 10**14)):
            print("MASTERCARD\n")
        else:
            print("INVALID\n")
    else:
        print("INVALID\n")


def check_sum(card):
    double_sum = 0
    pure_sum = sum(int(i) for i in card[len(card) - 1 :: -2])
    for i in card[len(card) - 2 :: -2]:
        temp_sum = 2 * int(i)
        temp_string = str(temp_sum)
        # print(i, temp_sum, temp_string)
        if len(temp_string) == 2:
            temp_sum = int(temp_string[0]) + int(temp_string[1])
        double_sum = double_sum + temp_sum
    checksum = pure_sum + double_sum
    # print(pure_sum, double_sum, checksum)
    if checksum % 10 == 0:
        return 1
    else:
        return 0


main()
