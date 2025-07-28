import openpyxl
from openpyxl.chart import ScatterChart, Reference, Series # type: ignore
# from openpyxl.chart.series import Series
import datetime
from math import floor
import time
import matplotlib.pyplot as plt
from datetime import date
from datetime import datetime
import threading
import os
import pandas as pd
import tabulate
import math


class DataStorage:

    def __init__(self) -> None:
        # Empty arrays for data
        self.time = []
        self.volts = []
        self.current = []
        self.power = []
        self.capacity = []

    # Function to add time value
    def addTime(self, Mtime_sec: float):
        self.time.append(float('{:.4f}'.format(Mtime_sec)))

    # Function to add voltage value
    def addVoltage(self, votls: float):
        self.volts.append(float('{:.4f}'.format(votls)))

    # Function to add current value
    def addCurrent(self, ampers: float):
        self.current.append(float('{:.4f}'.format(ampers)))

    def addCapacity(self, ah: float):
        """Store capacity value in ampere-hours."""
        self.capacity.append(float('{:.4f}'.format(ah)))

    # Function for creating a table
    def createTable(self, testName, c_rate: float, cycleNr: int, temperature: float, timeInterval: float, chargeTime=0):
        # Get the number of measurements
        length = len(self.volts)
        # Fill in power list with voltage and current values
        for i in range(length):
            self.power.append(self.volts[i] * self.current[i])
        # Create a 2 dimensional list for the data
        # Start with an empty list.  The previous implementation initialised the
        # data list with an empty inner list which resulted in an extra row of
        # NaNs when creating the DataFrame.
        data = []
        # Fill the list with the results
        include_capacity = len(self.capacity) == len(self.volts) and len(self.capacity) > 0
        for j in range(len(self.volts)):
            d = [float(j) * timeInterval, self.time[j],
                 self.volts[j], self.current[j], self.power[j]]
            if include_capacity:
                d.append(self.capacity[j])
            data.append(d)
        head = ["Time in seconds", "time", "Volts", "Current", "Power"]
        if include_capacity:
            head.append("Capacity")
        # Store the table in a text file
        today = date.today()
        try:
            # Find the absolute path to the current file
            abs_path = os.path.abspath("").replace("\\", "/")
            # Use the absolute path to create a path to the Data folder
            data_dir = f"{abs_path}/Data"
            os.makedirs(data_dir, exist_ok=True)
            filePath = f"{data_dir}/{testName}_{c_rate}C_#{cycleNr + 1}_@{temperature}°C_" +\
            str(datetime.now().strftime("%d.%m.%y_%H;%M"))
            # Display the Path for debug purposes
            print(abs)
            # Export to CSV file
            self.exportCSVFile(filePath, data, head)
            # Export to XLSX file
            print(filePath)
            print("filePath just now")
            self.exportXLSXFile(filePath, chargeTime, timeInterval)
            print("export xlsx file just now")
            print(f"Charge time is: {chargeTime}")
        except:
            print("Data storage failed, check file path")
        # Empty the result values
        self.time = []
        self.volts = []
        self.current = []
        self.power = []
        self.capacity = []

    def exportCSVFile(self, filePath, data, head):
        df = pd.DataFrame(data, columns=head)
        df.to_csv(filePath + ".csv", index=False)

    def exportXLSXFile(self, filePath, chargeTime, timeInterval):
        # Read in our csv file
        csvDataframe = pd.read_csv(filePath + ".csv")
        # Create our excel file
        xlsxDataframe = pd.ExcelWriter(filePath + ".xlsx", engine='openpyxl')
        # Write from csv to excel
        csvDataframe.to_excel(xlsxDataframe, index=False)
        # Save our excel file
        xlsxDataframe.close()

        # Open up our excel file as a work book
        wb = openpyxl.load_workbook(filePath + ".xlsx")
        # Access the sheet
        sheet = wb.active
        
        # Ensure sheet is not None
        if sheet is None:
            sheet = wb.worksheets[0]

        # Only create generic graphs when no dedicated charge time is provided
        if chargeTime == 0:
            # Create a list of Values to graph
            seconds = Reference(sheet, min_col=1, min_row=3,
                                max_col=1, max_row=len(csvDataframe))
            voltage = Reference(sheet, min_col=3, min_row=3,
                                max_col=3, max_row=len(csvDataframe))
            current = Reference(sheet, min_col=4, min_row=3,
                                max_col=4, max_row=len(csvDataframe))
            power = Reference(sheet, min_col=5, min_row=3,
                              max_col=5, max_row=len(csvDataframe))

            # Create a graph for the Voltage
            voltageChart = ScatterChart()
            voltageSeries = Series(voltage, seconds, title_from_data=True)
            voltageChart.series.append(voltageSeries)
            voltageChart.title = "Voltage over Time"
            voltageChart.x_axis.title = "Time [s]"
            # Label the y-axis correctly instead of overwriting the x-axis title
            voltageChart.y_axis.title = "Voltage [V]"

            # Create a graph for the Current
            currentChart = ScatterChart()
            currentSeries = Series(current, seconds, title_from_data=True)
            currentChart.series.append(currentSeries)
            currentChart.title = "Current over Time"
            currentChart.x_axis.title = "Time [s]"
            currentChart.y_axis.title = "Current [mA]"

            # Create a graph for the Power
            powerChart = ScatterChart()
            powerSeries = Series(power, seconds, title_from_data=True)
            powerChart.series.append(powerSeries)
            powerChart.title = "Power over Time"
            powerChart.x_axis.title = "Time [s]"
            powerChart.y_axis.title = "Power [W]"

            # Add our graphs to the sheet
            voltageChart.anchor = "E2"
            sheet.add_chart(voltageChart)
            currentChart.anchor = "E22"
            sheet.add_chart(currentChart)
            powerChart.anchor = "E42"
            sheet.add_chart(powerChart)

        else:  # This is used normally
            # Create a list of Values to graph
            seconds = Reference(sheet, min_col=2, min_row=3,
                                max_col=2, max_row=len(csvDataframe))
            print(f"Charge time: {chargeTime}")
            print(f"Time interval:  {timeInterval}")
            voltageCharging = Reference(sheet, min_col=3, min_row=3, max_col=3, max_row=int(
                (float(chargeTime) * 60) / float(timeInterval)))
            currentCharging = Reference(sheet, min_col=4, min_row=3, max_col=4, max_row=int(
                (float(chargeTime) * 60) / float(timeInterval)))
            powerCharging = Reference(sheet, min_col=5, min_row=3, max_col=5, max_row=int(
                (float(chargeTime) * 60) / float(timeInterval)))

            voltageDischarging = Reference(sheet, min_col=3, min_row=int((float(
                chargeTime) * 60) / float(timeInterval) + 1), max_col=3, max_row=len(csvDataframe))
            currentDischarging = Reference(sheet, min_col=4, min_row=int((float(
                chargeTime) * 60) / float(timeInterval) + 1), max_col=4, max_row=len(csvDataframe))
            powerDischarging = Reference(sheet, min_col=5, min_row=int((float(
                chargeTime) * 60) / float(timeInterval) + 1), max_col=5, max_row=len(csvDataframe))
            ## CHARGING GRAPHS ##
            # Create a graph for the Voltage during Charging
            voltageChartCharging = ScatterChart()
            voltageChartCharging.legend = None
            voltageSeriesCharging = Series(
                voltageCharging, seconds, title_from_data=False)
            voltageChartCharging.series.append(voltageSeriesCharging)
            voltageChartCharging.title = f"Voltage during charging ({chargeTime} s)"
            voltageChartCharging.x_axis.tickLblPos = "low"
            voltageChartCharging.x_axis.title = "Time [s]"
            voltageChartCharging.y_axis.title = "Voltage [V]"

            # Create a graph for the Current during Charging
            currentChartCharging = ScatterChart()
            currentChartCharging.legend = None
            currentSeriesCharging = Series(
                currentCharging, seconds, title_from_data=False)
            currentChartCharging.series.append(currentSeriesCharging)
            currentChartCharging.title = f"Current during charging ({chargeTime} s)"
            currentChartCharging.x_axis.tickLblPos = "low"
            currentChartCharging.x_axis.title = "Time [s]"
            currentChartCharging.y_axis.title = "Current [mA]"

            # Create a graph for the Power during Charging
            powerChartCharging = ScatterChart()
            powerChartCharging.legend = None
            powerSeriesCharging = Series(
                powerCharging, seconds, title_from_data=False)
            powerChartCharging.series.append(powerSeriesCharging)
            powerChartCharging.title = f"Power during charging ({chargeTime} s)"
            powerChartCharging.x_axis.tickLblPos = "low"
            powerChartCharging.x_axis.title = "Time [s]"
            powerChartCharging.y_axis.title = "Power [W]"
            ## DISCHARGING GRAPHS ##
            # Create a graph for the Voltage during Disharging
            voltageChartDischarging = ScatterChart()
            voltageChartDischarging.legend = None
            voltageSeriesDischarging = Series(
                voltageDischarging, seconds, title_from_data=False)
            voltageChartDischarging.series.append(voltageSeriesDischarging)
            voltageChartDischarging.title = "Voltage during discharging (" + str(float(math.ceil(
                (len(csvDataframe) - 2) * float(timeInterval)) / 60 - float(chargeTime))) + " s)"
            voltageChartDischarging.x_axis.tickLblPos = "low"
            voltageChartDischarging.x_axis.title = "Time [s]"
            voltageChartDischarging.y_axis.title = "Voltage [V]"

            # Create a graph for the Current during Disharging
            currentChartDischarging = ScatterChart()
            currentChartDischarging.legend = None
            currentSeriesDischarging = Series(
                currentDischarging, seconds, title_from_data=False)
            currentChartDischarging.series.append(currentSeriesDischarging)
            currentChartDischarging.title = "Current during discharging (" + str(float(math.ceil(
                (len(csvDataframe) - 2) * float(timeInterval)) / 60 - float(chargeTime))) + " s)"
            currentChartDischarging.x_axis.tickLblPos = "low"
            currentChartDischarging.x_axis.title = "Time [s]"
            currentChartDischarging.y_axis.title = "Current [mA]"

            # Create a graph for the Power during Discharging
            powerChartDischarging = ScatterChart()
            powerChartDischarging.legend = None
            powerSeriesDischarging = Series(
                powerDischarging, seconds, title_from_data=False)
            powerChartDischarging.series.append(powerSeriesDischarging)
            powerChartDischarging.title = "Power during discharging (" + str(float(math.ceil(
                (len(csvDataframe) - 2) * float(timeInterval)) / 60 - float(chargeTime))) + " s)"
            powerChartDischarging.x_axis.tickLblPos = "low"
            powerChartDischarging.x_axis.title = "Time [s]"
            powerChartDischarging.y_axis.title = "Power [W]"

            # Add our graphs to the sheet
            voltageChartCharging.anchor = "F2"
            sheet.add_chart(voltageChartCharging)
            currentChartCharging.anchor = "F22"
            sheet.add_chart(currentChartCharging)
            powerChartCharging.anchor = "F42"
            sheet.add_chart(powerChartCharging)

            voltageChartDischarging.anchor = "P2"
            sheet.add_chart(voltageChartDischarging)
            currentChartDischarging.anchor = "P22"
            sheet.add_chart(currentChartDischarging)
            powerChartDischarging.anchor = "P42"
            sheet.add_chart(powerChartDischarging)

        wb.save(filePath + ".xlsx")

    

    

# Notað til að keyra sjálfvirk gröf á utanaðkomandi csv skrár
# dataStorage = DataStorage()
# dataStorage.exportXLSXFile("C:/Users/runson/Dropbox/Sharing/Alor test/UPS Test for 1C nr. 2 at 20° celsius     03_01_2023 15_21_10",chargeTime="180",timeInterval=0.2)
