class Graph_data_graph:

    def __init__(self,data={}):
        self.data = data

    def setData(self,time=[],expected=[],actual=[],uom=""):
        self.data = {'time': time, 'expected':expected, 'actual':actual,'uom':uom}
