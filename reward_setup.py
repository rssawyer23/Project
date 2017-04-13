import pandas as pd

# Global variables, can be replaced with command line arguments
INPUT_FILENAME = "Cond2_sorted.csv"


# Function for creating dictionary mapping column header to index
def index_dictionary(header_line):
    in_dict = dict()
    header_split = header_line.split(",")
    for ele, index in zip(header_split, range(len(header_split))):
        in_dict[ele] = index
    extras = ["reward", "action-reward"]
    for e, i in zip(extras, range(len(header_split)+1, len(header_split) + len(extras) + 1)):
        in_dict[e] = i
    return in_dict


# Function for getting list of columns that are score rule columns
def get_score_cols(header_line):
    header_split = header_line.split(",")
    score_cols = [ele for ele in header_split if "score" in ele]
    return score_cols

# Data Initialization
data_file = open(INPUT_FILENAME, "r")
header_line = data_file.readline()

header_indexes = index_dictionary(header_line)
score_columns = get_score_cols(header_line)


#for line in data_file:
for i in range(10):
    line = data_file.readline()
    line_split = line.split(",")

