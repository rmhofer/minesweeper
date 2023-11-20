import sqlite3
import json

DATABASE_NAME = 'data.db'
TABLE_NAME = 'trials'

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                        id INTEGER PRIMARY KEY,
                        trial_id TEXT,
                        game_board TEXT,
                        game_state TEXT,
                        probe_position TEXT,
                        mine_present BOOLEAN,
                        user_response BOOLEAN,
                        response_correct BOOLEAN,
                        reaction_time INTEGER,
                        prolific_id TEXT)''')
    conn.commit()
    conn.close()

def save_trial_data(trial_data, trial_id, prolific_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''INSERT INTO {TABLE_NAME} (trial_id, game_board, game_state, probe_position, mine_present, user_response, response_correct, reaction_time, prolific_id)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (trial_id, json.dumps(trial_data['game_board']), 
                    json.dumps(trial_data['game_state']), json.dumps(trial_data['probe_position']),
                    trial_data['mine_present'], trial_data['user_response'],
                    trial_data['response_correct'], trial_data['reaction_time'],
                    prolific_id))
    conn.commit()
    conn.close()