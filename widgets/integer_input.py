import re
from kivy.uix.textinput import TextInput

class IntegerInput(TextInput):

    #TODO: actually enforce integer inputs
    pat = re.compile('[^0-9]')
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(IntegerInput, self).insert_text(s, from_undo=from_undo)
