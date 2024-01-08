import sqlite3
import json
import uuid

# Load database configuration
with open('./config.json') as config_file:
    config = json.load(config_file)
    
DATABASE_NAME = config['DATABASE_NAME']
TRIALS_TABLE_NAME = config['TRIALS_TABLE_NAME']
SUBJECTS_TABLE_NAME = config['SUBJECTS_TABLE_NAME']

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TRIALS_TABLE_NAME} (
                        row_id TEXT PRIMARY KEY,
                        prolific_id TEXT,
                        trial_id TEXT,
                        game_board TEXT,
                        game_state TEXT,
                        probe_position TEXT,
                        probe_type TEXT,
                        mine_present BOOLEAN,
                        user_response BOOLEAN,
                        response_correct BOOLEAN,
                        user_actions TEXT,
                        start_trial_time INTEGER,
                        response_given_time INTEGER,
                        total_reaction_time INTEGER
                        )''')
    
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {SUBJECTS_TABLE_NAME} (
                        prolific_id TEXT PRIMARY KEY,
                        score REAL,
                        bonus REAL,
                        age INTEGER,
                        gender TEXT,
                        education TEXT,
                        experience TEXT,
                        feedback TEXT
                        )''')
    conn.commit()
    conn.close()

def generate_unique_row_id(prolific_id, trial_id):
    return f"{prolific_id}-{trial_id}-{uuid.uuid4()}"

def save_trial_data(prolific_id, trial_data):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f'''INSERT INTO {TRIALS_TABLE_NAME} (row_id, prolific_id, trial_id, game_board, game_state, probe_position, probe_type, mine_present, user_response, response_correct, user_actions, start_trial_time, response_given_time, total_reaction_time)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (generate_unique_row_id(prolific_id, trial_data['trial_id']),
                prolific_id,
                trial_data['trial_id'], 
                json.dumps(trial_data['game_board']), 
                json.dumps(trial_data['game_state']), 
                json.dumps(trial_data['probe_position']),
                trial_data['probe_type'],
                trial_data['mine_present'], 
                trial_data['user_response'],
                trial_data['response_correct'], 
                json.dumps(trial_data['user_actions']), 
                trial_data['start_trial_time'],
                trial_data['response_given_time'],
                trial_data['total_reaction_time'])
            )
            conn.commit()
    except sqlite3.DatabaseError as e:
        # handle the database error
        print(f"Database error: {e}")
    except Exception as e:
        # Handle any other error
        print(f"Error: {e}")
        
        
def save_exit_data(prolific_id, score, bonus, survey_data):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f'''INSERT INTO {SUBJECTS_TABLE_NAME} (prolific_id, score, bonus, age, gender, education, experience, feedback)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (prolific_id,
                 score,
                 bonus,
                 survey_data['age'],
                 survey_data['gender'],
                 survey_data['education'],
                 survey_data['experience'],
                 survey_data['feedback'])
            )
            conn.commit()
    except sqlite3.DatabaseError as e:
        # Handle the database error
        print(f"Database error: {e}")
    except Exception as e:
        # Handle any other error
        print(f"Error: {e}")