import pandas as pd

# Global variables, can be replaced with command line arguments
INPUT_FILENAME = "Cond2_sorted.csv"
OUTPUT_FILENAME = "Cond2_with_rewards.csv"


# Function for creating dictionary mapping column header to index
def index_dictionary(header_line):
    in_dict = dict()
    header_split = header_line.split(",")
    for ele, index in zip(header_split, range(len(header_split))):
        in_dict[ele] = index
    extras = ["reward", "action-reward"]
    for e, i in zip(extras, range(len(header_split), len(header_split) + len(extras))):
        in_dict[e] = i
    return in_dict


# Function for getting list of columns that are score rule columns
def get_score_cols(header_line):
    header_split = header_line.split(",")
    score_cols = [ele for ele in header_split if "score" in ele]
    return score_cols


# Pulling a single value out of the semi-colon separated rule score cells
def pull_rule_score(rule_cell, select_index = 0):
    rule_split = rule_cell.split(";")
    return rule_split[select_index]


# Replacing each of the rule score semi-colons with single value
def replace_rule_score(line, select_index=0):
    line_split = line.split(",")
    for e in header_indexes.keys():
         if e in score_columns:
             line_split[header_indexes[e]] = pull_rule_score(line_split[header_indexes[e]],select_index=select_index)
    return ",".join(line_split)


def reward_function(line):
    line_split = line.split(",")
    reward_sum = 0
    for e in header_indexes.keys():
        if e in score_columns:
            try:
                reward_sum += float(line_split[header_indexes[e]])
            except ValueError:
                reward_sum += 0
    line_split += ["%.4f" % reward_sum]
    return ",".join(line_split)


def remove_excess_commas(line):
    replace_line = ""
    quote_on = False
    for char in line:
        if char == "\"":
            quote_on = not quote_on
        elif quote_on and char == ",":
            pass
        else:
            replace_line += char
    return replace_line



# Data Initialization
data_file = open(INPUT_FILENAME, "r")
header_line = data_file.readline()
output_file = open(OUTPUT_FILENAME, "w")

header_indexes = index_dictionary(header_line)
score_columns = get_score_cols(header_line)
#output_file.write(header_line)


for line in data_file:
    #line = data_file.readline()
    line = remove_excess_commas(line)
    line = replace_rule_score(line=line, select_index=0)
    line = reward_function(line=line)
    # output_file.write(line)

data_file.close()
output_file.close()


