import time,sys

# Spinning cursor
def spinning_cursor():
  while True:
    for cursor in '\\|/-':
      time.sleep(0.1)
      # Use '\r' to move cursor back to line beginning
      # Or use '\b' to erase the last character
      sys.stdout.write('\r{}'.format(cursor))
      # Force Python to write data into terminal.
      sys.stdout.flush()
      
spinning_cursor()