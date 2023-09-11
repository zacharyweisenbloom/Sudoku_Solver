"""
File: sudoku.py

Sudoku solver with optional displays. To solve a puzzle from the data/ folder
without any graphics, on the Console or Terminal:
    python3 sudoku.py data/easy.sdk
To show the graphical view, first click on "View Desktop" in CR, then 
run with:
    python3 sudoku.py -d data/easy.sdk

In Coding Rooms, you can change the settings and configure your RUN button
to use a different data file by specifying the above command as a "Custom Command"
under the "Run Configuration" option.

General usage: python3 sudoku.py [-h] [-d] [sdk_file]

Sudoku solver

positional arguments:
  sdk_file

options:
  -h, --help     show this help message and exit
  -d, --display  Graphical display
"""

import argparse
import sdk_reader
import sdk_display

import logging
logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger('sudoku.py')


def cli() -> object:
    """Get arguments from the command line"""
    parser = argparse.ArgumentParser(description="Sudoku solver")
    parser.add_argument("-d", "--display", help="Graphical display",
                        action="store_true")
    parser.add_argument('sdk_file', nargs='?', type=argparse.FileType('r'),
                        default='data/easy.sdk')
    args = parser.parse_args()
    return args


def main():
    args = cli()
    board = sdk_reader.read(args.sdk_file)
    log.debug(f'Read initial board from {args.sdk_file.name}:\n{board}')
    
    if args.display:
        the_display = sdk_display.Board(board, 800, 800)   
    if board.is_consistent():
        board.solve()
    else:
        print("Board has duplicates; rejected")
        
    print('Final board:')
    print(board)

    if args.display:
        input("Press enter to shut down")
        the_display.close()


if __name__ == "__main__":
    main()
