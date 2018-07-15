# ****************************************************
#  Project : Iot
#  Filename: controllers.py
#  Created : sv
#  Change history:
#  dd.mm.yyyy / developer name
#  18.02.2018 / sv
# ***************************************************
#   creating prescription  Controller
# ****************************************************

# Import flask dependencies
class Util():

    INV = "INVERTER"
    DPM = "DPM"
    IRR = "IRR"
    Solar = "Solar"

    @staticmethod
    def toJson(u):
        json_res = {}
        for i in u.keys():
            json_res.__setitem__(i, u[i])
        return json_res
