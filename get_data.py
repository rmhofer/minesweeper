import sqlite3
import pandas as pd
from database import DATABASE_NAME, TRIALS_TABLE_NAME, SUBJECTS_TABLE_NAME
import matplotlib.pyplot as plt
import seaborn as sns

def load_data_to_dataframe():
    # Establish a connection to the database
    conn = sqlite3.connect(DATABASE_NAME)

    # Load data into pandas DataFrames
    trial_data = pd.read_sql_query(f"SELECT * FROM {TRIALS_TABLE_NAME}", conn)
    subject_data = pd.read_sql_query(f"SELECT * FROM {SUBJECTS_TABLE_NAME}", conn)

    conn.close()
    return trial_data, subject_data

# usage
trial_data, subject_data = load_data_to_dataframe()


def print_bonus_info():
    conn = sqlite3.connect(DATABASE_NAME)
    query = f"SELECT prolific_id, bonus FROM {SUBJECTS_TABLE_NAME}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    for _, row in df.iterrows():
        print(f"{row['prolific_id']}, {float(row['bonus']):.2f}")

# usage
print_bonus_info()


def visualize_average_performance(trial_data):
    # Assuming 'probe_type' and 'response_correct' columns exist in trial_data
    avg_performance = trial_data.groupby('probe_type')['response_correct'].mean().reset_index()

    sns.barplot(x='probe_type', y='response_correct', data=avg_performance)
    plt.xlabel('Probe Type')
    plt.ylabel('Average Performance')
    plt.title('Average Performance by Probe Type')
    plt.show()

# Usage
visualize_average_performance(trial_data)