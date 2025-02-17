#include <cs50.h>
#include <stdio.h>

int main(void)
{
    // Prompt for input
    long card;
    long n;
    string type;
    bool valid = false;
    while (valid == false)
    {
        int count = 0;
        card = get_long("Enter valid card number: ");
        n = card;
        long n2 = n;
        long n1 = n;
        while (n != 0)
        {
            n2 = n1;
            n1 = n;
            n = n / 10;
            count++;
        }
        if ((count == 15) && ((n2 == 34) || (n2 == 37)))
        {
            type = "AMEX";
            valid = true;
        }
        else
        {
            if (((count == 16) || (count == 13)) && (n1 == 4))
            {
                type = "VISA";
                valid = true;
            }
            else
            {
                if ((count == 16) && ((n2 > 50) && (n2 < 56)))
                {
                    type = "MASTERCARD";
                    valid = true;
                }
                else
                {
                    printf("INVALID\n");
                    return (0);
                }
            }
        }
    }
    // Calculate Checksum
    int checksum = 0;
    long remainder = 0;
    long remainder1 = 0;
    long remainder2 = 0;
    int count = 0;
    n = card;
    while (n != 0)
    {
        remainder = n % 10;
        count = count + 1;
        if (count % 2 == 0)
        {
            remainder = remainder * 2;
            if (remainder < 10)
            {
                checksum = checksum + remainder;
            }
            else
            {
                remainder1 = remainder / 10;
                remainder2 = remainder % 10;
                checksum = checksum + remainder1 + remainder2;
            }
        }
        else
        {
            checksum = checksum + remainder;
        }
        n = n / 10;
    }
    if (checksum % 10 == 0)
    {
        printf("%s\n", type);
        return (0);
    }
    else
    {
        printf("INVALID\n");
        return (0);
    }
}
