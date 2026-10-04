import sys
PRESETS = {}
def save(name, filters):
    PRESETS[name] = filters
def load(name):
    return PRESETS.get(name)
if __name__ == '__main__':
    command, name = sys.argv[1:3]
    if command == 'save':
        save(name, sys.argv[3])
        print('Saved ' + name)
    elif command == 'load':
        print(load(name))
