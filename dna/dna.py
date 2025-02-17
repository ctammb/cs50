import csv
import sys


def main():
    # TODO: Check for command-line usage
    # Ensure correct usage
    if len(sys.argv) != 3:
        print("Usage: python dna.py csv.file text.file")
        return

    # TODO: Read database file into a variable
    csv_file = sys.argv[1]
    seq_dict_keys = []
    seq_dict = []
    with open(csv_file, newline="") as csvfile:
        file_reader = csv.DictReader(csvfile)
        num_str = len(file_reader.fieldnames)
        seq_dict_keys = file_reader.fieldnames[1:]
        for row in file_reader:
            seq_dict.append(row)

    # TODO: Read DNA sequence file into a variable
    txt_file = sys.argv[2]
    file = open(txt_file, "r")
    sequence = file.readline()
    file.close()

    # initializes table
    long_run = dict.fromkeys(seq_dict_keys, 0)
    # TODO: Find longest match of each STR in DNA sequence
    for subsequence in seq_dict_keys:
        long_run[subsequence] = longest_match(sequence, subsequence)

    # TODO: Check database for matching profiles
    for seq_dict_row in seq_dict:
        count_positive = 0

        for subsequence in seq_dict_keys:
            if int(seq_dict_row[subsequence]) == long_run[subsequence]:
                count_positive += 1

        if count_positive == num_str - 1:
            print(seq_dict_row["name"])
            return

    print("No match")
    return


def longest_match(sequence, subsequence):
    """Returns length of longest run of subsequence in sequence."""

    # Initialize variables
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    # Check each character in sequence for most consecutive runs of subsequence
    for i in range(sequence_length):
        # Initialize count of consecutive runs
        count = 0

        # Check for a subsequence match in a "substring" (a subset of characters) within sequence
        # If a match, move substring to next potential match in sequence
        # Continue moving substring and checking for matches until out of consecutive matches
        while True:
            # Adjust substring start and end
            start = i + count * subsequence_length
            end = start + subsequence_length

            # If there is a match in the substring
            if sequence[start:end] == subsequence:
                count += 1

            # If there is no match in the substring
            else:
                break

        # Update most consecutive matches found
        longest_run = max(longest_run, count)

    # After checking for runs at each character in seqeuence, return longest run found
    return longest_run


main()
