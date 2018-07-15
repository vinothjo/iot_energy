class Location:
    def __init__(self,zone,area,postal_code,blk,longitude,latitude,energygenrated,energyConsumed,helthy="true"
                 ,commStatus="90%",AlrmsStatus="true", temperature="true",Hours=23232.2132,voltage =43243.232 ,PF = 432432.24324):
        self.zone = zone
        self.area = area
        self.postal_code = postal_code
        self.blk = blk
        self.longitude = longitude
        self.latitude = latitude
        self.energygenrated = energygenrated
        self.energyConsumed = energyConsumed
        self.helthy = helthy
        self.commStatus = commStatus
        self.AlrmsStatus = AlrmsStatus
        self.temperature = temperature
        self.Hours = Hours
        self.voltage = voltage
        self.PF = PF
