#include "helpers.h"
#include <stdio.h>

void colorize(int height, int width, RGBTRIPLE image[height][width])
{
    // Change all black pixels to a color of your choosing
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            RGBTRIPLE colors;
            colors = image[i][j];
            if (colors.rgbtBlue == 0x00 && colors.rgbtGreen == 0x00 && colors.rgbtRed == 0x00)
            {
                colors.rgbtBlue = 0x8A;
                colors.rgbtGreen = 0x2B;
                colors.rgbtRed = 0xE2;
                image[i][j] = colors;
            }
        }
    }
    return;
}
