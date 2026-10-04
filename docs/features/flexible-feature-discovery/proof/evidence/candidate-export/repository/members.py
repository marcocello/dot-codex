import argparse
import json
from pathlib import Path

def records():
    return json.loads(Path(__file__).with_name('members.json').read_text())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['list'])
    args = parser.parse_args()
    for member in records():
        print(member['name'], member['email'], member['active'])
