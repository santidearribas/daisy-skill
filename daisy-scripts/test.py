from datetime import datetime

myFile = open("test-logs.txt", 'a')
myFile.write('\nAccessed on ' + str(datetime.now()))
