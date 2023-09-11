"""
File: display.py:
Sudoku sdk_board display. 
Designed for a simple model/view/controller architecture, 
in which the sdk_board display knows about the sudoku sdk_board, 
and not vice versa.  Communication from the sudoku sdk_board
to the sdk_board display is by event notifications through 
registered observers. 
Displays a rectangular grid of cells, organized in rows and columns
with row 0 at the top and growing down, column 0 at the left and 
growing to the right.  A sequence of unique colors for cells can 
be chosen from a color wheel, in addition to colors 'black' and 'white'
which do not appear in the color wheel. 
Author: M Young, Nov 10 2012 for CIS 210,
revised January 2018 for CIS 211
revised by B Norris, Feb 5, 2022 for CIS 211
"""

# Sudoku sdk_board configuration options

import time

# Peer classes from model
import sdk_board
from sdk_board import EventKind

# Graphics package based on Zelle's simple OO graphics
import Graphics.grid
import Graphics.graphics

from sdk_config import NROWS, NCOLS, ROOT, UNKNOWN, COLOR_UNKNOWN, COLOR_KNOWN, PENCIL, UPDATE_DELAY

import logging
logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger(__file__)


class Board(object):
    """View of sdk_board.Board"""

    def __init__(self, model: sdk_board.Board, width: int, height: int):
        """Create a view of the sdk_board.
        Width and height are dimensions in pixels.
        """
        self.model = model
        self.grid = graphics.grid.Grid(width, height, NROWS, NCOLS, title="Duck Sudoku")
        
        # We don't actually observe the model sdk_board; each individual tile view
        # observes its own model tile
        self.tiles = [ ]
        for row in model.tiles:
            for tile in row:
                self.tiles.append(Tile(self.grid, tile))

    def close(self):
        self.grid.close()


class Tile(sdk_board.TileObserver):
    """View of a single tile"""

    def __init__(self, grid: graphics.grid.Grid, model: sdk_board.Tile,
                     scan=False):
        """Create a view of a single tile"""
        self.grid = grid
        self.model = model
        self.row = model.row
        self.col = model.col
        self.scan = scan
        self.grid.sub_grid_dim(ROOT,ROOT)
        self._update(sdk_board.TileEvent(self.model, EventKind.TileChanged))
        self.model.add_observer(self)

    def _update(self, event: sdk_board.TileEvent):
        """Update the view of the tile when the model changes"""
        # Color code the tiles to indicate groups and status
        if event.kind == EventKind.TileChanged:
            self._color_by_status()
            self._label()
        else:
            raise ValueError("Unanticipated event type")
        time.sleep(UPDATE_DELAY)

    def _color_by_status(self):
        """Color the tile according to its status"""
        if self.model.value == UNKNOWN:
            self.grid.fill_cell(self.row, self.col, COLOR_UNKNOWN)
        else:
            self.grid.fill_cell(self.row, self.col, COLOR_KNOWN)

    def _label(self):
        """Label the tile with its value"""
        if self.model.value == UNKNOWN:
            self._pencil_marks()
        else:
            self.grid.label_cell(self.row, self.col, self.model.value)
        

    def _pencil_marks(self):
        """So-called 'pencil marks' are small digits indicating a possible 
        choice for a tile value.  We mark the possible choices in a 
        grid, leaving a blank for others.
        """
        for i in range(ROOT):
            for j in range(ROOT):
                    if self.model.could_be(PENCIL[i][j]):
                        self.grid.sub_label_cell(self.row, self.col,
                                                     i, j, PENCIL[i][j])


    def notify(self, event: sdk_board.TileEvent):
        """Update the view of the tile when the model changes"""
        self._update(event)