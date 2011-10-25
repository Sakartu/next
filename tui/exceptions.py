class TUIException(Exception):
    '''
    A TUI exception
    '''
    pass

class UserCancelled(TUIException):
    '''
    This class is raised when the user presses ^D in the TUI
    '''
    pass

class NoShowsException(TUIException):
    '''
    Class raides when there are no shows in the database
    '''
    pass
