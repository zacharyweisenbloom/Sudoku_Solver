"""
Reading and writing Sudoku boards.  We use the minimal
subset of the SadMan Sudoku ".sdk" format,
see http://www.sadmansoftware.com/sudoku/faq19.php

Author: M Young, January 2018
Modified: B Norris, Feb 5, 2022
"""

import sdk_board
from sdk_config import NROWS
from typing import List, Union
from io import IOBase

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)



class InputError(Exception):
    pass


def read(the_file: Union[IOBase, str],
         the_board: sdk_board.Board=None) -> sdk_board.Board:
    """Read a Sudoku sdk_board from a file.  Pass in a path
    or an already opened file.  Optionally pass in a sdk_board to be
    filled.
    """
    if isinstance(the_file, str):
        log.debug("Reading from string")
        the_file = open(the_file, "r")
    else:
        log.debug(f"Reading from file {the_file}")
    if the_board is None:
        the_board = sdk_board.Board()
    values = []
    for row in the_file:
        row = row.strip()
        log.debug(f"Reading row |{row}|")
        values.append(row)
        if len(row) != NROWS:
            raise InputError("Puzzle row wrong length: {}"
                             .format(row))
    log.debug(f"Read values: {values}")
    if len(values) != NROWS:
        raise InputError("Wrong number of rows in {}"
                         .format(values))
    the_board.set_tiles(values)
    the_file.close()
    return the_board



