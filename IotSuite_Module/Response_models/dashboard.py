import math


class Dashboard:

    def __init__(self, E_Generation={},E_Consumption={},Irr={},Tree_save={},Temperature ={}, Expected = {},PR={}):
        self.E_Generation = E_Generation
        self.setE_Generation_Graph([],[],"","")
        self.setE_Generation_summary(last_hour=round(0, 2), current=round(0, 2), l_uom="", c_uom="")
        self.setE_Generation_SummaryGraph(x=[], y=[], x_uom="", y_uom="")
        self.E_Consumption = E_Consumption
        self.setE_Consumption_Graph([], [], "", "")
        self.setE_Consumption_summary(last_hour=round(0, 2), current=round(0, 2), l_uom="", c_uom="")
        self.setE_Generation_SummaryGraph(x=[], y=[], x_uom="", y_uom="")
        self.Irr = Irr
        self.setIrr_Graph([], [], "", "")
        self.setE_Consumption_Graph([], [], "", "")
        self.setIrr_summary(last_hour=round(0, 2), current=round(0, 2), uom="")
        self.setIrr_SummaryGraph(x=[], y=[], x_uom="", y_uom="")
        self.Tree_save = Tree_save
        self.setTree_save_Graph([], [], "", "")
        self.setTree_save_summary(last_hour=0, current=0, co2_uom="", tree_uom="", co2=0)
        self.setTree_save_SummaryGraph(x=[], y=[], x_uom="", y_uom="")
        self.Temperature = Temperature
        self.setTemperatureGraph([], [], "", "","")
        self.Expected = Expected
        self.setExpected_Graph([], [], "", "")
        self.PR = PR
        self.setPR_Graph([], [], "", "")

    def reset(self):
        self.E_Generation = {}
        self.E_Consumption = {}
        self.Irr = {}
        self.Tree_save = {}
        self.Temperature = {}
        self.Expected = {}


    def setE_Generation_Graph(self, x, y, x_uom="", y_uom=""):
        if x is None:
            x = []
        if y is None:
            y = []
        self.E_Generation.__setitem__("Graphdata", {'x': x, 'y': y, 'x_UOM': x_uom, 'y_UOM': y_uom})

    def setE_Consumption_Graph(self, x, y, x_uom="", y_uom=""):
        if x is None:
            x = []
        if y is None:
            y = []
        self.E_Consumption.__setitem__("Graphdata", {'x': x, 'y': y, 'x_UOM': x_uom, 'y_UOM': y_uom})

    def setIrr_Graph(self, x, y, x_uom="", y_uom=""):
        if x is None:
            x = []
        if y is None:
            y = []
        self.Irr.__setitem__("Graphdata", {'x': x, 'y': y, 'x_UOM': x_uom, 'y_UOM': y_uom})

    def setTree_save_Graph(self, x, y, x_uom="", y_uom=""):
        if x is None:
            x = []
        if y is None:
            y = []
        self.Tree_save.__setitem__("Graphdata", {'x': x, 'y': y, 'x_UOM': x_uom, 'y_UOM': y_uom})

    def setTemperatureGraph(self, x, y, x_uom="", y_uom="",last_hr_temp="Nill"):
        if x is None:
            x = []
        if y is None:
            y = []
        self.Temperature.__setitem__("Graphdata", {'x': x, 'y': y, 'x_UOM': x_uom, 'y_UOM': y_uom})
        try:
         if math.isnan(last_hr_temp):
                last_hr_temp = 'nill'
        except Exception as err:
            last_hr_temp = 'nill'
        self.Temperature.__setitem__("Lasthour_Temperature", last_hr_temp)

    def setExpected_Graph(self, x, y, x_uom="", y_uom=""):
        if x is None:
            x = []
        if y is None:
            y = []
        self.Expected.__setitem__("Graphdata", {'x': x, 'y': y, 'x_UOM': x_uom, 'y_UOM': y_uom})

    def setPR_Graph(self, x, y, x_uom="", y_uom=""):
        if x is None:
            x = []
        if y is None:
            y = []
        self.PR.__setitem__("Graphdata", {'x': x, 'y': y, 'x_UOM': x_uom, 'y_UOM': y_uom})




    def setE_Generation_SummaryGraph(self, x, y, x_uom="", y_uom=""):
        if x is None:
            x = []
        if y is None:
            y = []
        self.E_Generation.__setitem__("Summary_graphdata", {'x': x, 'y': y, 'x_UOM': x_uom, 'y_UOM': y_uom})

    def setE_Consumption_SummaryGraph(self, x, y, x_uom="", y_uom=""):
        if x is None:
            x = []
        if y is None:
            y = []
        self.E_Consumption.__setitem__("Summary_graphdata", {'x': x, 'y': y, 'x_UOM': x_uom, 'y_UOM': y_uom})

    def setIrr_SummaryGraph(self, x, y, x_uom="", y_uom=""):
        if x is None:
            x = []
        if y is None:
            y = []
        self.Irr.__setitem__("Summary_graphdata", {'x': x, 'y': y, 'x_UOM': x_uom, 'y_UOM': y_uom})

    def setTree_save_SummaryGraph(self, x, y, x_uom="", y_uom=""):
        if x is None:
            x = []
        if y is None:
            y = []
        self.Tree_save.__setitem__("Summary_graphdata", {'x': x, 'y': y, 'x_UOM': x_uom, 'y_UOM': y_uom})



    def setE_Generation_summary(self,last_hour, current, l_uom = "",c_uom = ""):
        if last_hour is None:
            last_hour = 0
        if current is None:
            current = 0
        if math.isnan(last_hour):
            last_hour = "NaN"
        if math.isnan(current):
            current = "NaN"
        self.E_Generation.__setitem__('last_hr_val', last_hour)
        self.E_Generation.__setitem__('last_hr_UOM', l_uom)
        self.E_Generation.__setitem__('current_val', current)
        self.E_Generation.__setitem__('current_UOM', c_uom)

    def setE_Consumption_summary(self,last_hour, current, l_uom = "",c_uom = ""):
        if last_hour is None:
            last_hour = 0
        if current is None:
            current = 0
        if math.isnan(last_hour):
            last_hour = "NaN"
        if math.isnan(current):
            current = "NaN"
        self.E_Consumption.__setitem__('last_hr_val', last_hour)
        self.E_Consumption.__setitem__('last_hr_UOM', l_uom)
        self.E_Consumption.__setitem__('current_val', current)
        self.E_Consumption.__setitem__('current_UOM', c_uom)

    def setIrr_summary(self,last_hour, current, uom):
        if last_hour is None:
            last_hour = 0
        if current is None:
            current = 0
        if uom is None:
            uom =""
        if math.isnan(last_hour):
            last_hour = "NaN"
        if math.isnan(current):
            current = "NaN"

        self.Irr.__setitem__('last_hr_val', last_hour)
        self.Irr.__setitem__('last_hr_UOM', uom)
        self.Irr.__setitem__('current_val', current)
        self.Irr.__setitem__('current_UOM', uom)

    def setTree_save_summary(self,last_hour, current,co2, tree_uom="",co2_uom=""):
        if last_hour is None:
            last_hour = 0
        if current is None:
            current = 0
        if math.isnan(last_hour):
            last_hour = "NaN"
        if math.isnan(current):
            current = "NaN"
        if math.isnan(co2):
            co2 = "NaN"
        self.Tree_save.__setitem__('last_hr_val', last_hour)
        self.Tree_save.__setitem__('last_hr_UOM', co2_uom)
        self.Tree_save.__setitem__('current_val', current)
        self.Tree_save.__setitem__('current_UOM', tree_uom)
        self.Tree_save.__setitem__('CO2', co2)
        self.Tree_save.__setitem__('CO2_UOM', co2_uom)





