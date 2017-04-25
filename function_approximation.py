import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
import math

INPUT_FILENAMES = ["ExtractedData_424/acttab2_all_action_rewards.csv",
                   "ExtractedData_424/acttab5_all_action_rewards.csv",
                   "ExtractedData_424/acttab6_all_action_rewards.csv"]
#INPUT_COLUMNS = ["hintType", "hintReceived", "proactiveHintReceived", "hintRequested", "cumul_hintsReceived", "cumul_proactiveHintsReceived", "cumul_hintsRequested"]
# Cutting easyWE, difficultWE, restartCount
INPUT_COLUMNS = ['hintType', 'elTime', 'newInteraction', 'hintReceived', 'proactiveHintReceived', 'hintRequested', 'cumul_hintsReceived',
                 'cumul_proactiveHintsReceived', 'cumul_hintsRequested', 'problemDifficulty', 'easyProblem', 'difficultProblem',
                 'cumul_easyProblem', 'cumul_easyWE','cumul_difficultProblem', 'cumul_difficultWE', 'percentageDiffPS', 'percentageDiffWE',
                 'percentageWE', 'percentageDiff', 'skipCount','viewCount','selectCount','deSelectCount']
DISCOUNT = 0.9
TOTAL_ACTIONS = 2

# discretize HintGiven column (using hintType?)


# Removes rows that contain NaN values for desired input columns
def remove_NaN_rows(data_frame, cols_to_use):
    data_frame = data_frame.reindex_axis(labels=range(1, data_frame.shape[0]+1),axis=0)
    for col in cols_to_use:
        removed_rows = sum(pd.isnull(data_frame[col]))
        if removed_rows > 0:
            print "Removing %d rows because of %s" % (removed_rows, col)
            data_frame = data_frame.loc[pd.isnull(data_frame[col]) == False,:]
    data_frame.index = range(1, data_frame.shape[0]+1)
    return data_frame


# Converting the raw data into feature space for input to a supervised learning model
# Primary current purpose is to include interaction term with action
#   This will increase impact action has on the function value
def create_original_design_matrix(data, input_columns):
    temp_data = data.copy()
    for col in input_columns:
        if col != "hintType" and "-Interaction" not in col:
            if "action-%s-Interaction" % col not in input_columns:
                input_columns += ["action-%s-Interaction" % col]
            temp_data["action-%s-Interaction" % col] = temp_data["hintType"] * temp_data[col]
    return temp_data[input_columns].copy()


# Similar to above function but does not create new interaction terms
# This is to be used after feature selection has taken place (in proper format for next iteration)
def create_temp_design_matrix(data, full_data, input_columns):
    temp_data = data.copy()
    for col in input_columns:
        if "-Interaction" in col:
            base_col = col.split("-")[1]
            temp_data[col] = temp_data["hintType"] * full_data[base_col]
    return temp_data[input_columns].copy()


# Solve for theta (fit the model), initially using only initial rewards
# may need to replace with a gradient descent update
#   This can be done for a sklearn.linear_model.LinearRegression by using the .get_params and .set_params methods
#    -> lm.set_params(lm.get_params() + gradient step)
def fit_model(input_data, response, model):
    model.fit(input_data, response)
    return model


# Reduce feature set (use parameter significance)
def reduce_features(input_data, response, model):
    # Initializing and setting up data for use in feature selection
    remove_features = []
    keep_features = []
    all_features = list(input_data.columns.values)
    m = input_data.shape[1]
    X = np.array(input_data)

    # Linear Algebra to get the standard errors of each coefficient
    MSE = np.mean((response - model.predict(input_data).T)**2)
    var_est = MSE * np.diag(np.linalg.pinv(np.dot(X.T,X)))
    SE_est = np.sqrt(var_est)

    # Calculations for getting t-statistics for each coefficient
    for i in range(m):
        t_stat = model.coef_[i]/SE_est[i]
        if abs(t_stat) < 1 \
                and all_features[i] != "hintType":
            remove_features.append(all_features[i])
        else:
            keep_features.append(all_features[i])
    return input_data.loc[:,keep_features], remove_features


# Update labels using estimates from model adding to reward, needs to be fixed
def update_labels(predictions, immediate_rewards, non_terminal_rows):
    new_labels = immediate_rewards.copy()
    predictions = pd.Series(np.append(predictions, [0])[1:], index=range(1,len(new_labels)+1)) # Offsetting by one so using next state estimate
    new_labels[non_terminal_rows] = immediate_rewards[non_terminal_rows] + DISCOUNT * predictions[non_terminal_rows]
    return new_labels


# Making predictions for each action type and taking max action type as the predicted value
# This assumes the actions are ordinal, works for binary action space,
#    would need to revise for  one-hot encoding for more actions
def predict(model, input_data, full_data):
    all_predictions = np.zeros(shape=(input_data.shape[0],TOTAL_ACTIONS))
    temp_raw = input_data.copy()
    for action_code in range(TOTAL_ACTIONS):
        temp_raw["hintType"] = pd.Series(data=[action_code]*input_data.shape[0], index=range(1,input_data.shape[0]+1))
        temp_inputs = create_temp_design_matrix(data=temp_raw, full_data=full_data, input_columns=list(input_data.columns.values))
        for col in list(temp_inputs.columns.values):
            if sum(pd.isnull(temp_inputs[col])) > 0:
                print "%s:%d" % (col, sum(pd.isnull(temp_inputs[col])))
        all_predictions[:,action_code] = model.predict(temp_inputs)
    final_predictions = np.apply_along_axis(max, arr=all_predictions, axis=1)
    actions_selected = np.apply_along_axis(np.argmax, arr=all_predictions, axis=1)
    return final_predictions, actions_selected


# reading in filename and getting input columns to create date to be fed into model fitting (numerical, non NaN data)
# Function is pretty unnecessary, just to make the "main" cleaner to read
def initialize_data(input_filenames=INPUT_FILENAMES, input_columns=INPUT_COLUMNS):
    full_data = pd.DataFrame()
    for filename in input_filenames:
        new_data = pd.read_csv(filename)
        full_data = pd.concat([full_data, new_data],axis=0,ignore_index=True)
    # Changing hint type to 0,1 for binary representation of action space (useful for interaction terms later)
    full_data = remove_NaN_rows(full_data, cols_to_use=input_columns)
    full_data.loc[full_data["hintType"] == 2, "hintType"] = 0
    full_data.loc[full_data["hintType"] == 3, "hintType"] = 1
    non_terminal_rows = full_data["not_terminal"] == 1
    labels = full_data["action_rewards"].copy() # Initialized labels to immediate rewards
    immediate_rewards = full_data["action_rewards"].copy() # This will stay fixed throughout (and be fixed for terminal labels)
    input_data = create_original_design_matrix(full_data, input_columns)
    return full_data, input_data, non_terminal_rows, labels, immediate_rewards


# Helper function for traditional ECR method
def get_start_rows(full_data):
    start_indexes = []
    previous_id = "INVALID"
    for i, row in full_data.iterrows():
        if row["studentID"] != previous_id:
            start_indexes.append(i)
            previous_id = row["studentID"]
    return start_indexes


# Traditional ECR
# Finds start rows, calculates value (max A taken in fa.predict), returns mean (uniform start probability)
def traditional_ECR(full_data, input_data, input_columns, model):
    start_row_indexes = get_start_rows(full_data)
    start_rows = full_data.loc[start_row_indexes, input_columns]
    start_rows.index = range(1,start_rows.shape[0]+1)
    full_start_rows = full_data.loc[start_row_indexes, :]
    full_start_rows.index = range(1, start_rows.shape[0]+1)
    Q_values, actions_selected = predict(model, start_rows, full_start_rows)
    return np.mean(Q_values), np.std(Q_values), actions_selected


# Sampled ECR
# Treating data as following a multivariate normal distribution in order to draw samples
# fa.predict takes max A, returns mean of Q_values
def sampled_ECR(full_data, input_data, model, sample_size=10000):
    mean_vector = np.mean(full_data, axis=0)
    cov_matrix = np.cov(full_data, rowvar=False)
    sample_data = np.random.multivariate_normal(mean_vector, cov_matrix, size=sample_size)
    sample_data = pd.DataFrame(sample_data, columns=full_data.columns, index=range(1,sample_data.shape[0]+1))
    sample_data = create_original_design_matrix(sample_data, list(sample_data.columns.values))
    Q_values, actions_selected = predict(model, sample_data.loc[:,input_data.columns], sample_data)
    return np.mean(Q_values), np.std(Q_values), actions_selected


# Calculating the baseline ECR from the data
# Calculating average cumulative reward for each student in data
def baseline_ECR(full_data):
    ECRs = []
    previous_id = ""
    current_ECR = 0
    gamma_exp = 1
    for i, row in full_data.iterrows():
        if previous_id != row["studentID"]:
            ECRs.append(current_ECR)
            current_ECR = 0
            previous_id = row["studentID"]
            gamma_exp = 1
        current_ECR += math.pow(0.9, gamma_exp) * row["action_rewards"]
        gamma_exp += 1
    return np.mean(ECRs[1:]), np.std(ECRs[1:]), full_data["hintType"]


#model = LinearRegression(normalize=True)
model = Ridge(alpha=1.0)
delta_threshold = 0.05
prediction_sos = delta_threshold + 0.1 # Adding some constant to guarantee initial running of while loop
full_data, input_data, non_terminal_rows, labels, immediate_rewards = initialize_data(INPUT_FILENAMES, INPUT_COLUMNS)
all_removed_features = []
removed_features = []
iteration = 0
prev_predictions = labels.copy()
actions_selected = []

# Implementing an EM-Algorithm like method here, alternating between
#   Solving for the model parameters (fit_model)
#   Updating the expectations of the labels based on the (fixed) model and max action prediction value
while prediction_sos > delta_threshold:
    iteration += 1
    model = fit_model(input_data=input_data, response=labels, model=model)
    model_predictions, actions_selected = predict(model, input_data, full_data)
    differences = prev_predictions - model_predictions
    prediction_sos = differences.dot(differences.T)
    input_data, removed_features = reduce_features(input_data, labels, model)
    all_removed_features += removed_features
    labels = update_labels(model_predictions, immediate_rewards, non_terminal_rows)
    prev_predictions = model_predictions.copy()
    print "Iteration %d, LabelDifSoS %.4f, CoefSOS %.4f, RemovedFeats:%d" % (iteration, prediction_sos, model.coef_.dot(model.coef_.T), len(removed_features))

# Running evaluation methods on function after
print "Printing Coefficients:"
for i in range(input_data.shape[1]):
    print "%s:\t %.4f" % (list(input_data.columns.values)[i], model.coef_[i])
# Calculating the average and std for each ECR, could also plot histograms of the ECRs
print "R^2: %.5f" % (model.score(input_data, labels))
t_ECR, t_ECR_std, t_actions = traditional_ECR(full_data, input_data, list(input_data.columns.values), model)
print "Traditional ECR:%.5f +/- %.4f, percent A1:%.3f" % (t_ECR, 2*t_ECR_std, np.mean(t_actions))
non_inter_inputs = [e for e in list(input_data.columns.values) if "-Interaction" not in e]
s_ECR, s_ECR_std, s_actions = sampled_ECR(full_data.loc[:, non_inter_inputs], input_data, model)
print "Sampled ECR:%.5f, +/- %.4f, percent A1:%.3f" % (s_ECR, 2*s_ECR_std, np.mean(s_actions))
# Baseline is average and std discounted cumulative reward of all students
base_ECR, base_ECR_std, b_actions = baseline_ECR(full_data)
print "Baseline ECR:%.5f, +/- %.4f, percent A1:%.3f" % (base_ECR, 2*base_ECR_std, np.mean(b_actions))

# Calculate the rows from each separate data file using the function? -> ECR for three different policies

