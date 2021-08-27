from datetime import datetime
from timecode import Timecode
from pathlib import Path
import os
import json

registrazione = './marconio.json'
nomeRegistrazione = Path(registrazione).stem
OUTPUT_DIR        = 'ciessevui'
if not Path(OUTPUT_DIR).exists():
  os.mkdir(OUTPUT_DIR)
os.chdir(OUTPUT_DIR)
if not Path(nomeRegistrazione).exists():
  os.mkdir(nomeRegistrazione)
os.chdir('..')
startTime = 0
dataDiOggi = datetime.today()
drogni  =  3
framerate = 25
durataFrame = 1000 / 25 / 1000


def convertimiInQualcosaDiLeggibile(robaIllegibile):
  seconds     =  float(str(robaIllegibile).split('.')[0]) - 2208988800
  nanoseconds =  float(str(robaIllegibile).split('.')[1])
  milliseconds = nanoseconds / 1000000
  laData = [seconds, milliseconds]
  return laData


with open(registrazione) as f:
  data = json.load(f)
  carlo = 0
  for i in data.keys():
    carlo = data[i]['timestamps'][0]
    break
  startTime = convertimiInQualcosaDiLeggibile(carlo)[0]
  for drogno in data:
    # print (drogno)
    coordinate = data[drogno]['samples']

    filepath =  os.path.join( OUTPUT_DIR, "{}/timed_waypoints_drogno_{}.csv".format(nomeRegistrazione, str(drogno)[-5:-4]))
    print (filepath)
    with open(filepath, "w") as f:
      for i in range(len(coordinate)):
        riga = str(durataFrame)+',' + str(coordinate[i][1]) + ',' + str(coordinate[i][2]) + ',' + str(coordinate[i][3]) + '\n'
        f.write(riga)
        # print(riga)

# os.path.j
# capture_osc -f ./nomefile -p 9200
 

