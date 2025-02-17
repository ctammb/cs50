#include <cs50.h>
#include <stdio.h>

int main(void)
{
    // Prompt for height
    int n = 0;
    while (n < 1 || n > 8)
    {
        n = get_int("Height? ");
    }

    // Print hashes
    for (int j = 1; j <= n; j++)
    {
        for (int i = 0; i < (n - j); i++)
        {
            printf(" ");
        }
        for (int i = 0; i < j; i++)
        {
            printf("#");
        }
        printf("  ");
        for (int i = 0; i < j; i++)
        {
            printf("#");
        }
        printf("\n");
    }
}
