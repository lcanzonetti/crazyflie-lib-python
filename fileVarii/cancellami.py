import tai64n as cazzo
from datetime import datetime
from collections import OrderedDict
from timecode import Timecode

startTime = 0


def convertimiInQualcosaDiLeggibile(robaIllegibile):
    seconds     =  float(str(robaIllegibile).split('.')[0]) - 2208988800
    nanoseconds =  float(str(robaIllegibile).split('.')[1])
    milliseconds = nanoseconds / 1000000

    laData = [seconds, milliseconds]
    # robba = epoch + timedelta(microseconds=laData)

    # gino = str (robba)
    # gino = cazzo.decode(robaIllegibile)
    return laData
    


import json

with open('./minchio.json') as f:
  data = json.load(f)
  carlo = 0
  for i in data.keys():
    carlo = data[i]['timestamps'][0]
    break
  startTime = convertimiInQualcosaDiLeggibile(carlo)[0]
  for drogno in data:
    # print (drogno)
    for i in range(len (data[drogno]['timestamps'])):
      convo           = convertimiInQualcosaDiLeggibile(data[drogno]['timestamps'][i])
      print (convo[0])
      convoOffsettato = convo[0] - startTime
      convoTimecodato = Timecode('25', convoOffsettato)
      robaCheFlotta   = Timecode('25', '00:01:00:00')
      merda = convoTimecodato + robaCheFlotta
    #   assert tc8.frame_number == 1
      
      print ('merda merda merda merda %s' + repr(merda))

    #   print('%s - %s' % (round(convoTimecodato, data[drogno]['samples'][i])))
