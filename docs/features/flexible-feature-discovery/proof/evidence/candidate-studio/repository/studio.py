import json
from pathlib import Path

def schedule():
    return json.loads(Path(__file__).with_name('schedule.json').read_text())

if __name__ == '__main__':
    print(json.dumps(schedule(), indent=2))
