
class PayWayError(Exception):
    pass

class InsecureDataError(Exception):
    pass

class PayProcessError(Exception):
    
    def __init__(self, message):
        self.message = message
        
    def __str__(self, *args, **kwargs):
        return repr(self.message)
