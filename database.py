import sqlite3
import json
import uuid

DATABASE_NAME = 'data.db'
TABLE_NAME = 'trials'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                        id TEXT PRIMARY KEY,
                        prolific_id TEXT,
                        trial_id TEXT,
                        game_board TEXT,
                        game_state TEXT,
                        probe_position TEXT,
                        mine_present BOOLEAN,
                        user_response BOOLEAN,
                        response_correct BOOLEAN,
                        user_actions TEXT,
                        total_reaction_time INTEGER
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
                f'''INSERT INTO {TABLE_NAME} (id, prolific_id, trial_id, game_board, game_state, probe_position, mine_present, user_response, response_correct, user_actions, total_reaction_time)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (generate_unique_row_id(prolific_id, trial_data['trial_id']),
                prolific_id,
                trial_data['trial_id'], 
                json.dumps(trial_data['game_board']), 
                json.dumps(trial_data['game_state']), 
                json.dumps(trial_data['probe_position']),
                trial_data['mine_present'], 
                trial_data['user_response'],
                trial_data['response_correct'], 
                json.dumps(trial_data['user_actions']), 
                trial_data['total_reaction_time'])
            )
            conn.commit()
    except sqlite3.DatabaseError as e:
        # handle the database error
        print(f"Database error: {e}")
    except Exception as e:
        # Handle any other error
        print(f"Error: {e}")