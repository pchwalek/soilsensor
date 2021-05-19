import pymongo
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdate
from pytz import timezone

import numpy as np
from scipy.signal import butter,filtfilt
import matplotlib.dates as mdates
import math
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

myclient = pymongo.MongoClient("mongodb+srv://pchwalek:rQzhQWWrpQ2qTiJ0@envsensor.vn8ke.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
mydb = myclient["envSensor"]
mycol = mydb["soilSensor"]

# x = mycol.find_one()

myresult = mycol.find().sort("epoch",-1).limit(17280) #-1 is newest to oldest while 1 is oldest to newest

#print the result:

epoch = []
SCD_30_C02 = []
SCD_30_temp = []
SCD_30_hum = []

BME680_temp = []
BME680_hum = []
BME680_pres = []
BME680_gas = []
BME680_iaq = []
BME680_iaq_acc = []
BME680_temp_fil = []
BME680_hum_fil = []
BME680_static_iaq = []
BME680_co2_eq = []
BME680_breath_voc_eq = []
si7021_temp = []
si7021_hum = []

temp_0 = []
temp_1 = []
temp_2 = []
temp_3 = []
temp_4 = []
soil_m_1 = []
soil_m_2 = []
soil_m_3 = []
SF_moist_1 = []
SF_moist_2 = []
for x in myresult:
  temp_0.append(x['temp_0'])
  temp_1.append(x['temp_1'])
  temp_2.append(x['temp_2'])
  temp_3.append(x['temp_3'])
  temp_4.append(x['temp_4'])
  soil_m_1.append(x['soil_m_1'])
  soil_m_2.append(x['soil_m_2'])
  soil_m_3.append(x['soil_m_3'])
  SF_moist_1.append(x['SF_moist_1'])
  SF_moist_2.append(x['SF_moist_2'])

  epoch.append(x['epoch'])
  SCD_30_C02.append(x['SCD30']['CO2'])
  SCD_30_temp.append(x['SCD30']['temp'])
  SCD_30_hum.append(x['SCD30']['hum'])

  BME680_temp.append(x['BME680']['temp'])
  BME680_hum.append(x['BME680']['hum'])
  BME680_pres.append(x['BME680']['pres'])
  BME680_gas.append(x['BME680']['gas'])
  BME680_iaq.append(x['BME680']['iaq'])
  BME680_iaq_acc.append(x['BME680']['iaq_acc'])
  BME680_temp_fil.append(x['BME680']['temp_fil'])
  BME680_hum_fil.append(x['BME680']['hum_fil'])
  BME680_static_iaq.append(x['BME680']['static_iaq'])
  BME680_co2_eq.append(x['BME680']['co2_eq'])
  BME680_breath_voc_eq.append(x['BME680']['breath_voc_eq'])

  si7021_temp.append(x['si7021']['temp'])
  si7021_hum.append(x['si7021']['hum'])

BME680_temp.reverse()
BME680_hum.reverse()
BME680_pres.reverse()
BME680_gas.reverse()
BME680_iaq.reverse()
BME680_iaq_acc.reverse()
BME680_temp_fil.reverse()
BME680_hum_fil.reverse()
BME680_static_iaq.reverse()
BME680_co2_eq.reverse()
BME680_breath_voc_eq.reverse()
si7021_temp.reverse()
si7021_hum.reverse()

temp_0.reverse()
temp_1.reverse()
temp_2.reverse()
temp_3.reverse()
temp_4.reverse()
soil_m_1.reverse()
soil_m_2.reverse()
soil_m_3.reverse()
SF_moist_1.reverse()
SF_moist_2.reverse()

epoch.reverse()
SCD_30_C02.reverse()
SCD_30_temp.reverse()
SCD_30_hum.reverse()


def interpolateMissingSamples(array):

  length = len(array)
  idx_1 = 0
  idx_2 = 0
  for idx, _ in enumerate(array):
    if idx == 0 or idx == (length-1):
      pass

    # interpolate if sample is missing
    if array[idx] < 0:
      array[idx] = 0

      # find first bounded value
      first_bound = 0
      for idx_1,_ in reversed(list(enumerate(array[:idx-1]))):
        if array[idx_1] > 0:
          first_bound = array[idx_1]
          break

      #find second bounded value
      second_bound = 0
      for idx_2,_ in enumerate(list(array[(idx+1):])):
        idx_2 += idx + 1
        if array[idx_2] > 0:
          second_bound = array[idx_2]
          break

      # print(str(idx) + " " + str(idx_1) + "  " + str(idx_2))
      array[idx] = (first_bound+second_bound)/2.0


plt.style.use('dark_background')

# Filter requirements for one-wire temperature sensors
T = 1440        # Sample Period (number of seconds)
fs = 0.2       # sample rate, Hz
cutoff = 0.01      # desired cutoff frequency of the filter, Hz
nyq = 0.5 * fs  # Nyquist Frequency
order = 2       # sin wave can be approx represented as quadratic
n = int(T * fs) # total number of samples

def butter_lowpass_filter(data, cutoff, fs, order):
  normal_cutoff = cutoff / nyq
  # Get the filter coefficients
  b, a = butter(order, normal_cutoff, btype='low', analog=False)
  y = filtfilt(b, a, data)
  return y

interpolateMissingSamples(temp_0)
temp_0_filtered = butter_lowpass_filter(temp_0, cutoff, fs, order)
interpolateMissingSamples(temp_1)
temp_1_filtered = butter_lowpass_filter(temp_1, cutoff, fs, order)
interpolateMissingSamples(temp_2)
temp_2_filtered = butter_lowpass_filter(temp_2, cutoff, fs, order)
interpolateMissingSamples(temp_3)
temp_3_filtered = butter_lowpass_filter(temp_3, cutoff, fs, order)
interpolateMissingSamples(temp_4)
temp_4_filtered = butter_lowpass_filter(temp_4, cutoff, fs, order)

# SCD_30_temp_filtered = butter_lowpass_filter(SCD_30_temp, cutoff, fs, order)
# BME680_temp_filtered = butter_lowpass_filter(BME680_temp, cutoff, fs, order)
# si7021_temp_filtered = butter_lowpass_filter(si7021_temp, cutoff, fs, order)



# ######################################################
# Temperature PLOTS
# ######################################################

# convert epoch to matplotlib format
secs = mdate.epoch2num(epoch)

# Choose your xtick format string
date_fmt = '%m-%d-%y %H:%M:%S'
date_formatter = mdate.DateFormatter(date_fmt, tz=timezone('US/Eastern'),)
fig, ax = plt.subplots(figsize=(40,10), dpi= 80)

ax.plot(secs, temp_0_filtered,  label='DS18B20 (52mm from center, 198mm deep)',linestyle='solid',marker='')
ax.plot(secs,temp_1_filtered, label='DS18B20 (138mm from center, 198mm deep)',linestyle='solid',marker='')
ax.plot(secs,temp_2_filtered, label='DS18B20 (52mm from center, 25mm deep)',linestyle='solid',marker='')
ax.plot(secs,temp_3_filtered, label='DS18B20 (138mm from center, 25mm deep)',linestyle='solid',marker='')
ax.plot(secs,temp_4_filtered, label='DS18B20 (external)',linestyle='solid',marker='')

ax.plot(secs,SCD_30_temp,label='SCD30 (external)',linestyle='solid',marker='')
ax.plot(secs,BME680_temp_fil,label='BME680 (external)',linestyle='solid',marker='')
ax.plot(secs,si7021_temp,label='SI7021 (external)',linestyle='solid',marker='')

# Use a DateFormatter to set the data to the correct format.
ax.xaxis.set_major_formatter(date_formatter)

# Sets the tick labels diagonal so they fit easier.
fig.autofmt_xdate()

# Decorations
# plt.tick_params(axis="both", which="both", bottom=False, top=False,
#                 labelbottom=True, left=False, right=False, labelleft=True)

ax.grid()
ax.legend(prop={'size': 10})
plt.xlabel("Time", fontsize=20)
plt.ylabel("Temperature (C)", fontsize=20)
# plt.title("Temperature", fontsize=22)
plt.gca().spines["top"].set_alpha(0.0)
plt.gca().spines["bottom"].set_alpha(0.5)
plt.gca().spines["right"].set_alpha(0.0)
plt.gca().spines["left"].set_alpha(0.5)


# Major ticks every 1 hr.
fmt_major_hour = mdates.HourLocator(interval=4)
ax.xaxis.set_major_locator(fmt_major_hour)

# Minor ticks every 30 minutes.
fmt_minor_hour = mdates.HourLocator(interval=1)
ax.xaxis.set_minor_locator(fmt_minor_hour)

ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.grid(True, which='minor')


plt.grid(b=True, which='minor', color='w', linestyle='-', alpha=0.2)
# plt.minorticks_on()
# ax.xaxis.set_minor_locator(AutoMinorLocator())
#
# ax.tick_params(which='both', width=2)
# ax.tick_params(which='major', length=7)
# ax.tick_params(which='minor', length=4, color='r')
plt.show()

# ######################################################
# Capacitive Soil Moisture PLOTS
# ######################################################

soil_m_1_filtered = butter_lowpass_filter(soil_m_1, cutoff, fs, order)
soil_m_2_filtered = butter_lowpass_filter(soil_m_2, cutoff, fs, order)
soil_m_3_filtered = butter_lowpass_filter(soil_m_3, cutoff, fs, order)

fig, ax = plt.subplots(figsize=(40,10), dpi= 80)
ax.plot(secs,soil_m_1_filtered, label='EC-5 (52mm from center, 25mm deep)')
ax.plot(secs,soil_m_2_filtered, label='EC-5 (138mm from center, 25mm deep)')
ax.plot(secs,soil_m_3_filtered, label='VH400 (138mm from center, 25mm deep)')
# Use a DateFormatter to set the data to the correct format.
ax.xaxis.set_major_formatter(date_formatter)

# Sets the tick labels diagonal so they fit easier.
fig.autofmt_xdate()

# Decorations
plt.tick_params(axis="both", which="both", bottom=False, top=False,
                labelbottom=True, left=False, right=False, labelleft=True)
ax.grid()
ax.legend(prop={'size': 10})
plt.gca().spines["top"].set_alpha(0.0)
plt.gca().spines["bottom"].set_alpha(0.5)
plt.gca().spines["right"].set_alpha(0.0)
plt.gca().spines["left"].set_alpha(0.5)
plt.xlabel("Time", fontsize=20)
plt.ylabel("ADC Readings (12-bit @ 3.3V)", fontsize=20)
# Major ticks every 1 hr.
fmt_major_hour = mdates.HourLocator(interval=4)
ax.xaxis.set_major_locator(fmt_major_hour)

# Minor ticks every 30 minutes.
fmt_minor_hour = mdates.HourLocator(interval=1)
ax.xaxis.set_minor_locator(fmt_minor_hour)

ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.grid(True, which='minor')


plt.grid(b=True, which='minor', color='w', linestyle='-', alpha=0.2)
plt.show()
#
# # http://publications.metergroup.com/Manuals/20431_EC-5_Manual_Web.pdf
# #   this equation is for 2.5V excitation but we are doing 3.3V excitation
# def vwc_conversion(array):
#   temps = np.array(array)
#   vwc = (11.9 * math.pow(10,-4)) * (temps/4096.) - 0.401
#   return vwc
#
#
# soil_m_1_filtered_vwc = vwc_conversion(soil_m_1_filtered)
# soil_m_2_filtered_vwc = vwc_conversion(soil_m_2_filtered)
# fig, ax = plt.subplots(figsize=(40,10), dpi= 80)
# ax.plot(soil_m_1_filtered_vwc, label='soil_m_1_vwc')
# ax.plot(soil_m_2_filtered_vwc, label='soil_m_2_vwc')
# ax.grid()
# ax.legend()
# plt.gca().spines["top"].set_alpha(0.0)
# plt.gca().spines["bottom"].set_alpha(0.5)
# plt.gca().spines["right"].set_alpha(0.0)
# plt.gca().spines["left"].set_alpha(0.5)
# plt.show()

# ######################################################
# SparkFun Resistive Moisture Sensor PLOTS
# ######################################################

# Filter requirements for SparkFun soil moisture sensor
T_sf = 1440        # Sample Period (number of seconds)
fs_sf = 0.2       # sample rate, Hz
cutoff_sf = 0.0005      # desired cutoff frequency of the filter, Hz
nyq_sf = 0.5 * fs_sf  # Nyquist Frequency
order_sf = 2       # sin wave can be approx represented as quadratic
n_sf = int(T_sf * fs_sf) # total number of samples


SF_moist_1_filtered = butter_lowpass_filter(SF_moist_1, cutoff_sf, fs_sf, order_sf)
SF_moist_2_filtered = butter_lowpass_filter(SF_moist_2, cutoff_sf, fs_sf, order_sf)
fig, ax = plt.subplots(figsize=(40,10), dpi= 80)
ax.plot(secs,SF_moist_1_filtered, label='SparkFun Probe 1 (138mm from center)')
ax.plot(secs,SF_moist_2_filtered, label='SparkFun Probe 2 (52mm from center)')
# Use a DateFormatter to set the data to the correct format.
ax.xaxis.set_major_formatter(date_formatter)

# Sets the tick labels diagonal so they fit easier.
fig.autofmt_xdate()

# Decorations
plt.tick_params(axis="both", which="both", bottom=False, top=False,
                labelbottom=True, left=False, right=False, labelleft=True)
ax.grid()
ax.legend(prop={'size': 10})
plt.gca().spines["top"].set_alpha(0.0)
plt.gca().spines["bottom"].set_alpha(0.5)
plt.gca().spines["right"].set_alpha(0.0)
plt.gca().spines["left"].set_alpha(0.5)
plt.xlabel("Time", fontsize=20)
plt.ylabel("ADC Readings (12-bit @ 3.3V)", fontsize=20)
# Major ticks every 1 hr.
fmt_major_hour = mdates.HourLocator(interval=4)
ax.xaxis.set_major_locator(fmt_major_hour)

# Minor ticks every 30 minutes.
fmt_minor_hour = mdates.HourLocator(interval=1)
ax.xaxis.set_minor_locator(fmt_minor_hour)

ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.grid(True, which='minor')


plt.grid(b=True, which='minor', color='w', linestyle='-', alpha=0.2)
plt.show()



# ######################################################
# CO2 PLOTS
# ######################################################

fig, ax = plt.subplots(figsize=(40,10), dpi= 80)
ax.plot(secs,SCD_30_C02, label='SCD30')
ax.plot(secs,BME680_co2_eq, label='BME680 (CO2 EQ)')
# Use a DateFormatter to set the data to the correct format.
ax.xaxis.set_major_formatter(date_formatter)

# Sets the tick labels diagonal so they fit easier.
fig.autofmt_xdate()

# Decorations
plt.tick_params(axis="both", which="both", bottom=False, top=False,
                labelbottom=True, left=False, right=False, labelleft=True)
ax.grid()
ax.legend(prop={'size': 10})
plt.gca().spines["top"].set_alpha(0.0)
plt.gca().spines["bottom"].set_alpha(0.5)
plt.gca().spines["right"].set_alpha(0.0)
plt.gca().spines["left"].set_alpha(0.5)
plt.xlabel("Time", fontsize=20)
plt.ylabel("CO2 (PPM)", fontsize=20)
# Major ticks every 1 hr.
fmt_major_hour = mdates.HourLocator(interval=4)
ax.xaxis.set_major_locator(fmt_major_hour)

# Minor ticks every 30 minutes.
fmt_minor_hour = mdates.HourLocator(interval=1)
ax.xaxis.set_minor_locator(fmt_minor_hour)

ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.grid(True, which='minor')


plt.grid(b=True, which='minor', color='w', linestyle='-', alpha=0.2)
plt.show()


# ######################################################
# HUMIDITY PLOTS
# ######################################################

fig, ax = plt.subplots(figsize=(40,10), dpi= 80)
ax.plot(secs,si7021_hum, label='SI7021')
ax.plot(secs,SCD_30_hum, label='SCD30')
ax.plot(secs,BME680_hum_fil, label='BME680')
# Use a DateFormatter to set the data to the correct format.
ax.xaxis.set_major_formatter(date_formatter)

# Sets the tick labels diagonal so they fit easier.
fig.autofmt_xdate()

# Decorations
plt.tick_params(axis="both", which="both", bottom=False, top=False,
                labelbottom=True, left=False, right=False, labelleft=True)
ax.grid()
ax.legend(prop={'size': 10})
plt.gca().spines["top"].set_alpha(0.0)
plt.gca().spines["bottom"].set_alpha(0.5)
plt.gca().spines["right"].set_alpha(0.0)
plt.gca().spines["left"].set_alpha(0.5)
plt.xlabel("Time", fontsize=20)
plt.ylabel("Humidity (%)", fontsize=20)
# Major ticks every 1 hr.
fmt_major_hour = mdates.HourLocator(interval=4)
ax.xaxis.set_major_locator(fmt_major_hour)

# Minor ticks every 30 minutes.
fmt_minor_hour = mdates.HourLocator(interval=1)
ax.xaxis.set_minor_locator(fmt_minor_hour)

ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.grid(True, which='minor')


plt.grid(b=True, which='minor', color='w', linestyle='-', alpha=0.2)
plt.show()


# ######################################################
# VOC PLOTS
# ######################################################

fig, ax = plt.subplots(figsize=(40,10), dpi= 80)
ax.plot(secs,BME680_breath_voc_eq, label='BME680 Breath VOC')
# Use a DateFormatter to set the data to the correct format.
ax.xaxis.set_major_formatter(date_formatter)

# Sets the tick labels diagonal so they fit easier.
fig.autofmt_xdate()

# Decorations
plt.tick_params(axis="both", which="both", bottom=False, top=False,
                labelbottom=True, left=False, right=False, labelleft=True)
ax.grid()
ax.legend(prop={'size': 10})
plt.gca().spines["top"].set_alpha(0.0)
plt.gca().spines["bottom"].set_alpha(0.5)
plt.gca().spines["right"].set_alpha(0.0)
plt.gca().spines["left"].set_alpha(0.5)
plt.xlabel("Time", fontsize=20)
plt.ylabel("VOC", fontsize=20)
# Major ticks every 1 hr.
fmt_major_hour = mdates.HourLocator(interval=4)
ax.xaxis.set_major_locator(fmt_major_hour)

# Minor ticks every 30 minutes.
fmt_minor_hour = mdates.HourLocator(interval=1)
ax.xaxis.set_minor_locator(fmt_minor_hour)

ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.grid(True, which='minor')


plt.grid(b=True, which='minor', color='w', linestyle='-', alpha=0.2)
plt.show()


# ######################################################
# PRESSURE PLOTS
# ######################################################

fig, ax = plt.subplots(figsize=(40,10), dpi= 80)
ax.plot(secs,BME680_pres, label='BME680')
# Use a DateFormatter to set the data to the correct format.
ax.xaxis.set_major_formatter(date_formatter)

# Sets the tick labels diagonal so they fit easier.
fig.autofmt_xdate()

# Decorations
plt.tick_params(axis="both", which="both", bottom=False, top=False,
                labelbottom=True, left=False, right=False, labelleft=True)
ax.grid()
ax.legend(prop={'size': 10})
plt.gca().spines["top"].set_alpha(0.0)
plt.gca().spines["bottom"].set_alpha(0.5)
plt.gca().spines["right"].set_alpha(0.0)
plt.gca().spines["left"].set_alpha(0.5)
plt.xlabel("Time", fontsize=20)
plt.ylabel("Pressure (hPa)", fontsize=20)
# Major ticks every 1 hr.
fmt_major_hour = mdates.HourLocator(interval=4)
ax.xaxis.set_major_locator(fmt_major_hour)

# Minor ticks every 30 minutes.
fmt_minor_hour = mdates.HourLocator(interval=1)
ax.xaxis.set_minor_locator(fmt_minor_hour)

ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.grid(True, which='minor')


plt.grid(b=True, which='minor', color='w', linestyle='-', alpha=0.2)
plt.show()


# ######################################################
# PRESSURE PLOTS
# ######################################################

fig, ax = plt.subplots(figsize=(40,10), dpi= 80)
ax.plot(secs,BME680_iaq, label='BME680 IAQ')
ax.plot(secs,BME680_static_iaq, label='BME680 Static IAQ')
# Use a DateFormatter to set the data to the correct format.
ax.xaxis.set_major_formatter(date_formatter)

# Sets the tick labels diagonal so they fit easier.
fig.autofmt_xdate()

# Decorations
plt.tick_params(axis="both", which="both", bottom=False, top=False,
                labelbottom=True, left=False, right=False, labelleft=True)
ax.grid()
ax.legend(prop={'size': 10})
plt.gca().spines["top"].set_alpha(0.0)
plt.gca().spines["bottom"].set_alpha(0.5)
plt.gca().spines["right"].set_alpha(0.0)
plt.gca().spines["left"].set_alpha(0.5)
plt.xlabel("Time", fontsize=20)
plt.ylabel("Index of Air Quality (IAQ)", fontsize=20)
# Major ticks every 1 hr.
fmt_major_hour = mdates.HourLocator(interval=4)
ax.xaxis.set_major_locator(fmt_major_hour)

# Minor ticks every 30 minutes.
fmt_minor_hour = mdates.HourLocator(interval=1)
ax.xaxis.set_minor_locator(fmt_minor_hour)

ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.grid(True, which='minor')


plt.grid(b=True, which='minor', color='w', linestyle='-', alpha=0.2)
plt.show()
