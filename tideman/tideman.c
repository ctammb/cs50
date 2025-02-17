#include <cs50.h>
#include <stdio.h>
#include <string.h>

// Max number of candidates
#define MAX 9

// preferences[i][j] is number of voters who prefer i over j
int preferences[MAX][MAX];

// locked[i][j] means i is locked in over j
bool locked[MAX][MAX];

// Each pair has a winner, loser
typedef struct
{
    int winner;
    int loser;
} pair;

// Array of candidates
string candidates[MAX];
pair pairs[MAX * (MAX - 1) / 2];

int pair_count;
int candidate_count;

// Function prototypes
bool vote(int rank, string name, int ranks[]);
void record_preferences(int ranks[]);
void add_pairs(void);
void sort_pairs(void);
void lock_pairs(void);
void print_winner(void);

int main(int argc, string argv[])
{
    // Check for invalid usage
    if (argc < 2)
    {
        printf("Usage: tideman [candidate ...]\n");
        return 1;
    }

    // Populate array of candidates
    candidate_count = argc - 1;
    if (candidate_count > MAX)
    {
        printf("Maximum number of candidates is %i\n", MAX);
        return 2;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        candidates[i] = argv[i + 1];
        // printf("Candidates: %s\n", candidates[i]);
    }

    // Clear graph of locked in pairs
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = 0; j < candidate_count; j++)
        {
            locked[i][j] = false;
        }
    }

    pair_count = 0;
    int voter_count = get_int("Number of voters: ");

    // Query for votes
    for (int i = 0; i < voter_count; i++)
    {
        // ranks[i] is voter's ith preference
        int ranks[candidate_count];

        // Query for each rank
        for (int j = 0; j < candidate_count; j++)
        {
            string name = get_string("Rank %i: ", j + 1);

            if (!vote(j, name, ranks))
            {
                printf("Invalid vote.\n");

                return 3;
            }
        }

        record_preferences(ranks);

        printf("\n");
    }

    add_pairs();
    sort_pairs();
    lock_pairs();
    print_winner();
    return 0;
}

// Update ranks given a new vote
bool vote(int rank, string name, int ranks[])
{
    // TODO

    for (int k = 0; k < candidate_count; k++)
    {
        //  printf("Candidate k: %s\n", candidates[k]);
        if (strcmp(name, candidates[k]) == 0)
        {
            ranks[rank] = k;
            return true;
        }
    }

    return false;
}

// Update preferences given one voter's ranks
void record_preferences(int ranks[])
{
    // TODO
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = i + 1; j < candidate_count; j++)
        {
            {
                preferences[ranks[i]][ranks[j]] = preferences[ranks[i]][ranks[j]] + 1;
            }
        }
    }
    return;
}

// Record pairs of candidates where one is preferred over the other
void add_pairs(void)
{
    // TODO
    pair_count = 0;
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = 0; j < candidate_count; j++)
        {
            // printf("preferences[%i][%i]: %i\n", i, j, preferences[i][j]);
            if (preferences[i][j] > preferences[j][i])
            {
                pairs[pair_count].winner = i;
                pairs[pair_count].loser = j;
                // printf("pairs %i: %i, %i\n", pair_count, pairs[pair_count].winner, pairs[pair_count].loser);
                pair_count = pair_count + 1;
            }
        }
    }
    return;
}

// Sort pairs in decreasing order by strength of victory
void sort_pairs(void)
{
    // TODO

    int save1 = 0;
    int save2 = 0;
    for (int i = 0; i < pair_count; i++)
    {
        for (int j = 0; j < pair_count - i; j++)
        {
            // printf("preferences [%i][%i]: %i\n", pairs[j].winner, pairs[j].loser, preferences[pairs[j].winner][pairs[j].loser]);
            // printf("preferences [%i][%i]: %i\n", pairs[j+1].winner, pairs[j+1].loser,
            // preferences[pairs[j+1].winner][pairs[j+1].loser]);
            if (preferences[pairs[j].winner][pairs[j].loser] < preferences[pairs[j + 1].winner][pairs[j + 1].loser])
            {
                save1 = pairs[j].winner;
                save2 = pairs[j].loser;
                pairs[j].winner = pairs[j + 1].winner;
                pairs[j].loser = pairs[j + 1].loser;
                pairs[j + 1].winner = save1;
                pairs[j + 1].loser = save2;
                // printf("pairs j: %i,%i, save1: %i, save2: %i\n", i, j, save1, save2);
                // printf("i = %i, pref j= %i [%i][%i]: %i, pref j + 1 [%i][%i]: %i\n", i, j, pairs[j].winner, pairs[j].loser,
                // preferences[pairs[j].winner][pairs[j].loser], pairs[j+1].winner, pairs[j+1].loser,
                // preferences[pairs[j+1].winner][pairs[j+1].loser]);
            }
        }
    }
    for (int i = 0; i < pair_count; i++)
    {
        // printf("sort pairs %i: %i, %i\n", i, pairs[i].winner, pairs[i].loser);
    }
    return;
}

bool check_cycle(int winner, int loser)
{
    // printf("winner = %i, loser = %i\n", winner, loser);

    if (loser == winner)
    {
        return true;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        if (locked[loser][i])
        {
            printf("locked: %d\n", locked[loser][i]);
            if (check_cycle(winner, i))
            {
                printf("cycle: locked[%i][%i]\n", winner, loser);
                return true;
            }
        }
    }
    // printf("no cycle: locked[%i][%i]\n", winner, loser);
    return false;
}

// Lock pairs into the candidate graph in order, without creating cycles
void lock_pairs(void)
{
    // TODO
    locked[pairs[0].winner][pairs[0].loser] = true;
    for (int i = 1; i < pair_count; i++)
    {
        printf("pair %i winner/loser: %i, %i\n", i, pairs[i].winner, pairs[i].loser);
        if (!check_cycle(pairs[i].winner, pairs[i].loser))
        {
            locked[pairs[i].winner][pairs[i].loser] = true;
            printf("locked[%i][%i]: %d\n", pairs[i].winner, pairs[i].loser, locked[pairs[i].winner][pairs[i].loser]);
        }
    }
    return;
}

bool not_loss(int winner)
{
    for (int i = 0; i < candidate_count; i++)
    {
        if (locked[i][winner])
        {
            return false;
        }
    }
    return true;
}

// Print the winner of the election
void print_winner(void)
{
    // TODO

    for (int i = 0; i < candidate_count; i++)
    {
        if (not_loss(i))
        {
            printf("%s\n", candidates[i]);
        }
    }
    return;
}
