import csv

# load data from csv
def load_csv(filename):
    total_store = []
    row_store = []
    with open(filename, 'rU') as f:  # opens PW file
        reader = csv.reader(f)
        # Print every value of every row.
        for row in reader:
            for value in row:
                row_store.append(str(value))
            total_store.append(row_store)
            row_store = []
    return total_store




#load_csv_basic_info = load_csv("basic_info.csv")
#load_csv_ingredients = load_csv("ingredients.csv")
#load_csv_steps = load_csv("steps.csv")





