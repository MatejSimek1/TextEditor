from tkinter import *
from functools import total_ordering

COLLUMN_START = 5
ROW_HEIGHT = 20
CHAR_WIDTH = 11  # approximation for Courier style



class TextEditorModel:
    '''This class represents subject in observer principle'''
    def __init__(self, text:str):
        self.lines = [line for line in text.split("\r")] # list of text rows
        self.selectionRange = LocationRange(Location(0,0), Location(0,0))   # start and end coordinates of selected text
        self.cursorLocation = Location(0,0)      # coordinates of current cursor location
        self.cursorObservers: list[CursorObserver] = []     # list of cursor observers subscribed to this subject
        self.textObservers: list[TextObserver] = []         # list of text observers subscribed to this subject
    
    def allLines(self):
        '''Returns iterator/generator that goes through all lines of document'''
        for i, el in enumerate(self.lines):
            yield i, el
    
    def linesRange(self, index1:int, index2:int):
        '''
        Returns iterator that goes from lines of index index1 until index2-1.
        Index1 is inclusive, while index2 is exclusive: [index1, index2>
        '''
        for i in range(index1, index2):
            yield i, self.lines[i]
    
    def attachCursorObserver(self, observer:'CursorObserver'):
        '''This method attaches new cursor observer to this subject.'''
        self.cursorObservers.append(observer)
    def dettachCursorObserver(self, observer:'CursorObserver'):
        '''This method dettaches cursor observer from this subject.'''
        if observer in self.cursorObservers:
            self.cursorObservers.remove(observer)
    
    def attachTextObserver(self, observer:'TextObserver'):
        '''This metod attaches new text observer to this subject.'''
        self.textObservers.append(observer)
    def dettachTextObserver(self, observer:'TextObserver'):
        '''This metod dettaches text observer from this subject.'''
        if observer in self.textObservers:
            self.textObservers.remove(observer)


    def notifyCursorObservers(self):
        '''Notifying all cursor observers that a change was made.'''
        for o in self.cursorObservers:
            o.updateCursorLocation(self.cursorLocation)
    def notifyTextObservers(self):
        '''Notifying all text observers that a change was mafe.'''
        for to in self.textObservers:
            to.updateText()
    
    def moveCursorLeft(self):
        '''Tries to move cursor to the left.'''
        if self.cursorLocation.column > 0:
            '''If cursor is somewhere in the middle or right of the row -> move it one space left'''
            new_location = Location(self.cursorLocation.row, self.cursorLocation.column - 1)
            self.cursorLocation = new_location
            self.notifyCursorObservers()
            return True
        # If we didn't fulfilled upper condition -> cursor was at the start of the row (column = 0)
        elif self.cursorLocation.row > 0:
            '''If it isn't the first row -> move it one row upwards and place it at the rightmost location'''
            new_location = Location(self.cursorLocation.row - 1, len(self.lines[self.cursorLocation.row - 1]))
            self.cursorLocation = new_location
            self.notifyCursorObservers()
            return True
        '''Else -> the cursor was at index (0,0) and we leave it there'''
        return False

    def moveCursorRight(self):
        '''Tries to move cursor to the right.'''
        if self.cursorLocation.column < len(self.lines[self.cursorLocation.row]):
            '''If the cursor is not at the rightmost place in a row -> move it one space to the right.'''
            new_location = Location(self.cursorLocation.row, self.cursorLocation.column + 1)
            self.cursorLocation = new_location
            self.notifyCursorObservers()
            return True
        # If we didn't fulfilled upper condition -> cursor was at the end of the row
        elif self.cursorLocation.row < len(self.lines)-1:
            '''if it wasn't the last row -> move it one row down at place it at the leftmost location'''
            new_location = Location(self.cursorLocation.row + 1, 0)
            self.cursorLocation = new_location
            self.notifyCursorObservers()
            return True
        return False
    
    def moveCursorUp(self):
        '''Tries to move cursor upwards.'''
        if self.cursorLocation.row > 0:
            '''Move cursor one row uppwards'''
            newRowLocation = self.cursorLocation.row - 1
            newColumnLocation = self.cursorLocation.column
            if len(self.lines[newRowLocation]) < self.cursorLocation.column:
                '''If upper row is shorter than the initial position of a cursor in the starting row -> cursor should be placed at the end of row'''
                newColumnLocation = len(self.lines[newRowLocation])
            new_location = Location(newRowLocation,newColumnLocation)
            self.cursorLocation = new_location
            self.notifyCursorObservers()
            return True
        # if upper condition wasn't met -> we were in a first row
        elif self.cursorLocation.column > 0:
            '''Move cursor at the start of the line.'''
            new_location = Location(self.cursorLocation.row, 0)
            self.cursorLocation = new_location
            self.notifyCursorObservers()
            return True
        '''else -> the cursor was at index (0,0) and we leave it there'''
        return False

    def moveCursorDown(self):
        '''Tries to move cursor downwards.'''
        if self.cursorLocation.row < len(self.lines)-1:
            '''Move cursor one row downwards.'''
            newRowLocation = self.cursorLocation.row + 1
            newColumnLocation = self.cursorLocation.column
            if len(self.lines[newRowLocation]) < self.cursorLocation.column:
                '''If bottom row is shorter than the initial position of a cursor in the starting row -> cursor should be placed at the end of row'''
                newColumnLocation = len(self.lines[newRowLocation])
            new_location = Location(newRowLocation, newColumnLocation)
            self.cursorLocation = new_location
            self.notifyCursorObservers()
            return True
        # if upper condition wasn't met -> we were initially in the last row
        elif self.cursorLocation.column < len(self.lines[self.cursorLocation.row]):
            '''Move cursor at the end of line.'''
            new_location = Location(self.cursorLocation.row, len(self.lines[self.cursorLocation.row]))
            self.cursorLocation = new_location
            self.notifyCursorObservers()
            return True
        '''else -> the cursor was at the last end of text and we leave it there'''
        return False
    
    def deleteBefore(self):
        '''
        Deletes char before cursor (left from cursor) and moves cursor one space left. Or deletes "\r" and two rows merge into one.
        Equivalent to backspace button.
        '''
        deleteBefore = DeleteBeforeAction(self)
        deleteBefore.execute_do()
        UndoManager().push(deleteBefore)
        UndoManager().notifyUndoManagerObservers()
    
    def _performDeleteBefore(self):
        '''
        Deletes char before cursor (left from cursor) and moves cursor one space left. Or deletes "\r" and two rows merge into one.
        Equivalent to backspace button.
        '''
        row, column = self.cursorLocation.row, self.cursorLocation.column
        if column > 0:
            '''Delete one element and move cursor to the left.'''
            line = self.lines[row]
            self.lines[row] = line[:column-1] + line[column:]
            self.cursorLocation = Location(row, column-1)
        # this means that column was 0, and we want to concatenate two rows
        elif row > 0:
            '''Concatenate two rows.'''
            self.cursorLocation = Location(row-1, len(self.lines[row-1]))
            self.lines[row-1] += self.lines[row]
            self.lines.pop(row)
        else:
            '''cursor is at location (0,0) -> nothing to change'''
            return
        
        # self.notifyCursorObservers()
        # self.notifyTextObservers()
    
    def deleteAfter(self):
        '''Deletes char which is one space ahead of cursor. Leaves cursor unchanged.'''
        deleteAfter = DeleteAfterAction(self)
        deleteAfter.execute_do()
        UndoManager().push(deleteAfter)
        UndoManager().notifyUndoManagerObservers()
    
    def _performDeleteAfter(self):
        '''Deletes char which is one space ahead of cursor. Leaves cursor unchanged.'''
        row, column = self.cursorLocation.row, self.cursorLocation.column
        if column < len(self.lines[row]):
            '''Delete one char right from cursor.'''
            self.lines[row] = self.lines[row][:column] + self.lines[row][column+1:]
        # if not -> cursor is at the end of line
        elif row < len(self.lines)-1:
            '''We are not in the last row. -> concatenate row+1 to row and delete row+1'''
            self.lines[row] += self.lines[row+1]
            self.lines.pop(row+1)
        else:
            '''We are at the end of file. -> Nothing to do.'''
            return

    def deleteRange(self, r:'LocationRange'):
        '''Deletes given range of characters.'''
        deleteRange = DeleteRangeAction(self)
        deleteRange.execute_do()
        UndoManager().push(deleteRange)
        UndoManager().notifyUndoManagerObservers()
    
    def _performDeleteRange(self, r:'LocationRange'):
        '''Deletes given range of characters.'''
        start, end = r.startingCoordinate, r.endingCoordinate
        # standardization
        if start > end:
            start, end = end, start

        if start.row == end.row:
            '''Chosen text is in one row.'''
            line = self.lines[start.row]
            self.lines[start.row] = line[:start.column] + line[end.column:]
        else:
            '''Chosen text goes through many rows.'''
            self.lines[start.row:end.row+1] = [self.lines[start.row][:start.column] + self.lines[end.row][end.column:]]
            # line above -> deletes all rows from self.lines starting from start.row until end.row (included) and replaces it with one new line
    
        self.cursorLocation = Location(start.row, start.column)
        self.setSelectionRange(LocationRange(self.cursorLocation, self.cursorLocation))

    def insert(self, c: str):
        '''
        Method that takes char or string c and places it in place of a cursor and moves cursor.
        Actually, it calls for EditAction.execute_do()
        Input:
            - c: string -> input text
        '''
        insertAction = InsertTextAction(self, c)
        insertAction.execute_do()
        UndoManager().push(insertAction)
        UndoManager().notifyUndoManagerObservers()
    
    def _performInsert(self, c: str):
        if not c:
            return
        selectedRange = self.getSelectionRange()
        selectionStart = selectedRange.startingCoordinate
        selectionEnd = selectedRange.endingCoordinate

        if selectionStart != selectionEnd:
            '''
            There was selected text. -> firstly we need to remove it and then do insertion.
            '''
            self.deleteRange(LocationRange(selectionStart, selectionEnd))
        
        '''
        Input given string at the place of cursor and move cursore.
        '''
        cursor = self.cursorLocation # if deletion was made, cursor location has changed
        line = self.lines[cursor.row]
        self.lines[cursor.row] = line[:cursor.column] + c + line[cursor.column:]
        newRows = self.lines[cursor.row].split('\r')
        if len(newRows) > 1:
            '''\r was given in input string -> we need to split that one row into more rows'''
            self.lines = self.lines[:cursor.row] + [row for row in newRows] + self.lines[cursor.row+1:]
            if len(c) > 1:
                '''We didn't input only enter but the whole sentence, with new rows. -> wa want the cursor at the last input word'''
                lastLine = newRows[-1]
                self.cursorLocation = Location(cursor.row + len(newRows) - 1, len(lastLine))
            elif len(c) == 1:
                '''We just inputed \r using enter -> we want cursor at the start of the following row'''
                self.cursorLocation = Location(cursor.row+len(newRows)-1,0) # placing cursor at the start of last row from newRows
        else:
            '''
            line is already changed. -> We just need to move cursor.
            This section executes if we don't give multiple rows as input. -> we want cursor to move in the same row at the last inputed word.
            '''
            self.cursorLocation = Location(cursor.row, cursor.column + len(c))
    
    
    def getSelectionRange(self) -> 'LocationRange':
        '''Returns Location Range that are included in current selected area.'''
        return self.selectionRange
    
    def setSelectionRange(self, range: 'LocationRange'):
        '''Sets selection range for current selection.'''
        self.selectionRange = range
        self.notifyTextObservers()
    
    def getSelectionRangeText(self):
        '''Returns string of selected text.'''
        selectedRange = self.getSelectionRange()
        start, end = selectedRange.startingCoordinate, selectedRange.endingCoordinate

        # normalize
        if start > end:
            start, end = end, start

        if start == end:
            return ''
        
        if start.row == end.row:
            return self.lines[start.row][start.column:end.column]
        
        '''selected text is in more rows'''
        listRows = []
        for rowInd in range(start.row, end.row+1):
            if rowInd == start.row:
                '''select text from column index till the end of row'''
                listRows.append(self.lines[rowInd][start.column:])
            elif rowInd == end.row:
                listRows.append(self.lines[rowInd][:end.column])
            else:
                '''for all rows in between start row and end row -> takes all row'''
                listRows.append(self.lines[rowInd])
        
        return f"{'\r'.join(listRows)}"

@total_ordering
class Location:
    '''Class describing coordinates'''
    def __init__(self, row, column):
        self.row = row
        self.column = column
    
    def __eq__(self, other):
        '''Used to compare if two locations are equall'''
        if not isinstance(other, Location):
            return NotImplemented
        return self.row == other.row and self.column == other.column

    def __lt__(self, other):
        if not isinstance(other, Location):
            return NotImplemented
        # checking firstly by row and then column
        return (self.row, self.column) < (other.row, other.column)


class LocationRange:
    '''Class describing coordinates range'''
    def __init__(self, startingCoordinate:Location, endingCoordinate:Location):
        self.startingCoordinate = startingCoordinate
        self.endingCoordinate = endingCoordinate

class CursorObserver:
    '''This is cursor observer interface.'''
    def updateCursorLocation(self, loc:Location):
        pass

class TextObserver:
    '''This is text observer interface.'''
    def updateText(self):
        pass

class EditAction:
    '''Interface that defines which methods action classes have to define.'''
    def execute_do(self):
        pass
    def execute_undo(self):
        pass

class InsertTextAction(EditAction):
    '''
    Class for inserting text
    It also stores state before change, so we can later on do undo operations.
    '''
    def __init__(self, textEditorModel: TextEditorModel, inputText: str):
        self.textEditorModel = textEditorModel
        self.inputText = inputText
        self.initialLinesList = textEditorModel.lines.copy()
        self.initialCursorPosition = textEditorModel.cursorLocation
        self.selectedRange = textEditorModel.getSelectionRange()

    def execute_do(self):
        '''
        This method, if selection was given, deletes that selection and replaces it with given string. Otherwise it just places given string
        at the location of cursor and moves cursore that many spaces to the right.
        '''
        # it is important to have this here -> so after each call of execute_do we get fresh information about prior state
        self.initialLinesList = self.textEditorModel.lines.copy()
        self.textEditorModel.cursorLocation = self.initialCursorPosition
        
        self.textEditorModel._performInsert(self.inputText)
        self.textEditorModel.notifyCursorObservers()
        self.textEditorModel.notifyTextObservers()

    def execute_undo(self):
        self.textEditorModel.lines = self.initialLinesList
        self.textEditorModel.cursorLocation = self.initialCursorPosition
        self.textEditorModel.notifyCursorObservers()
        self.textEditorModel.notifyTextObservers()


class DeleteBeforeAction(EditAction):
    def __init__(self, textEditorModel: TextEditorModel):
        self.textEditorModel = textEditorModel
        self.initialLinesList = textEditorModel.lines.copy()
        self.initialCursorPosition = textEditorModel.cursorLocation
    
    def execute_do(self):
        self.initialLinesList = self.textEditorModel.lines.copy()
        self.textEditorModel.cursorLocation = self.initialCursorPosition
        self.textEditorModel._performDeleteBefore()
        self.textEditorModel.notifyCursorObservers()
        self.textEditorModel.notifyTextObservers()
    
    def execute_undo(self):
        self.textEditorModel.lines = self.initialLinesList
        self.textEditorModel.cursorLocation = self.initialCursorPosition
        self.textEditorModel.notifyCursorObservers()
        self.textEditorModel.notifyTextObservers()

class DeleteAfterAction(EditAction):
    def __init__(self, textEditorModel: TextEditorModel):
        self.textEditorModel = textEditorModel
        self.initialLinesList = textEditorModel.lines.copy()
        self.initialCursorPosition = textEditorModel.cursorLocation

    def execute_do(self):
        self.initialLinesList = self.textEditorModel.lines.copy()
        self.textEditorModel.cursorLocation = self.initialCursorPosition
        self.textEditorModel._performDeleteAfter()
        self.textEditorModel.notifyTextObservers()
    
    def execute_undo(self):
        self.textEditorModel.lines = self.initialLinesList
        self.textEditorModel.cursorLocation = self.initialCursorPosition
        self.textEditorModel.notifyTextObservers()

class DeleteRangeAction(EditAction):
    def __init__(self, textEditorModel: TextEditorModel):
        self.textEditorModel = textEditorModel
        self.initialLinesList = textEditorModel.lines.copy()
        self.initialCursorPosition = textEditorModel.cursorLocation
        self.selectedRange = textEditorModel.getSelectionRange()

    def execute_do(self):
        self.initialLinesList = self.textEditorModel.lines.copy()
        self.textEditorModel.cursorLocation = self.initialCursorPosition
        self.textEditorModel._performDeleteRange(self.selectedRange)
        self.textEditorModel.notifyCursorObservers()
        self.textEditorModel.notifyTextObservers()
    
    def execute_undo(self):
        self.textEditorModel.lines = self.initialLinesList
        self.textEditorModel.cursorLocation = self.initialCursorPosition
        self.textEditorModel.notifyCursorObservers()
        self.textEditorModel.notifyTextObservers()

class ClipboardStack:
    '''Class that provides stack functionality for clipboard operations (cut, paste...)'''
    def __init__(self):
        self.texts : list[str] = []     # imitates stack -> elements are strings
        self.clipboardObservers : list[ClipboardObserver] = []  # list of clipboard observers

    def pushInClipboard(self, text: str):
        '''Pushes text at the top of the stack.'''
        self.texts.append(text)

    def popFromClipboard(self) -> str:
        '''
        Pops and returns last element from the clipboard (if it is not empty).
        If it's empty method does not do anything.
        '''
        if self.isTextInClipboardPresent():
            return self.texts.pop()
    
    def peekAtClipboard(self) -> str:
        '''
        Says last element in clipboard, BUT DOES NOT change clipboard.
        If clipboard is not empty, if it is, method does nothing.
        '''
        if self.isTextInClipboardPresent():
            return self.texts[-1]
        
    def clearClipboard(self):
        '''Deletes everything from clipboard.'''
        self.texts.clear()
        
    def isTextInClipboardPresent(self) -> bool:
        return bool(self.texts)
    
    def attachClipboardObserver(self, clipboardObserver : 'ClipboardObserver'):
        '''Attaches given clipboard observer into a list of observers.'''
        self.clipboardObservers.append(clipboardObserver)
    
    def dettachClipboardObserver(self, clipboardObserver : 'ClipboardObserver'):
        '''Dettaches given clipboard observer from the list of observers.'''
        if clipboardObserver in self.clipboardObservers:
            self.clipboardObservers.remove(clipboardObserver)
    
    def notifyClipboardObservers(self):
        '''Notifies all clipboard observers about a change.'''
        for el in self.clipboardObservers:
            el.updateClipboard()

class ClipboardObserver:
    '''This is clipboard observer interface.'''
    def updateClipboard(self):
        pass

class UndoManager:
    '''
    Class that specifies undo and redo actions.
    This class is singleton and a subjet in OO observer
    '''
    _instance = None

    def __new__(cls):
        '''used in singletons -> static method which is called before __init__ method'''
        if cls._instance is None:
            cls._instance = super(UndoManager, cls).__new__(cls)
            cls.undoStack : list[EditAction] = []
            cls.redoStack : list[EditAction] = []
            cls.observers : list[UndoManagerObserver] = []
        return cls._instance
    
    def undo(self):
        '''takes command from undoStack, pushes it to redoStack and complites it'''
        if self.undoStack:
            '''undoStack is not empty'''
            command = self.undoStack.pop()
            command.execute_undo()
            self.redoStack.append(command)
            self.notifyUndoManagerObservers()
    
    def redo(self):
        '''takes command from redoStack, pushes it to undoStack adn complites it'''
        if self.redoStack:
            command = self.redoStack.pop()
            command.execute_do()
            self.undoStack.append(command)
            self.notifyUndoManagerObservers()
    
    def push(self, c: EditAction):
        '''deletes redoStack and pushes command to undoStack'''
        self.redoStack.clear()
        self.undoStack.append(c)
        self.notifyUndoManagerObservers()

    def attachUndoManagerObserver(self, o: 'UndoManagerObserver'):
        self.observers.append(o)
    
    def dettachUndoManagerObserver(self, o: 'UndoManagerObserver'):
        if o in self.observers:
            self.observers.remove(o)
    
    def notifyUndoManagerObservers(self):
        for el in self.observers:
            el.updateUndoRedo(bool(self.undoStack), bool(self.redoStack))

class UndoManagerObserver:
    '''Observer for undo and redo actions.'''
    def updateUndoRedo(self, undoAvailable: bool, redoAvailable: bool):
        pass

class TextEditor(Canvas, CursorObserver, TextObserver, ClipboardObserver):
    '''Component that lets to its users monitoring and simple editing of text.'''
    def __init__(self, master, textEditorModel:'TextEditorModel', **kwargs):    # 'TextEditorModel' -> forward reference
        super().__init__(master, **kwargs)
        self.textEditorModel = textEditorModel
        self.textEditorModel.attachCursorObserver(self)
        self.textEditorModel.attachTextObserver(self)
        self.clipboard = ClipboardStack()     # clipboardStack
        self.clipboard.attachClipboardObserver(self)
        self.shiftHeld = False
        self.oldCursorLoc = None    # marks starting location of cursor when shift is pressed
        self.deleteAllAndDraw()

        # binding buttons
        self.focus_set()    # enables click events -> directs input focus to this widget
        self.bind('<Left>', lambda event: self.move_cursore_left())
        self.bind('<Right>', lambda event: self.move_cursore_right())
        self.bind('<Up>', lambda event: self.move_cursore_up())
        self.bind('<Down>', lambda event: self.move_cursore_down())
        self.bind('<BackSpace>', lambda event: self.delete_before())
        self.bind('<Delete>', lambda event: self.delete_after())
        self.bind('<KeyPress-Shift_L>', lambda event: self.setShift(True))
        self.bind('<KeyRelease-Shift_L>', lambda event: self.setShift(False))
        self.bind('<Key>', lambda event: self.textEditorModel.insert(event.char) if event.char else None)
        self.bind('<Control-c>', lambda event: self.handle_copy())
        self.bind('<Control-x>', lambda event: self.handle_cut())
        self.bind('<Control-v>', lambda event: self.handle_paste())
        self.bind('<Control-Shift-V>', lambda event: self.handle_paste_and_pop())
        self.bind('<Control-z>', lambda event: UndoManager().undo())
        self.bind('<Control-y>', lambda event: UndoManager().redo())
    
    def handle_copy(self):
        '''Current selection (if existant) pushes back in clipboard.'''
        selectedText = self.textEditorModel.getSelectionRangeText()
        if selectedText:
            self.clipboard.pushInClipboard(selectedText)
        
    def handle_cut(self):
        '''pushes current selection (if existent) into clipboard and deletes it from text.'''
        self.handle_copy()  # pushes selection into clipboard
        self.textEditorModel.deleteRange(self.textEditorModel.getSelectionRange())
    
    def handle_paste(self):
        '''Pastes element from the top of stack (from clipboard into text -> by calling insert() method).'''
        self.textEditorModel.insert(self.clipboard.peekAtClipboard())
    
    def handle_paste_and_pop(self):
        '''Takes text from the top of the stack removes it and places it into text.'''
        self.textEditorModel.insert(self.clipboard.popFromClipboard())

    def setShift(self, value: bool):
        '''Stores whether shift is pressed and if so marks starting location of selected partition.'''
        if value == True:
            self.oldCursorLoc = Location(self.textEditorModel.cursorLocation.row, self.textEditorModel.cursorLocation.column)
        elif value == False:
            self.oldCursorLoc = None

        self.shiftHeld = value


    def move_cursore_left(self):
        '''
        Checks whether shift is pressed or not and depending on that it either selects section or just moves cursor left (and marks that Location
        range is from point x to point x)
        '''
        if self.shiftHeld:
            '''shift pressed -> select section'''
            self.textEditorModel.moveCursorLeft()
            self.textEditorModel.setSelectionRange(LocationRange(self.oldCursorLoc, self.textEditorModel.cursorLocation))
        else:
            '''shift not pressed'''
            self.textEditorModel.moveCursorLeft()
            self.textEditorModel.setSelectionRange(LocationRange(self.textEditorModel.cursorLocation, self.textEditorModel.cursorLocation))
    
    def move_cursore_right(self):
        '''
        Checks whether shift is pressed or not and depending on that it either selects section or just moves cursor right (and marks that Location
        range is from point x to point x)
        '''
        if self.shiftHeld:
            '''shift pressed -> select section'''
            self.textEditorModel.moveCursorRight()
            self.textEditorModel.setSelectionRange(LocationRange(self.oldCursorLoc, self.textEditorModel.cursorLocation))
        else:
            '''shift not pressed'''
            self.textEditorModel.moveCursorRight()
            self.textEditorModel.setSelectionRange(LocationRange(self.textEditorModel.cursorLocation, self.textEditorModel.cursorLocation))
    
    def move_cursore_up(self):
        '''
        Checks whether shift is pressed or not and depending on that it either selects section or just moves cursor up (and marks that Location
        range is from point x to point x)
        '''
        if self.shiftHeld:
            '''shift pressed -> select section'''
            self.textEditorModel.moveCursorUp()
            self.textEditorModel.setSelectionRange(LocationRange(self.oldCursorLoc, self.textEditorModel.cursorLocation))
        else:
            '''shift not pressed'''
            self.textEditorModel.moveCursorUp()
            self.textEditorModel.setSelectionRange(LocationRange(self.textEditorModel.cursorLocation, self.textEditorModel.cursorLocation))

    def move_cursore_down(self):
        '''
        Checks whether shift is pressed or not and depending on that it either selects section or just moves cursor down (and marks that Location
        range is from point x to point x)
        '''
        if self.shiftHeld:
            '''shift pressed -> select section'''
            self.textEditorModel.moveCursorDown()
            self.textEditorModel.setSelectionRange(LocationRange(self.oldCursorLoc, self.textEditorModel.cursorLocation))
        else:
            '''shift not pressed'''
            self.textEditorModel.moveCursorDown()
            self.textEditorModel.setSelectionRange(LocationRange(self.textEditorModel.cursorLocation, self.textEditorModel.cursorLocation))
    
    def delete_before(self):
        '''Determines whether it has to remove one char or the whole section.'''
        range = self.textEditorModel.getSelectionRange()
        start, end = range.startingCoordinate, range.endingCoordinate
        if start != end:
            '''Section is selected -> remove the whole section.'''
            self.textEditorModel.deleteRange(range)
        # otherwise -> only one char to remove
        else:
            self.textEditorModel.deleteBefore()
    
    def delete_after(self):
        '''Determines whether it has to remove one char or the whole section.'''
        range = self.textEditorModel.getSelectionRange()
        start, end = range.startingCoordinate, range.endingCoordinate
        if start != end:
            '''Section is selected -> remove the whole section.'''
            self.textEditorModel.deleteRange(range)
        # otherwise -> only one char to remove
        else:
            self.textEditorModel.deleteAfter()

    def updateCursorLocation(self, loc: Location):
        self.delete('cursor')
        x = COLLUMN_START + loc.column * CHAR_WIDTH
        y1 = loc.row * ROW_HEIGHT
        y2 = y1 + ROW_HEIGHT
        self.create_line(x, y1, x, y2, fill='black', tags='cursor')

    def updateText(self):
        '''Updates text.'''
        self.delete('all')
        # If section is selected -> show it as light blue corridore
        selection = self.textEditorModel.getSelectionRange()
        start = selection.startingCoordinate
        end = selection.endingCoordinate
        if start != end:
            # Normalizacija
            if start > end:
                start, end = end, start

            for row in range(start.row, end.row + 1):
                line = self.textEditorModel.lines[row]
                col_start = start.column if row == start.row else 0
                col_end = end.column if row == end.row else len(line)
                x1 = COLLUMN_START + col_start * CHAR_WIDTH
                x2 = COLLUMN_START + col_end * CHAR_WIDTH
                y1 = row * ROW_HEIGHT
                y2 = y1 + ROW_HEIGHT
                self.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline='', tags="selection")
        
        self.draw()

    def draw(self):
        '''This method draws text and cursor on a canvas.'''
        # managing text
        for i, line in self.textEditorModel.allLines():
            self.create_text(COLLUMN_START, i*ROW_HEIGHT, anchor='nw', text=line, font=('Courier',14))  # anchor=nw -> north-west (reff point for coord)
        # managing cursor
        cursor = self.textEditorModel.cursorLocation
        line = self.textEditorModel.lines[cursor.row]
        x = COLLUMN_START + cursor.column * CHAR_WIDTH
        y1 = cursor.row * ROW_HEIGHT
        y2 = y1 + ROW_HEIGHT
        self.create_line(x, y1, x, y2, fill="black", tags='cursor')

    def deleteAllAndDraw(self):
        '''
        Wrapper around draw method.
        Firstly it deletes everything on a canvas and then draws on it.
        '''
        self.delete('all')
        self.draw()
    
    def updateClipboard(self):
        '''Updates clipboard. Perhaps show it in status bar.'''
    
    def delete_document(self):
        self.textEditorModel.setSelectionRange(LocationRange(Location(0,0), Location(len(self.textEditorModel.lines)-1, len(self.textEditorModel.lines[len(self.textEditorModel.lines)-1]))))
        self.delete_before()
    
    def moveCursorAtDocumentStart(self):
        while self.textEditorModel.moveCursorUp():
            continue
        while self.textEditorModel.moveCursorLeft():
            continue
    
    def moveCursorAtDocumentEnd(self):
        while self.textEditorModel.moveCursorDown():
            continue
        while self.textEditorModel.moveCursorRight():
            continue

# main
root = Tk()
root.title("Text Editor")

textEditor = TextEditor(root, TextEditorModel("Ovo je moj prvi tekst editor.\rOvo je drugi redak,\rdok je ovo treći."), width=400, height=400)
# Toolbar (Frame + Buttons)
toolbar = Frame(root, bd=1, relief=RAISED)

spacer = Label(toolbar)
spacer.pack(side=LEFT, expand=True)
undoButton = Button(toolbar, text="Undo", command=UndoManager().undo)
undoButton.pack(side=LEFT, padx=2, pady=2)
redoButton = Button(toolbar, text="Redo", command=UndoManager().redo)
redoButton.pack(side=LEFT, padx=2, pady=2)
cutButton = Button(toolbar, text="Cut", command=textEditor.handle_cut)
cutButton.pack(side=LEFT, padx=2, pady=2)
copyButton = Button(toolbar, text="Copy", command=textEditor.handle_copy)
copyButton.pack(side=LEFT, padx=2, pady=2)
pasteButton = Button(toolbar, text="Paste", command=textEditor.handle_paste)
pasteButton.pack(side=LEFT, padx=2, pady=2)

toolbar.pack(side=TOP, fill=X)
textEditor.pack()

menuBar = Menu(root)

# file menu
fileMenu = Menu(menuBar, tearoff=0)
fileMenu.add_command(label='Open')
fileMenu.add_command(label='Save')
fileMenu.add_command(label='Exit')
menuBar.add_cascade(label='File', menu=fileMenu)

# edit menu
editMenu = Menu(menuBar, tearoff=0)
editMenu.add_command(label='Undo', command=UndoManager().undo)
editMenu.add_command(label='Redo', command=UndoManager().redo)
editMenu.add_command(label='Cut', command=textEditor.handle_cut)
editMenu.add_command(label='Copy', command=textEditor.handle_copy)
editMenu.add_command(label='Paste', command=textEditor.handle_paste)
editMenu.add_command(label='Paste and Take', command=textEditor.handle_paste_and_pop)
editMenu.add_command(label='Delete selection', command=textEditor.delete_before)    # giving delete_before or after bc if selection is given it deletes it
editMenu.add_command(label='Clear document', command=textEditor.delete_document)
menuBar.add_cascade(label='Edit', menu=editMenu)

# move menu
moveMenu = Menu(menuBar, tearoff=0)
moveMenu.add_command(label='Cursor to document start', command=textEditor.moveCursorAtDocumentStart)
moveMenu.add_command(label='Cursor to document end', command=textEditor.moveCursorAtDocumentEnd)
menuBar.add_cascade(label='Move', menu=moveMenu)

root.config(menu=menuBar)



root.mainloop()