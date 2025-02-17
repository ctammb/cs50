// Implements a dictionary's functionality

#include "dictionary.h"
#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
} node;

// TODO: Choose number of buckets in hash table
const unsigned int N = 26;

// Hash table
node *table[N];

// Dictionary word count
int word_count = 0;

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    // TODO

    int hashInt = hash(word);
    node *nodecheck = table[hashInt];

    while (nodecheck != NULL)
    {
        if (strcasecmp(word, nodecheck->word) == 0)
        {
            return true;
        }
        else
        {
            nodecheck = nodecheck->next;
        }
    }
    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    // TODO: Improve this hash function

    char A = 'A';
    int i = 0;
    // printf("word = %s \n", word);
    // printf("word[0] = %c \n", word[0]);
    // printf("toupper(word[0]) = %c \n", toupper(word[0]));
    // printf("toupper(word[0]) = %c \n", (toupper(word[0] + 1)));
    for (i = 0; i < N; i++)
    {
        if (toupper(word[0]) == A + i)
        {
            return i;
        }
    }
    return i;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    // TODO
    // define dictionary word store
    char charArray[LENGTH + 1];

    // Open dictionary
    FILE *inptr = fopen(dictionary, "r");
    if (inptr == NULL)
    {
        printf("Could not open %s\n", dictionary);
        return false;
    }

    // Load words, allocating node memory dynamically
    while (fscanf(inptr, "%s", charArray) != EOF)
    {
        // printf("dictionary word = %s \n", charArray);
        node *n = malloc(sizeof(node));
        if (n == NULL)
        {
            printf("Not enough memory to store dictionary\n");
            fclose(inptr);
            return false;
        }
        strcpy(n->word, charArray);

        // Run Hash function
        int hashResult = hash(n->word);

        // Insert node
        if (table[hashResult] == NULL)
        {
            table[hashResult] = n;
            n->next = NULL;
        }
        else
        {
            n->next = table[hashResult];
            table[hashResult] = n;
        }
        word_count++;
    }
    fclose(inptr);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    // TODO
    if (word_count >= 1)
    {
        return word_count;
    }
    else
    {
        return 0;
    }
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    // TODO

    node *nodecheck = NULL;
    node *temp = NULL;
    for (int i = 0; i < N; i++)
    {
        nodecheck = table[i];
        temp = table[i];
        while (nodecheck != NULL)
        {
            nodecheck = nodecheck->next;
            free(temp);
            temp = nodecheck;
        }
    }
    return true;
}
