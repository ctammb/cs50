#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

int compute_level(string phrase);

int main(void)
{
    // Get phrase
    string phrase = get_string("Enter passage: ");
    // printf("Text: %s\n", phrase);

    // Compute index
    int grade_level = compute_level(phrase);

    // Print Grade Level

    if (grade_level >= 1 && grade_level <= 16)
    {
        printf("Grade %i\n", grade_level);
    }
    else
    {
        if (grade_level < 1)
        {
            printf("Before Grade 1\n");
        }
        else
        {
            printf("Grade 16+\n");
        }
    }
}

int compute_level(string phrase)
{
    // Compute grade_level index

    float index = 0;
    int index_round = 0;
    int L = 0;
    int W = 0;
    int S = 0;

    for (int i = 0, n = strlen(phrase); i < n; i++)
    {
        int j = phrase[i];
        if (j >= 65 && j <= 122)
        {
            L = L + 1;
        }
        else
        {
            if (j == 32)
            {
                W = W + 1;
            }
            else
            {
                if (j == 46 || j == 33 || j == 63)
                {
                    S = S + 1;
                    if (i == n - 1)
                    {
                        W = W + 1;
                    }
                }
                else
                {
                    //                printf("Unidentifiable character \n");
                }
            }
        }
    }

    // printf("%i letters\n", L);
    // printf("%i words\n", W);
    // printf("%i sentences\n",S);
    index = (5.88 * L / W) - (29.6 * S / W) - 15.8;
    index_round = round(index);

    // printf("%f index\n", index);
    return index_round;
}
