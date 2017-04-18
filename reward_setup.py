import pandas as pd
import datetime
import sys

# Global variables, can be replaced with command line arguments
INPUT_FILENAME = "Cond2_sorted.csv"
R_OUTPUT_FILENAME = "Cond2_with_rewards.csv"
RA_OUTPUT_FILENAME = "Cond2_with_action_rewards.csv"


# Function for creating dictionary mapping column header to index
def index_dictionary(header_line, extras):
    in_dict = dict()
    header_split = header_line.replace("\n","").split(",")
    for ele, index in zip(header_split, range(len(header_split))):
        in_dict[ele] = index
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
def replace_rule_score(line, select_index, header_indexes, score_columns):
    line_split = line.split(",")
    for e in header_indexes.keys():
         if e in score_columns:
             line_split[header_indexes[e]] = pull_rule_score(line_split[header_indexes[e]],select_index=select_index)
    return ",".join(line_split)


def reward_function(line, header_indexes, score_columns):
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
    return replace_line.replace("\n","")


def get_action_reward(current_line, previous_line, header_indexes, score_cols, weight=2):
    try:
        #future_reward = float(current_line.split(",")[header_indexes["rewards"]])
        #current_reward = float(previous_line.split(",")[header_indexes["rewards"]])

        vector = []
        for e in score_cols:
            future_rs = float(current_line.split(",")[header_indexes[e]])
            current_rs = float(previous_line.split(",")[header_indexes[e]])
            difference = future_rs - current_rs
            if difference < 0:
                vector.append(difference * weight)
            else:
                vector.append(difference)
        action_reward = sum(vector)

        #action_reward = future_reward - current_reward
    except ValueError:
        action_reward = "NaN"
    except IndexError:
        action_reward = "NaN"
    return previous_line.replace("\n","") + "," + str(action_reward)


def set_rewards(input_filename=INPUT_FILENAME, output_filename=R_OUTPUT_FILENAME):
    print "Setting Rewards: ", datetime.datetime.now()
    # Data Initialization
    data_file = open(input_filename, "r")
    header_line = data_file.readline().replace("\n","")
    output_file = open(output_filename, "w")

    header_indexes = index_dictionary(header_line, extras=["rewards"])
    score_columns = get_score_cols(header_line)
    output_file.write(header_line+",rewards\n")

    for line in data_file:
        #line = data_file.readline()
        line = remove_excess_commas(line)
        line = replace_rule_score(line=line, select_index=0, header_indexes=header_indexes, score_columns=score_columns)
        line = reward_function(line=line, header_indexes=header_indexes, score_columns=score_columns)
        output_file.write(line+"\n")

    data_file.close()
    output_file.close()
    print "Rewards Set in %s : " % output_filename, datetime.datetime.now()


def check_line_conditions(line_split, header_indexes):
    a = len(line_split[header_indexes["hintGiven"]]) > 1 # indicates not a tutor action (hint given) step
    b = line_split[header_indexes["hintType"]] != "1" # indicates worked example
    c = line_split[header_indexes["hintGiven"]] != "No hint available for this step." # tutor not actually performing action (unable to give a hint)
    return a and b and c


def set_action_rewards(input_filename=R_OUTPUT_FILENAME, output_filename=RA_OUTPUT_FILENAME):
    print "Setting Action-Rewards from %s : " % input_filename, datetime.datetime.now()
    data_file = open(input_filename, "r")
    header_line = data_file.readline().replace("\n","")
    output_file = open(output_filename, "w")
    score_columns = get_score_cols(header_line)

    header_indexes = index_dictionary(header_line, extras=["action-reward"])
    output_file.write(header_line+",action-rewards,is-terminal\n")
    prev_line = ""
    alt_prev_line = ""
    prev_id = ""

    for line in data_file:
        line = remove_excess_commas(line)
        line = replace_rule_score(line=line, select_index=0, header_indexes=header_indexes, score_columns=score_columns)
        line_split = line.split(",")
        current_id = line_split[header_indexes["studentID"]]
        if current_id != prev_id and prev_id != "":  # indicates new student, immediately previous line is terminal action
            prev_line = get_action_reward(current_line=alt_prev_line, previous_line=prev_line, header_indexes=header_indexes, score_cols=score_columns)
            output_file.write(prev_line+",0\n")
            prev_line = line
        elif check_line_conditions(line_split, header_indexes):
            prev_line = get_action_reward(current_line=line, previous_line=prev_line, header_indexes=header_indexes, score_cols=score_columns)
            output_file.write(prev_line+",1\n")
            prev_line = line
        prev_id = current_id
        alt_prev_line = line
    data_file.close()
    output_file.close()
    print "Action-Rewards Set in %s : " % output_filename, datetime.datetime.now()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            set_rewards(input_filename=filename, output_filename=filename+"_rewards.csv")
            set_action_rewards(input_filename=filename+"_rewards.csv", output_filename=filename+"_action_rewards.csv")
    else:
        print "Using default input file: %s" % INPUT_FILENAME
        #set_rewards(input_filename=INPUT_FILENAME, output_filename=INPUT_FILENAME+"_rewards.csv")
        set_action_rewards(input_filename=INPUT_FILENAME, output_filename=INPUT_FILENAME[:-4]+"_action_rewards.csv")
