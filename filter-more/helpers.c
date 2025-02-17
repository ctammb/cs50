#include "helpers.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    float floatGray = 0;
    int gray = 0;
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            floatGray = (image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed) / 3.0;
            gray = round(floatGray);
            image[i][j].rgbtBlue = gray;
            image[i][j].rgbtGreen = gray;
            image[i][j].rgbtRed = gray;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE colors[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            colors[i][j] = image[i][width - j - 1];
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {

            image[i][j] = colors[i][j];
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE blur[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            blur[i][j] = image[i][j];
            int colorRed = 0;
            int colorBlue = 0;
            int colorGreen = 0;
            float block_count = 0;
            float doubleBlue = 0;
            float doubleGreen = 0;
            float doubleRed = 0;

            for (int k = -1; k < 2; k++)
            {
                if (i + k >= 0 && i + k < height)
                {
                    for (int l = -1; l < 2; l++)
                    {
                        if (j + l >= 0 && j + l < width)
                        {
                            colorBlue += image[i + k][j + l].rgbtBlue;
                            colorGreen += image[i + k][j + l].rgbtGreen;
                            colorRed += image[i + k][j + l].rgbtRed;
                            block_count++;
                            // printf("i= %i , j= %i , k= %i , l= %i, colors: %i, %i, %i, block: %i\n", i, j, k, l, colorBlue,
                            // colorGreen, colorRed, block_count);
                        }
                    }
                }
            }

            doubleBlue = colorBlue / block_count;
            blur[i][j].rgbtBlue = round(doubleBlue);
            doubleGreen = colorGreen / block_count;
            blur[i][j].rgbtGreen = round(doubleGreen);
            doubleRed = colorRed / block_count;
            blur[i][j].rgbtRed = round(doubleRed);
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j] = blur[i][j];
        }
    }
    return;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    typedef struct
    {
        double rgbtBlue;
        double rgbtGreen;
        double rgbtRed;
    } __attribute__((__packed__)) RGBTRIPLE_double;

    RGBTRIPLE_double Gx[height][width];
    RGBTRIPLE_double Gy[height][width];

    int GxConst[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    int GyConst[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            float GxcolorRed = 0;
            float GxcolorBlue = 0;
            float GxcolorGreen = 0;
            float GycolorRed = 0;
            float GycolorBlue = 0;
            float GycolorGreen = 0;

            for (int k = -1; k < 2; k++)
            {
                if (i + k >= 0 && i + k < height)
                {
                    for (int l = -1; l < 2; l++)
                    {
                        if (j + l >= 0 && j + l < width)
                        {
                            GxcolorBlue = GxcolorBlue + ((GxConst[k + 1][l + 1]) * (image[i + k][j + l].rgbtBlue));
                            GxcolorGreen = GxcolorGreen + ((GxConst[k + 1][l + 1]) * (image[i + k][j + l].rgbtGreen));
                            GxcolorRed = GxcolorRed + ((GxConst[k + 1][l + 1]) * (image[i + k][j + l].rgbtRed));
                            GycolorBlue = GycolorBlue + ((GyConst[k + 1][l + 1]) * (image[i + k][j + l].rgbtBlue));
                            GycolorGreen = GycolorGreen + ((GyConst[k + 1][l + 1]) * (image[i + k][j + l].rgbtGreen));
                            GycolorRed = GycolorRed + ((GyConst[k + 1][l + 1]) * (image[i + k][j + l].rgbtRed));
                            // printf("i= %i , j= %i , k= %i , l= %i, colors: %i, %i, %i, %i, %i, %i\n", i, j, k, l, GxcolorBlue,
                            // GxcolorGreen, GxcolorRed, GycolorBlue, GycolorGreen, GycolorRed);
                        }
                    }
                }
            }

            Gx[i][j].rgbtBlue = round(GxcolorBlue);
            Gx[i][j].rgbtGreen = round(GxcolorGreen);
            Gx[i][j].rgbtRed = round(GxcolorRed);
            Gy[i][j].rgbtBlue = round(GycolorBlue);
            Gy[i][j].rgbtGreen = round(GycolorGreen);
            Gy[i][j].rgbtRed = round(GycolorRed);
            // printf("i= %i, j= %i, colors: %i, %i, %i, %i, %i, %i\n", i, j, GxcolorBlue, GxcolorGreen, GxcolorRed, GycolorBlue,
            // GycolorGreen, GycolorRed);
        }
    }
    float Blue = 0;
    float Green = 0;
    float Red = 0;
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            Blue = sqrt((Gx[i][j].rgbtBlue * Gx[i][j].rgbtBlue) + (Gy[i][j].rgbtBlue * Gy[i][j].rgbtBlue));
            if (Blue > 255)
            {
                Blue = 255;
            }
            image[i][j].rgbtBlue = round(Blue);
            // printf("Blue: %i\n", image[i][j].rgbtBlue);

            Green = sqrt((Gx[i][j].rgbtGreen * Gx[i][j].rgbtGreen) + (Gy[i][j].rgbtGreen * Gy[i][j].rgbtGreen));
            if (Green > 255)
            {
                Green = 255;
            }
            image[i][j].rgbtGreen = round(Green);
            // printf("Green: %i\n", image[i][j].rgbtGreen);

            Red = sqrt((Gx[i][j].rgbtRed * Gx[i][j].rgbtRed) + (Gy[i][j].rgbtRed * Gy[i][j].rgbtRed));
            if (Red > 255)
            {
                Red = 255;
            }
            image[i][j].rgbtRed = round(Red);
            // printf("Red: %i\n", image[i][j].rgbtRed);
        }
    }
    return;
}
