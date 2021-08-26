class bufferDrone():
    def __init__(self, ID ):
        self.ID          = int(ID)
        self.name        = 'bufferDrone'+str(ID)
        
        self.requested_X            = 0.0
        self.requested_Y            = 0.0
        self.requested_Z            = 0.0
        self.requested_R            = 0.0
        self.requested_G            = 0.0
        self.requested_B            = 0.0
        self.yaw                   = 0.0



gino = bufferDrone(2)

var = 'Y'

proprietà = 'requested_' + var

setattr(gino,proprietà,3)
print (getattr(gino,proprietà))