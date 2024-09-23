import sqlite3
from random import randint
from argparse import ArgumentParser
from pinterest import *
from dotenv import dotenv_values
from json import load, dump
from sqlite3 import Connection

VALUES = dotenv_values()

path = r"C:\Users\Gato\Documents\OneDrive\Obsidian Vault"
selections = {}

def get_db_connection() -> Connection:
    """Create and return a database connection."""
    return sqlite3.connect(fr'{path}\scripts\python\data\pins.db')

def get_links(pins):
    """Extract image URLs from pin data."""
    return [pin['image_url'] for pin in pins if 'image_url' in pin]

def updating(boards):
    """Update pin data from the boards and store in the database."""
    all_data = {}
    links = {}
    conn = get_db_connection()
    cursor = conn.cursor()
    
    r = ReferenceShuffle(email=VALUES['EMAIL'], username=VALUES['USERNAME'], password=VALUES['PASSWORD'])
    
    for name, board in boards.items():
        board_id = board['id']
        # Fetch new pin data using Pinterest library
        prev_data = load(open(fr'{path}\scripts\python\data\data.json', 'r', encoding='UTF-8')).get(name, [])
        new_data = r.get_board_pins(board_id, as_url=False, prev_data=prev_data)
        
        # Update database with new data
        cursor.execute('DELETE FROM pins WHERE board_node_id = ?', (board_id,))
        for pin in new_data:
            cursor.execute('''
                INSERT INTO pins (
                    node_id, board_node_id, pin_id, saves, done, pinner_name, pinner_username,
                    description, image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pin['node_id'],
                board_id,
                pin.get('aggregated_pin_data', {}).get('id', None),
                pin.get('aggregated_pin_data', {}).get('saves', 0),
                pin.get('aggregated_pin_data', {}).get('done', 0),
                pin.get('pinner', {}).get('full_name', None),
                pin.get('pinner', {}).get('username', None),
                pin.get('description', None),
                pin.get('images', {}).get('orig', {}).get('url', None)
            ))
        conn.commit()

        all_data[name] = new_data
        links[name] = get_links(new_data)
        print(f'{name} refreshed!')

    save_data(all_data, conn)
    conn.close()
    
    return links

def shuffle_data(name, pins):
    """Shuffle pin data for display."""
    selections[name] = []
    i = 0
    
    while len(selections[name]) < 12 and i <= 500 and len(pins) > 1:
        temp = f'<img src="{pins[randint(0, len(pins) - 1)]}" style="width: 100%;">'
        if temp not in selections[name]:
            selections[name].append(temp)
        i += 1

def save_markdown():
    """Save selections to Markdown file."""
    with open(fr'{path}\References.md', 'w+', encoding='UTF-8') as f:
        header = '''```button
name Reset References
type command
action Execute Code: Run all Code Blocks in Current File
color blue
```
''' 
        bottom = '''
```python from os import system from os.path import expanduser

usr = expanduser('~') 
path = fr'{usr}\Documents\OneDrive\Obsidian Vault\scripts\python' 
system(fr'python "{path}\DailyDrawScript.py" -s') 
print('# References changed')
```
'''

        f.write(header)
        for name in selections:
            f.write('\n---\n')
            f.write(f'## {name}')
            f.write('\n<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">\n')
            f.write('\n'.join(selections[name]))
            f.write('\n</div>\n')
        f.write('\n')
        f.write(bottom)

def save_data(all_data, conn):
    """Save data to the database."""
    cursor = conn.cursor()
    for name, pins in all_data.items():
        for pin in pins:
            cursor.execute('''
                INSERT OR REPLACE INTO pins (
                    node_id, board_node_id, pin_id, saves, done, pinner_name, pinner_username,
                    description, image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pin['node_id'],
                board_id,
                pin.get('aggregated_pin_data', {}).get('id', None),
                pin.get('aggregated_pin_data', {}).get('saves', 0),
                pin.get('aggregated_pin_data', {}).get('done', 0),
                pin.get('pinner', {}).get('full_name', None),
                pin.get('pinner', {}).get('username', None),
                pin.get('description', None),
                pin.get('images', {}).get('orig', {}).get('url', None)
            ))
    conn.commit()

def main(refresh, shuffle):
    """Main function to handle arguments and execute operations."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT board_node_id FROM pins
    ''')
    boards_ids = [row[0] for row in cursor.fetchall()]
    
    boards = {board_id: {'id': board_id} for board_id in boards_ids}
    
    if refresh:
        links = updating(boards)
    else:
        cursor.execute('''
            SELECT * FROM pins
        ''')
        data = cursor.fetchall()
        links = get_links(data)
    
    if shuffle:
        for name, pins in links.items():
            shuffle_data(name, pins)
        save_markdown()
    
    conn.close()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-r', '--refresh', action='store_true')
    parser.add_argument('-s', '--shuffle', action='store_true')
    args = parser.parse_args()
    
    main(args.refresh, args.shuffle)