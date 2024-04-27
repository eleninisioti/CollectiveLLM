import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from scipy.stats import ttest_ind

# Set random seed for reproducibility
np.random.seed(42)

# Generate dummy data for three methods (human, AI, random)
num_rounds = 1000
methods = ['Human', 'AI', 'Random']

# Initialize empty list to store data
data_list = []

# Generate data for each method
for method in methods:
    # Generate data for each round
    for _ in range(num_rounds):
        # Simulate combining two random elements
        element_1 = np.random.choice(range(1, 100))  # Example: Elements are represented by integers 1 to 99
        element_2 = np.random.choice(range(1, 100))  # Example: Elements are represented by integers 1 to 99

        # Append data for the current round to the list
        data_list.append({'Method': method, 'Element_1': element_1, 'Element_2': element_2})

# Convert the list of dictionaries to a DataFrame
data = pd.DataFrame(data_list)

# Convert element variables to categorical
data['Element_1'] = pd.Categorical(data['Element_1'])
data['Element_2'] = pd.Categorical(data['Element_2'])

# Create dummy variables for method
data = pd.get_dummies(data, columns=['Method'], drop_first=True)

# Split data into features (X) and target (y)
X = data.drop(columns=['Method_Human'])  # Exclude Method_Human column from features
y = data['Method_Human']  # Target variable: 1 if method is human, 0 otherwise

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize logistic regression model
model = LogisticRegression()

# Fit logistic regression model
model.fit(X_train, y_train)

# Get regression coefficients
coefficients = model.coef_[0]

# Retrieve coefficients corresponding to AI and Random features
coefficient_ai = coefficients[X.columns.get_loc('AI')]
coefficient_random = coefficients[X.columns.get_loc('Random')]

# Perform t-test
t_stat, p_value = ttest_ind(coefficient_ai, coefficient_random)

# Interpret the results
if p_value < 0.05:
    if t_stat > 0:
        print("Human data are more correlated with AI than Random.")
    else:
        print("Human data are more correlated with Random than AI.")
else:
    print("There is not enough evidence to conclude a significant difference.")
