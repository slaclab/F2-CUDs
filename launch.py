# launcher script to spawn FACET-II CUDs
# desired display to launch is 1st (and only) arg

from sys import argv
from core import launcher

def show_help():
    print('Usage:')
    print('  $ python launcher.py [CUD_NAME]')
    print('  where [CUD_NAME] is one of:')
    for name in launcher.CUD_names(): print(f'  * {name}')
    print()

def main():
    try:
        target = argv[1]
        print(f' -> Launching FACET-II {target} CUD')
        launcher.run_CUD(target)
    except (KeyError, IndexError):
        print('Invalid arguments provided.')
        show_help()

if __name__ == '__main__':
    main()
