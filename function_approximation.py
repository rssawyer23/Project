import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

INPUT_FILENAME = "ExtractedData_417/acttab2_hs_action_rewards.csv"
INPUT_COLUMNS = ["hintType", "hintReceived", "proactiveHintReceived", "hintRequested", "cumul_hintsReceived", "cumul_proactiveHintsReceived", "cumul_hintsRequested"]
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


# Converting the raw data into feature space for input to a supervised learning model (including interaction terms)
def create_design_matrix(full_data, input_columns):
    return full_data[input_columns].copy()


# Solve for theta (fit the model), initially using only initial rewards
# may need to replace with a gradient descent update
#   This can be done for a sklearn.linear_model.LinearRegression by using the .get_params and .set_params methods
#    -> lm.set_params(lm.get_params() + gradient step)
def fit_model(input_data, response, model):
    model.fit(input_data, response)
    return model


# Reduce feature set (use parameter significance)
def reduce_features(input_data, response, model):
    return input_data, []


# Update labels using estimates from model adding to reward, needs to be fixed
def update_labels(predictions, immediate_rewards, non_terminal_rows):
    new_labels = immediate_rewards
    predictions = np.append(predictions, [0])[1:]
    new_labels[non_terminal_rows] = immediate_rewards[non_terminal_rows] + DISCOUNT * predictions[non_terminal_rows] # NEED TO MAKE THESE OFFSET BY ONE DOWN
    return new_labels


# reading in filename and getting input columns to create date to be fed into model fitting (numerical, non NaN data)
# Function is pretty unnecessary, just to make the "main" cleaner to read
def initialize_data(input_filename=INPUT_FILENAME, input_columns=INPUT_COLUMNS):
    full_data = pd.read_csv(INPUT_FILENAME)
    full_data = remove_NaN_rows(full_data, cols_to_use=input_columns)
    non_terminal_rows = full_data["not_terminal"] == 1
    labels = full_data["action_rewards"].copy() # Initialized labels to immediate rewards
    immediate_rewards = full_data["action_rewards"].copy() # This will stay fixed throughout (and be fixed for terminal labels)
    input_data = create_design_matrix(full_data, input_columns)
    return full_data, input_data, non_terminal_rows, labels, immediate_rewards


model = LinearRegression()
delta_threshold = 0.05
label_change_sos = delta_threshold + 0.1
full_data, input_data, non_terminal_rows, labels, immediate_rewards = initialize_data(INPUT_FILENAME, INPUT_COLUMNS)
removed_features = []

# Implementing an EM-Algorithm like method here, alternating between
#   Solving for the model parameters (fit_model)
#   Updating the expectations of the labels based on the (fixed) model and max action prediction value
while label_change_sos > delta_threshold and len(removed_features) < 1:
    model = fit_model(input_data=input_data, response=labels, model=model)
    model_predictions = model.predict(X=input_data) # need to take the MAX a here when predicting, i.e. create multiple prediction arrays for each action possible
    differences = labels - model_predictions
    label_change_sos = differences.dot(differences.T)
    input_data, removed_features = reduce_features(input_data, model_predictions, model)
    labels = update_labels(model_predictions, immediate_rewards, non_terminal_rows)


print full_data.shape