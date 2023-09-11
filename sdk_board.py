
from sdk_config import CHOICES, UNKNOWN, ROOT
from sdk_config import NROWS, NCOLS
import logging
import enum
from typing import Sequence, List, Set
logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger(__name__)

# --------------------------------
#  The events for MVC
# --------------------------------

class Event(object):
    """Abstract base class of all events, both for MVC
    and for other purposes.
    """
    pass
class EventKind(enum.Enum):
    TileChanged = 1
    TileGuessed = 2

class TileEvent(Event):
    """Abstract base class for things that happen
    to tiles. We always indicate the tile.  Concrete
    subclasses indicate the nature of the event.
    """

    def __init__(self, tile: 'Tile', kind: EventKind):
        self.tile = tile
        self.kind = kind

    def __str__(self):
        """Printed representation includes name of concrete subclass"""
        return f"{repr(self.tile)}"

# ---------------
# Observer (base class)
# ---------------

class Observer(object):
    """Abstract base class for observers.
    Subclass this to make the notification do
    something useful.
    """

    def __init__(self):
        """Default constructor for simple observers without state"""
        pass

    def notify(self, event: Event):
        """The 'notify' method of the base class must be
        overridden in concrete classes.
        """
        raise NotImplementedError("You must override Observer.notify")
class TileObserver(Observer):
    def notify(self, event: TileEvent):
        raise NotImplementedError(
            "TileObserver subclass needs to override notify(TileEvent)")

class Observable:
    """Objects to which observers (like a view component) can be attached"""

    def __init__(self):
        self.observers = [ ]

    def add_observer(self, observer: Observer):
        self.observers.append(observer)

    def notify_all(self, event: Event):
        for observer in self.observers:
            observer.notify(event)

# ------------------------------
#  Board class
# ------------------------------

class Board(object):
    """A board has a matrix of tiles"""
    def __init__(self):
        """The empty board"""
        # Row/Column structure: Each row contains columns
        self.tiles: List[List[Tile]] = [ ]
        self.groups = []

        for row in range(NROWS):
            cols = [ ]
            for col in range(NCOLS):
                cols.append(Tile(row, col))
            self.tiles.append(cols)
        self.groups = []

        for row in self.tiles: 
            self.groups.append(row)

        for index in range(NCOLS):
            column = []
            for row in self.tiles:
                column.append(row[index])
            self.groups.append(column)

        for block_row in range(ROOT):
            for block_col in range(ROOT):
                group = [ ] 
                for row in range(ROOT):
                    for col in range(ROOT):
                        row_addr = (ROOT * block_row) + row
                        col_addr = (ROOT * block_col) + col
                        group.append(self.tiles[row_addr][col_addr])
                self.groups.append(group)
        
    def is_consistent(self) -> bool:
        """checks if the board is legal.
        Returns:
        bool: True if the board is legal, False otherwise. """
        for group in self.groups:
            used_symbols = set()
            for tile in group:
                if tile.__str__() in CHOICES:
                    if tile.__str__() in used_symbols:
                        return False
                    else:
                        used_symbols.add(tile.__str__())
        return True

    def naked_single(self) -> bool:
        """Eliminate candidates and check for sole remaining possibilities.
        
        Returns:
            True means we crossed off at least one candidate.
            False means we made no progress.

            check every possiblilitie for each tile until 
            there is only one left or fail to solve
        """
        progress = False
        for group in self.groups:
            list_of_choices = set() 
            for tile in group:
                if tile.value in CHOICES:
                    list_of_choices.add(tile.value)
            for another_tile in group: 
                if another_tile.value == UNKNOWN:
                    progress = another_tile.remove_candidates(list_of_choices) or progress                 
        return progress

    def hidden_single(self):
        """uses hidden singles method to eliminate possible choices and assign values to tiles.
        Returns:
        Bool: True if progress is made, False otherwise."""
        progress = False
        
        for group in self.groups:
            leftovers = set(CHOICES)
            for tile in group: 
                if tile.value in CHOICES: 
                    leftovers.discard(tile.value)
            for value in leftovers:
                count = 0
                for another_tile in group:
                    if value in another_tile.candidates:
                        count += 1
                        the_tile = another_tile
                if count == 1:
                    progress = True
                    the_tile.set_value(value)
        return progress
                        
    def solve(self):
        """Solve the puzzle!
        returns:
            BOOL: True if the board is solved. False if not """
        self.propagate()
        if self.is_consistent() is False:
            return False
        if self.is_complete():
            return True
        min_tile_option = self.min_choice_tile()
        save_list = self.as_list()
        for list_value in list(min_tile_option.candidates):
            min_tile_option.set_value(list_value)
            if self.solve():
                return True
            self.set_tiles(save_list)
        return False 


    def propagate(self):
        """runs one sequence of naked single and hidden single solve methods.
        Return:
            None"""
        progress = True
        while progress:
            progress = self.naked_single()
            self.hidden_single()
        return

    def is_complete(self):
        """checks if the board is solved.
        Returns:
            True: if board is complete
            False: if board is incomplete"""
        for row in self.tiles:
            for tile in row:
                if tile.value == UNKNOWN:
                    return False
        return True
    
    def min_choice_tile(self):
        """The first tile in self.tiles whos value is not yet known.
        Returns:
            min_choice: the first tile that is not yet known. """
        min_so_far = NROWS + 1
        min_choice = None
        for row in self.tiles:
            for tile in row:
                if tile.value == UNKNOWN and len(tile.candidates) < min_so_far:
                    min_so_far = len(tile.candidates)
                    min_choice = tile
        return min_choice

    def as_list(self):
        """makes a string representation of a board at a particular state.
        returns:
        row_syms_to_list: a string representation of the board. """
        row_syms_to_list = [ ]
        for row in self.tiles:
            'gets the tile value from tile'
            values = [tile.value for tile in row]
            row_syms_to_list.append("".join(values))
        return row_syms_to_list   
            
    def set_tiles(self, tile_values: Sequence[Sequence[str]] ):
        """Set the tile values a list of lists or a list of strings
        Args:
            tile_values: list of lists containing values of tiles
        
        
        """
        for row_num in range(NROWS):
            for col_num in range(NCOLS):
                tile = self.tiles[row_num][col_num]
                tile.set_value(tile_values[row_num][col_num])
    def __str__(self) -> str:
        """In Sadman Sudoku format
        Returns: 
            str representation of rows and columns"""
        row_syms = [ ]
        for row in self.tiles:
            values = [tile.value for tile in row]
            row_syms.append("".join(values))
        return "\n".join(row_syms)

class Tile(Observable):
    def __init__(self, row: int, col: int, value=UNKNOWN):
        super().__init__()
        """Constructor for a new tile.
        Args:
            row:  row number of tile
            col:  column number of tile
            value:  initial value of tile
        """  
        assert value == UNKNOWN or value in CHOICES
        self.row = row
        self.col = col
        self.set_value(value)

    def set_value(self, value: str):
        """Set the value of this tile.
        Args:
            value: new tile value 
        """
        if value in CHOICES:
            self.value = value
            self.candidates = {value}
        else:
            self.value = UNKNOWN
            self.candidates = set(CHOICES)
        self.notify_all(TileEvent(self, EventKind.TileChanged))
    def __str__(self):
        return f"{self.value}"
    def __repr__(self):
        return f"Tile({self.row}, {self.col}, '{self.value}')"

    def could_be(self, value: str) -> bool:
        """True if value is a candidate value for this tile
        Args:
            value:  value to test
        Returns:
            True iff value is a candidate value for this tile.
        """
        return value in self.candidates
    def __hash__(self) -> int:
        """Hash on position only (not value)"""
        return hash((self.row, self.col))
    
    def remove_candidates(self, used_values: Set[str]) -> bool:
        """The used values cannot be a value of this unknown tile.
        We remove those possibilities from the list of candidates.
        If there is exactly one candidate left, we set the
        value of the tile.
        
        Args:
            used_values:  set of values that cannot be candidates
        Returns:  
            True means we eliminated at least one candidate,
            False means nothing changed (none of the 'used_values' was in our candidates set).
        """
        new_candidates = self.candidates.difference(used_values)
        if new_candidates == self.candidates:
            # Didn't remove any candidates
            return False
        self.candidates = new_candidates
        if len(self.candidates) == 1:
            self.set_value(new_candidates.pop())
        self.notify_all(TileEvent(self, EventKind.TileChanged))
        return True

# --------------------------------------
# Events and observers for Tile objects
# --------------------------------------


