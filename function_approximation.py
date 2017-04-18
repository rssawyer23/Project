import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

INPUT_FILENAME = "ExtractedData_417/acttab2_hs_action_rewards.csv"
DISCOUNT = 0.9

# discretize HintGiven column (using hintType?)


#Removes rows that contain NaN values for desired input columns
def remove_NaN_rows(data_frame, cols_to_use):
    for col in cols_to_use:
        removed_rows = sum(pd.isnull(data_frame[col]))
        if removed_rows > 0:
            print "Removing %d rows because of %s" % (removed_rows, col)
            data_frame = data_frame.loc[pd.isnull(data_frame[col]) == False,:]
    return data_frame


# Solve for theta (fit the model), initially using only initial rewards
# may need to replace with a gradient descent update
#   This can be done for a sklearn.linear_model.LinearRegression by using the .get_params and .set_params methods
#   I believe this would work -> lm.set_params(lm.get_params() + gradient step)
def fit_model(input_data, response, model):
    print input_data.iloc[:5,:]
    print response[:5]
    model.fit(input_data, response)
    return model


# Reduce feature set (use parameter significance)
def reduce_features(input_data, response, model):
    pass


# Update labels using estimates from model adding to reward
def update_labels(full_data, model):
    predictions = model.predict(full_data[input_columns])
    full_data.loc[terminal_rows,"labels"] = full_data.loc[terminal_rows,"action_reward"]
    full_data.loc[non_terminal_rows,"labels"] = full_data.loc[non_terminal_rows,"action_reward"] + DISCOUNT * predictions
    pass



full_data = pd.read_csv(INPUT_FILENAME)
input_columns = ["hintType", "hintReceived", "proactiveHintReceived", "hintRequested", "cumul_hintsReceived", "cumul_proactiveHintsReceived", "cumul_hintsRequested"]
full_data = remove_NaN_rows(full_data, cols_to_use=input_columns)
direct_reward = full_data["action_rewards"]
terminal_rows = full_data["not_terminal"] == 0
non_terminal_rows = full_data["not_terminal"] == 1
full_data["labels"] = full_data["action_rewards"].copy()
#input_data = remove_NaN_rows(full_data[input_columns].copy())
input_data = full_data[input_columns]

lin_reg = LinearRegression()

fit_model(input_data=input_data, response=full_data["labels"], model=lin_reg)

print full_data.shape