#include <cs50.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    // Housekeeping
    if (argc != 2)
    {
        printf("Usage: recover infile\n");
        return 1;
    }

    // Filenames
    char *infile = argv[1];

    // Open Memory Card
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        printf("Could not open %s.\n", infile);
        return 4;
    }

    typedef uint8_t BYTE;
    BYTE buffer[512] = {0};
    int jpg_counter = 0;
    char *filename = malloc(8);
    FILE *img = NULL;

    // open initial output file

    // Read Memory Card in blocks of 512Bytes
    // Look for header signature

    while (fread(buffer, 1, 512, inptr) == 512)
    {
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {
            if (jpg_counter == 0)
            {
                sprintf(filename, "%03i.jpg", jpg_counter);
                img = fopen(filename, "w");
                if (img == NULL)
                {
                    printf("Could not create %s.\n", filename);
                    return 5;
                }
                fwrite(buffer, 1, 512, img);
            }
            else
            {
                fclose(img);
                sprintf(filename, "%03i.jpg", jpg_counter);
                img = fopen(filename, "w");
                if (img == NULL)
                {
                    printf("Could not create %s.\n", filename);
                    return 5;
                }
                fwrite(buffer, 1, 512, img);
            }
            jpg_counter++;
        }
        else
        {
            if (img != NULL)
            {
                fwrite(buffer, 1, 512, img);
            }
        }
    }

    fclose(img);
    fclose(inptr);
    free(filename);
}
