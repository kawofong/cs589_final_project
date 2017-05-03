from sklearn.ensemble import RandomForestRegressor

from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import Imputer
from sklearn.metrics import make_scorer
from sklearn.linear_model import Lasso
import numpy as np
import pandas
import math
import time
import matplotlib.pyplot as plt


def hp_vs_rae_plot(x_array, y_array_1, y_array_2, clf_index):  # for plotting the hp vs rae for each model
    pic_name = ['./RFR_hp_vs_rae.png', './Lasso_hp_vs_rae.png', './SVR_hp_vs_rae.png']
    title_name = ["Train RAE and Test RAE for each n_estimators of RFR",
                  "Train RAE and Test RAE for each alpha of Lasso",
                  "Train RAE and Test RAE for each c of SVR"]
    x_name = ['n_estimators', 'alpha', 'c']
    for i in range(0, len(y_array_1)):
        y_array_1[i] *= -1
        y_array_2[i] *= -1

    # Plot a line graph
    labels = ["Test", "Train"]
    index = x_array

    plt.figure(2, figsize=(6, 4))  # 6x4 is the aspect ratio for the plot
    plt.plot(index, y_array_1, 'or-', linewidth=3)  # Plot the first series in red with circle marker
    plt.plot(index, y_array_2, 'sb-', linewidth=3)  # Plot the first series in blue with square marker

    # This plots the data
    plt.grid(True)  # Turn the grid on
    plt.ylabel("RAE")  # Y-axis label
    plt.xlabel(x_name[clf_index])  # X-axis label
    plt.title(title_name[clf_index])  # Plot title
    plt.legend(labels, loc="best")
    plt.savefig(pic_name[clf_index])
    plt.close()


def feature_importance_plot(y_array, clf_index):  # for plotting the feature importance and feature coefficient of RFR and Lasso
    # Plot a line graph

    savefig_loc = ['./feature_importance.png_RFR.png','./feature_importance_Lasso.png']
    ylabels = ["Importance", "coefficients"]
    title = ["Importance of each feature", "Coefficient for each feature"]
    index = range(1, 26)

    plt.figure(2, figsize=(6, 4))  # 6x4 is the aspect ratio for the plot
    plt.plot(index, y_array, 'or-', linewidth=3)  # Plot the first series in red with circle marker

    # This plots the data
    plt.grid(True)  # Turn the grid on
    plt.ylabel(ylabels[clf_index])  # Y-axis label
    plt.xlabel("Feature")  # X-axis label
    plt.title(title[clf_index])  # Plot title
    plt.savefig(savefig_loc[clf_index])
    plt.close()


def rae(prediction, correct):  # RAE
    total = 0
    for i in range(len(correct)):
        total += abs(correct[i] - prediction[i])
    return float(total) / len(correct)


def get_hyperparameter_optimized(clf, grid, num_folds):  # Get the RFR after hp optimization
    return GridSearchCV(estimator=clf, param_grid=grid, cv=num_folds, scoring=make_scorer(rae, greater_is_better=False)
                        , verbose=0)


def get_features():  # load the features from csv
    df = pandas.read_csv("./features.csv", header=None)
    data = df.as_matrix()

    # exclude the id column
    data = np.delete(data, [0], 1)

    # replace NA with np.nan and impute with mean

    imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(data)
    data = imp.transform(data)

    # drop zero rating recipes
    print "Num of data before deleting zeros: ", len(data)
    no_score_recipes = list([])
    for i in range(0, len(data)):
        if data[i][-1] == 0:
            no_score_recipes.append(i)
    data = np.delete(data, no_score_recipes, 0)
    print "Num of data AFTER deleting zeros: ", len(data)
    np.random.shuffle(data)

    return np.array_split(data, [int(0.8 * len(data))])


########## Main ##########

np.random.seed(7)

# get the data
split_data = get_features()
data_for_cv = split_data[0]
data_for_generalization_test = split_data[1]

clf = list([])
clf.append(RandomForestRegressor())
clf.append(Lasso())
clf.append(SVR())

clf_param_grid = list([])
hp_range = []
hp_range.append([10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
hp_range.append([0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.22, 0.24])
hp_range.append([0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0])
clf_param_grid.append({'n_estimators': hp_range[0]})
clf_param_grid.append({'alpha': hp_range[1]})
clf_param_grid.append({'C': hp_range[2]})

for i in range(0, len(clf)):  # len(data_for_cv)
    initial_time = time.clock()
    print " "
    print "########### CLF ##########"
    result_clf = get_hyperparameter_optimized(clf[i], clf_param_grid[i], 10)  # len(data_for_cv)

    train_x = data_for_cv[:, 0:data_for_cv.shape[1] - 1]
    train_y = data_for_cv[:, -1]
    test_x = data_for_generalization_test[:, 0:data_for_generalization_test.shape[1] - 1]
    test_y = data_for_generalization_test[:, -1]

    fitting = result_clf.fit(train_x, train_y)
    print result_clf.best_estimator_
    if i == 0:
        print result_clf.best_estimator_.feature_importances_
        feature_importance_plot(result_clf.best_estimator_.feature_importances_, 0)
    elif i == 1:
        print result_clf.best_estimator_.coef_
        feature_importance_plot(result_clf.best_estimator_.coef_, 1)
    predictions = result_clf.predict(test_x)
    print rae(predictions, test_y)
    print "Time Spent: ", time.clock() - initial_time
    # print result_clf.cv_results_
    hp_vs_rae_plot(hp_range[i],
                      result_clf.cv_results_['mean_test_score'].tolist(),
                      result_clf.cv_results_['mean_train_score'].tolist(), i)
    print "##########################"
