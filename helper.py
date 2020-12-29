import datetime
from pyqtgraph import *

"""
    Get environment setting
"""
def env(parameter):
    with open('config.env', 'r') as env_file:
        environment_array = env_file.read().split("\n")
        for param in environment_array:
            param = param.replace(" ", "")
            p_specific = param.split("=")[0]
            if p_specific==parameter:
                return param.split("=")[1]

class TimeAxisItem(AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text='Time', units=None)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(value).strftime("%H:%M") for value in values]