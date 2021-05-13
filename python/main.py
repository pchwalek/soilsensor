import json
import serial
import sys
import time
import pymongo
import ssl



# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

DATA_DIRECTORY = "C:\\Users\\patri\\OneDrive\\Desktop\\"


# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def soil_sensor_logger():

    print("Soil Sensor Logger Started")
    client = pymongo.MongoClient(
        "mongodb+srv://pchwalek:rQzhQWWrpQ2qTiJ0@envsensor.vn8ke.mongodb.net/envsensor?retryWrites=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)
    mydb = client["envSensor"]
    mySoilSensor = mydb["soilSensor"]
    #
    # client.server_info()

    ser = serial.Serial(
        port='COM3', \
        baudrate=115200)

    while True:
        try:
            # grab data from serial USB
            line = ser.readline()

            # parse json
            data = json.loads(line)
            data["epoch"] = time.time()

            print(data["idx"])
            # print(data["temp_1"])

            # write to file
            with open(DATA_DIRECTORY + 'soil_sensor_log.txt', 'a') as outfile:
                json.dump(data, outfile)
                outfile.write("\n")

            # write to database
            x = mySoilSensor.insert_one(data)
        except pymongo.errors.ServerSelectionTimeoutError as err:
            # do whatever you need
            print(err)
            break
        except json.decoder.JSONDecodeError as err:
            print(err)
            print(line)
            continue
        except:
            print("EXCEPTION")
            print(sys.exc_info()[0])
            ser.close()
            break


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    soil_sensor_logger()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
