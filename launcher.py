# launcher script to spawn FACET-II CUDs
# desired display to launch is 1st (and only) arg

from sys import argv
from core import launch

def show_help():
    print('Usage:')
    print('  $ python launcher.py [CUD_NAME]')
    print('  where [CUD_NAME] is one of:')
    for name in launch.CUD_names(): print(f'  * {name}')
    print()

def main():
    try:
        target = argv[1]
        print(f' -> Launching FACET-II {target} CUD')
        launch.run_CUD(target)
    except (KeyError, IndexError):
        print('Invalid arguments provided.')
        show_help()

if __name__ == '__main__':
    main()
