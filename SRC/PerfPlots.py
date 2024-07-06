#!/usr/bin/env python

########################################################################
# PEPPUS/SRC/PerfPlots.py:
# This is the PerfPlots Module of PEPPUS tool
#
#  Project:        PEPPUS
#  File:           PerfPlots.py
#  Date(YY/MM/DD): 06/07/2024
#
#   Author: Alexis Díaz López
#
#
########################################################################

import sys, os

from pandas import read_csv
from InputOutput import PerfIdx, XpeIdx
sys.path.append(os.getcwd() + '/' + \
    os.path.dirname(sys.argv[0]) + '/' + 'COMMON')
from COMMON.Plots import generatePlot

def initPlot(PerfFile, PlotConf, Title, Label):
    PerfFileName = os.path.basename(PerfFile)
    PerfFileNameSplit = PerfFileName.split('_')
    Rcvr = PerfFileNameSplit[1]
    DatepDat = PerfFileNameSplit[2]
    Date = DatepDat.split('.')[0]
    Year = Date[1:3]
    Doy = Date[4:]

    if "xLabel" not in PlotConf:
        PlotConf["xLabel"] = "Hour of Day %s" % Doy

    PlotConf["Title"] = "%s on Year %s"\
        " DoY %s" % (Title, Year, Doy)

    PlotConf["Path"] = sys.argv[1] + '/OUT/PERF/figures/%s/' % Label + \
        '%s_Y%sD%s.png' % (Label, Year, Doy)

def initXpePlot(PosFile, PlotConf, Title, Label):
    PosFileName = os.path.basename(PosFile)
    PosFileNameSplit = PosFileName.split('_')
    Rcvr = PosFileNameSplit[1]
    DatepDat = PosFileNameSplit[2]
    Date = DatepDat.split('.')[0]
    Year = Date[1:3]
    Doy = Date[4:]

    if "xLabel" not in PlotConf:
        PlotConf["xLabel"] = "Hour of Day %s" % Doy

    PlotConf["Title"] = "%s %s on Year %s"\
        " DoY %s" % (Rcvr, Title, Year, Doy)

    PlotConf["Path"] = sys.argv[1] + '/OUT/PERF/figures/%s/' % Label + \
        '%s_%s_Y%sD%s.png' % (Label, Rcvr, Year, Doy)
    

# Plot Confg
cfg = {
    # PERF MAPS
    "CONVT"        : 1,
    "HPE-RMS"      : 1,
    "VPE-RMS"      : 1,
    "HPE95"        : 1,
    "VPE95"        : 1,
    "NSVMIN"       : 1,
    "NSVMAX"       : 1,
    "PDOPMAX"      : 1,
    "HDOPMAX"      : 1,
    "VDOPMAX"      : 1,
    # HIST
    "HPE-HIST"     : 1,
    "VPE-HIST"     : 1
}

def plotCONVT():
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "Convergence Time" 

    PlotConf["LonMin"] = -35
    PlotConf["LonMax"] = 40
    PlotConf["LatMin"] = 10
    PlotConf["LatMax"] = 90
    PlotConf["LonStep"] = 5
    PlotConf["LatStep"] = 5

    PlotConf["yLim"] = [PlotConf["LatMin"], PlotConf["LatMax"]]
    PlotConf["xLabel"] = ""
    PlotConf["xLim"] = [PlotConf["LonMin"], PlotConf["LonMax"]]

    PlotConf["AlignAxes"] = True

    PlotConf["Grid"] = True

    PlotConf["Map"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 5

    PlotConf["ColorBar"] = "rainbow"
    PlotConf["ColorBarLabel"] = "Convergence Time [s]"

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    PlotConf["RcvrTag"] = {}
    Label = 0

    # Annotate
    PlotConf["Annotate"] = True
    PlotConf["xPosText"] = 1
    PlotConf["yPosText"] = 2.5
    PlotConf["AnnFontSize"] = 4


    # Path to the Perf Files
    path = sys.argv[1] + '/OUT/PERF/'
    PerfFile = None

    # Loop over all the Perf Files
    for file_name in os.listdir(path):
        if "PERF_" in file_name:
            PerfFile = path+file_name

            PerfData = read_csv(PerfFile, delim_whitespace=True, skiprows=1, header=None,\
            usecols=[PerfIdx["RCVR"], PerfIdx["LONREF"], PerfIdx["LATREF"], PerfIdx["CONVT"]])

            PlotConf["xData"][Label] = PerfData[PerfIdx["LONREF"]]
            PlotConf["yData"][Label] = PerfData[PerfIdx["LATREF"]]
            PlotConf["zData"][Label] = PerfData[PerfIdx["CONVT"]]

            PlotConf["RcvrTag"][Label] = PerfData[PerfIdx["RCVR"]]
            Label += 1

    # Store max and min values from all stations
    values = [series.values[0] for series in PlotConf["zData"].values()]
    PlotConf["ColorBarMin"] = min(values)
    PlotConf["ColorBarMax"] = max(values)


    # init plot
    Folder = "CONVT"
    initPlot(PerfFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotHpeRms():
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "HPE RMS" 

    PlotConf["LonMin"] = -35
    PlotConf["LonMax"] = 40
    PlotConf["LatMin"] = 10
    PlotConf["LatMax"] = 90
    PlotConf["LonStep"] = 5
    PlotConf["LatStep"] = 5

    PlotConf["yLim"] = [PlotConf["LatMin"], PlotConf["LatMax"]]
    PlotConf["xLabel"] = ""
    PlotConf["xLim"] = [PlotConf["LonMin"], PlotConf["LonMax"]]

    PlotConf["Grid"] = True

    PlotConf["Map"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 5

    PlotConf["ColorBar"] = "rainbow"
    PlotConf["ColorBarLabel"] = "HPE RMS [m]"

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    PlotConf["RcvrTag"] = {}
    Label = 0

    # Annotate
    PlotConf["Annotate"] = True
    PlotConf["xPosText"] = 1
    PlotConf["yPosText"] = 2
    PlotConf["AnnFontSize"] = 5


    # Path to the Perf Files
    path = sys.argv[1] + '/OUT/PERF/'
    PerfFile = None

    # Loop over all the Perf Files
    for file_name in os.listdir(path):
        if "PERF_" in file_name:
            PerfFile = path+file_name

            PerfData = read_csv(PerfFile, delim_whitespace=True, skiprows=1, header=None,\
            usecols=[PerfIdx["RCVR"], PerfIdx["LONREF"], PerfIdx["LATREF"], PerfIdx["HPERMS"]])

            PlotConf["xData"][Label] = PerfData[PerfIdx["LONREF"]]
            PlotConf["yData"][Label] = PerfData[PerfIdx["LATREF"]]
            PlotConf["zData"][Label] = round(PerfData[PerfIdx["HPERMS"]],2)

            PlotConf["RcvrTag"][Label] = PerfData[PerfIdx["RCVR"]]
            Label += 1

    # Store max and min values from all stations
    values = [series.values[0] for series in PlotConf["zData"].values()]
    PlotConf["ColorBarMin"] = min(values)
    PlotConf["ColorBarMax"] = max(values)


    # init plot
    Folder = "HPERMS"
    initPlot(PerfFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotVpeRms():
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "VPE RMS" 

    PlotConf["LonMin"] = -35
    PlotConf["LonMax"] = 40
    PlotConf["LatMin"] = 10
    PlotConf["LatMax"] = 90
    PlotConf["LonStep"] = 5
    PlotConf["LatStep"] = 5

    PlotConf["yLim"] = [PlotConf["LatMin"], PlotConf["LatMax"]]
    PlotConf["xLabel"] = ""
    PlotConf["xLim"] = [PlotConf["LonMin"], PlotConf["LonMax"]]

    PlotConf["Grid"] = True

    PlotConf["Map"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 5

    PlotConf["ColorBar"] = "rainbow"
    PlotConf["ColorBarLabel"] = "VPE RMS [m]"

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    PlotConf["RcvrTag"] = {}
    Label = 0

    # Annotate
    PlotConf["Annotate"] = True
    PlotConf["xPosText"] = 1
    PlotConf["yPosText"] = 2
    PlotConf["AnnFontSize"] = 5


    # Path to the Perf Files
    path = sys.argv[1] + '/OUT/PERF/'
    PerfFile = None

    # Loop over all the Perf Files
    for file_name in os.listdir(path):
        if "PERF_" in file_name:
            PerfFile = path+file_name

            PerfData = read_csv(PerfFile, delim_whitespace=True, skiprows=1, header=None,\
            usecols=[PerfIdx["RCVR"], PerfIdx["LONREF"], PerfIdx["LATREF"], PerfIdx["VPERMS"]])

            PlotConf["xData"][Label] = PerfData[PerfIdx["LONREF"]]
            PlotConf["yData"][Label] = PerfData[PerfIdx["LATREF"]]
            PlotConf["zData"][Label] = round(PerfData[PerfIdx["VPERMS"]],2)

            PlotConf["RcvrTag"][Label] = PerfData[PerfIdx["RCVR"]]
            Label += 1

    # Store max and min values from all stations
    values = [series.values[0] for series in PlotConf["zData"].values()]
    PlotConf["ColorBarMin"] = min(values)
    PlotConf["ColorBarMax"] = max(values)


    # init plot
    Folder = "VPERMS"
    initPlot(PerfFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotHpe95():
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "HPE 95%" 

    PlotConf["LonMin"] = -35
    PlotConf["LonMax"] = 40
    PlotConf["LatMin"] = 10
    PlotConf["LatMax"] = 90
    PlotConf["LonStep"] = 5
    PlotConf["LatStep"] = 5

    PlotConf["yLim"] = [PlotConf["LatMin"], PlotConf["LatMax"]]
    PlotConf["xLabel"] = ""
    PlotConf["xLim"] = [PlotConf["LonMin"], PlotConf["LonMax"]]

    PlotConf["Grid"] = True

    PlotConf["Map"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 5

    PlotConf["ColorBar"] = "rainbow"
    PlotConf["ColorBarLabel"] = "HPE 95% [m]"

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    PlotConf["RcvrTag"] = {}
    Label = 0

    # Annotate
    PlotConf["Annotate"] = True
    PlotConf["xPosText"] = 1
    PlotConf["yPosText"] = 2.5
    PlotConf["AnnFontSize"] = 5


    # Path to the Perf Files
    path = sys.argv[1] + '/OUT/PERF/'
    PerfFile = None

    # Loop over all the Perf Files
    for file_name in os.listdir(path):
        if "PERF_" in file_name:
            PerfFile = path+file_name

            PerfData = read_csv(PerfFile, delim_whitespace=True, skiprows=1, header=None,\
            usecols=[PerfIdx["RCVR"], PerfIdx["LONREF"], PerfIdx["LATREF"], PerfIdx["HPE95"]])

            PlotConf["xData"][Label] = PerfData[PerfIdx["LONREF"]]
            PlotConf["yData"][Label] = PerfData[PerfIdx["LATREF"]]
            PlotConf["zData"][Label] = round(PerfData[PerfIdx["HPE95"]],2)

            PlotConf["RcvrTag"][Label] = PerfData[PerfIdx["RCVR"]]
            Label += 1

    # Store max and min values from all stations
    values = [series.values[0] for series in PlotConf["zData"].values()]
    PlotConf["ColorBarMin"] = min(values)
    PlotConf["ColorBarMax"] = max(values)


    # init plot
    Folder = "HPE95"
    initPlot(PerfFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotVpe95():
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "VPE 95%" 

    PlotConf["LonMin"] = -35
    PlotConf["LonMax"] = 40
    PlotConf["LatMin"] = 10
    PlotConf["LatMax"] = 90
    PlotConf["LonStep"] = 5
    PlotConf["LatStep"] = 5

    PlotConf["yLim"] = [PlotConf["LatMin"], PlotConf["LatMax"]]
    PlotConf["xLabel"] = ""
    PlotConf["xLim"] = [PlotConf["LonMin"], PlotConf["LonMax"]]

    PlotConf["Grid"] = True

    PlotConf["Map"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 5

    PlotConf["ColorBar"] = "rainbow"
    PlotConf["ColorBarLabel"] = "VPE 95% [m]"

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    PlotConf["RcvrTag"] = {}
    Label = 0

    # Annotate
    PlotConf["Annotate"] = True
    PlotConf["xPosText"] = 1
    PlotConf["yPosText"] = 2
    PlotConf["AnnFontSize"] = 5


    # Path to the Perf Files
    path = sys.argv[1] + '/OUT/PERF/'
    PerfFile = None

    # Loop over all the Perf Files
    for file_name in os.listdir(path):
        if "PERF_" in file_name:
            PerfFile = path+file_name

            PerfData = read_csv(PerfFile, delim_whitespace=True, skiprows=1, header=None,\
            usecols=[PerfIdx["RCVR"], PerfIdx["LONREF"], PerfIdx["LATREF"], PerfIdx["VPE95"]])

            PlotConf["xData"][Label] = PerfData[PerfIdx["LONREF"]]
            PlotConf["yData"][Label] = PerfData[PerfIdx["LATREF"]]
            PlotConf["zData"][Label] = round(PerfData[PerfIdx["VPE95"]],2)

            PlotConf["RcvrTag"][Label] = PerfData[PerfIdx["RCVR"]]
            Label += 1

    # Store max and min values from all stations
    values = [series.values[0] for series in PlotConf["zData"].values()]
    PlotConf["ColorBarMin"] = min(values)
    PlotConf["ColorBarMax"] = max(values)


    # init plot
    Folder = "VPE95"
    initPlot(PerfFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotNSVMIN():
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "Min Num of SVs used in solution" 

    PlotConf["LonMin"] = -35
    PlotConf["LonMax"] = 40
    PlotConf["LatMin"] = 10
    PlotConf["LatMax"] = 90
    PlotConf["LonStep"] = 5
    PlotConf["LatStep"] = 5

    PlotConf["yLim"] = [PlotConf["LatMin"], PlotConf["LatMax"]]
    PlotConf["xLabel"] = ""
    PlotConf["xLim"] = [PlotConf["LonMin"], PlotConf["LonMax"]]

    PlotConf["Grid"] = True

    PlotConf["Map"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 5

    PlotConf["ColorBar"] = "rainbow"
    PlotConf["ColorBarLabel"] = "Min Number of SVs used in solution"

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    PlotConf["RcvrTag"] = {}
    Label = 0

    # Annotate
    PlotConf["Annotate"] = True
    PlotConf["xPosText"] = 1
    PlotConf["yPosText"] = 2
    PlotConf["AnnFontSize"] = 5


    # Path to the Perf Files
    path = sys.argv[1] + '/OUT/PERF/'
    PerfFile = None

    # Loop over all the Perf Files
    for file_name in os.listdir(path):
        if "PERF_" in file_name:
            PerfFile = path+file_name

            PerfData = read_csv(PerfFile, delim_whitespace=True, skiprows=1, header=None,\
            usecols=[PerfIdx["RCVR"], PerfIdx["LONREF"], PerfIdx["LATREF"], PerfIdx["NSVMIN"]])

            PlotConf["xData"][Label] = PerfData[PerfIdx["LONREF"]]
            PlotConf["yData"][Label] = PerfData[PerfIdx["LATREF"]]
            PlotConf["zData"][Label] = PerfData[PerfIdx["NSVMIN"]]

            PlotConf["RcvrTag"][Label] = PerfData[PerfIdx["RCVR"]]
            Label += 1

    # Store max and min values from all stations
    values = [series.values[0] for series in PlotConf["zData"].values()]
    PlotConf["ColorBarMin"] = min(values)
    PlotConf["ColorBarMax"] = max(values)


    # init plot
    Folder = "MIN_NSATS"
    initPlot(PerfFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotNSVMAX():
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "Max Num of SVs used in solution" 

    PlotConf["LonMin"] = -35
    PlotConf["LonMax"] = 40
    PlotConf["LatMin"] = 10
    PlotConf["LatMax"] = 90
    PlotConf["LonStep"] = 5
    PlotConf["LatStep"] = 5

    PlotConf["yLim"] = [PlotConf["LatMin"], PlotConf["LatMax"]]
    PlotConf["xLabel"] = ""
    PlotConf["xLim"] = [PlotConf["LonMin"], PlotConf["LonMax"]]

    PlotConf["Grid"] = True

    PlotConf["Map"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 5

    PlotConf["ColorBar"] = "rainbow"
    PlotConf["ColorBarLabel"] = "Max Number of SVs used in solution"

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    PlotConf["RcvrTag"] = {}
    Label = 0

    # Annotate
    PlotConf["Annotate"] = True
    PlotConf["xPosText"] = 1
    PlotConf["yPosText"] = 2
    PlotConf["AnnFontSize"] = 5


    # Path to the Perf Files
    path = sys.argv[1] + '/OUT/PERF/'
    PerfFile = None

    # Loop over all the Perf Files
    for file_name in os.listdir(path):
        if "PERF_" in file_name:
            PerfFile = path+file_name

            PerfData = read_csv(PerfFile, delim_whitespace=True, skiprows=1, header=None,\
            usecols=[PerfIdx["RCVR"], PerfIdx["LONREF"], PerfIdx["LATREF"], PerfIdx["NSVMAX"]])

            PlotConf["xData"][Label] = PerfData[PerfIdx["LONREF"]]
            PlotConf["yData"][Label] = PerfData[PerfIdx["LATREF"]]
            PlotConf["zData"][Label] = PerfData[PerfIdx["NSVMAX"]]

            PlotConf["RcvrTag"][Label] = PerfData[PerfIdx["RCVR"]]
            Label += 1

    # Store max and min values from all stations
    values = [series.values[0] for series in PlotConf["zData"].values()]
    PlotConf["ColorBarMin"] = min(values)
    PlotConf["ColorBarMax"] = max(values)


    # init plot
    Folder = "MAX_NSATS"
    initPlot(PerfFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotPDOP():
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "Max PDOP" 

    PlotConf["LonMin"] = -35
    PlotConf["LonMax"] = 40
    PlotConf["LatMin"] = 10
    PlotConf["LatMax"] = 90
    PlotConf["LonStep"] = 5
    PlotConf["LatStep"] = 5

    PlotConf["yLim"] = [PlotConf["LatMin"], PlotConf["LatMax"]]
    PlotConf["xLabel"] = ""
    PlotConf["xLim"] = [PlotConf["LonMin"], PlotConf["LonMax"]]

    PlotConf["Grid"] = True

    PlotConf["Map"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 5

    PlotConf["ColorBar"] = "rainbow"
    PlotConf["ColorBarLabel"] = "Max PDOP"

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    PlotConf["RcvrTag"] = {}
    Label = 0

    # Annotate
    PlotConf["Annotate"] = True
    PlotConf["xPosText"] = 1
    PlotConf["yPosText"] = 2
    PlotConf["AnnFontSize"] = 5


    # Path to the Perf Files
    path = sys.argv[1] + '/OUT/PERF/'
    PerfFile = None

    # Loop over all the Perf Files
    for file_name in os.listdir(path):
        if "PERF_" in file_name:
            PerfFile = path+file_name

            PerfData = read_csv(PerfFile, delim_whitespace=True, skiprows=1, header=None,\
            usecols=[PerfIdx["RCVR"], PerfIdx["LONREF"], PerfIdx["LATREF"], PerfIdx["PDOPMAX"]])

            PlotConf["xData"][Label] = PerfData[PerfIdx["LONREF"]]
            PlotConf["yData"][Label] = PerfData[PerfIdx["LATREF"]]
            PlotConf["zData"][Label] = round(PerfData[PerfIdx["PDOPMAX"]],2)

            PlotConf["RcvrTag"][Label] = PerfData[PerfIdx["RCVR"]]
            Label += 1

    # Store max and min values from all stations
    values = [series.values[0] for series in PlotConf["zData"].values()]
    PlotConf["ColorBarMin"] = min(values)
    PlotConf["ColorBarMax"] = max(values)


    # init plot
    Folder = "MAX_PDOP"
    initPlot(PerfFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotHDOP():
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "Max HDOP" 

    PlotConf["LonMin"] = -35
    PlotConf["LonMax"] = 40
    PlotConf["LatMin"] = 10
    PlotConf["LatMax"] = 90
    PlotConf["LonStep"] = 5
    PlotConf["LatStep"] = 5

    PlotConf["yLim"] = [PlotConf["LatMin"], PlotConf["LatMax"]]
    PlotConf["xLabel"] = ""
    PlotConf["xLim"] = [PlotConf["LonMin"], PlotConf["LonMax"]]

    PlotConf["Grid"] = True

    PlotConf["Map"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 5

    PlotConf["ColorBar"] = "rainbow"
    PlotConf["ColorBarLabel"] = "Max HDOP"

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    PlotConf["RcvrTag"] = {}
    Label = 0

    # Annotate
    PlotConf["Annotate"] = True
    PlotConf["xPosText"] = 1
    PlotConf["yPosText"] = 2
    PlotConf["AnnFontSize"] = 5


    # Path to the Perf Files
    path = sys.argv[1] + '/OUT/PERF/'
    PerfFile = None

    # Loop over all the Perf Files
    for file_name in os.listdir(path):
        if "PERF_" in file_name:
            PerfFile = path+file_name

            PerfData = read_csv(PerfFile, delim_whitespace=True, skiprows=1, header=None,\
            usecols=[PerfIdx["RCVR"], PerfIdx["LONREF"], PerfIdx["LATREF"], PerfIdx["HDOPMAX"]])

            PlotConf["xData"][Label] = PerfData[PerfIdx["LONREF"]]
            PlotConf["yData"][Label] = PerfData[PerfIdx["LATREF"]]
            PlotConf["zData"][Label] = round(PerfData[PerfIdx["HDOPMAX"]],2)

            PlotConf["RcvrTag"][Label] = PerfData[PerfIdx["RCVR"]]
            Label += 1

    # Store max and min values from all stations
    values = [series.values[0] for series in PlotConf["zData"].values()]
    PlotConf["ColorBarMin"] = min(values)
    PlotConf["ColorBarMax"] = max(values)


    # init plot
    Folder = "MAX_HDOP"
    initPlot(PerfFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotVDOP():
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "Max VDOP" 

    PlotConf["LonMin"] = -35
    PlotConf["LonMax"] = 40
    PlotConf["LatMin"] = 10
    PlotConf["LatMax"] = 90
    PlotConf["LonStep"] = 5
    PlotConf["LatStep"] = 5

    PlotConf["yLim"] = [PlotConf["LatMin"], PlotConf["LatMax"]]
    PlotConf["xLabel"] = ""
    PlotConf["xLim"] = [PlotConf["LonMin"], PlotConf["LonMax"]]

    PlotConf["Grid"] = True

    PlotConf["Map"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 5

    PlotConf["ColorBar"] = "rainbow"
    PlotConf["ColorBarLabel"] = "Max VDOP"

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    PlotConf["RcvrTag"] = {}
    Label = 0

    # Annotate
    PlotConf["Annotate"] = True
    PlotConf["xPosText"] = 1
    PlotConf["yPosText"] = 2
    PlotConf["AnnFontSize"] = 5


    # Path to the Perf Files
    path = sys.argv[1] + '/OUT/PERF/'
    PerfFile = None

    # Loop over all the Perf Files
    for file_name in os.listdir(path):
        if "PERF_" in file_name:
            PerfFile = path+file_name

            PerfData = read_csv(PerfFile, delim_whitespace=True, skiprows=1, header=None,\
            usecols=[PerfIdx["RCVR"], PerfIdx["LONREF"], PerfIdx["LATREF"], PerfIdx["VDOPMAX"]])

            PlotConf["xData"][Label] = PerfData[PerfIdx["LONREF"]]
            PlotConf["yData"][Label] = PerfData[PerfIdx["LATREF"]]
            PlotConf["zData"][Label] = round(PerfData[PerfIdx["VDOPMAX"]],2)

            PlotConf["RcvrTag"][Label] = PerfData[PerfIdx["RCVR"]]
            Label += 1

    # Store max and min values from all stations
    values = [series.values[0] for series in PlotConf["zData"].values()]
    PlotConf["ColorBarMin"] = min(values)
    PlotConf["ColorBarMax"] = max(values)


    # init plot
    Folder = "MAX_VDOP"
    initPlot(PerfFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Generate PerfPlots
def generatePerfPlots():
    # Purpose: generate output plots regarding Map Perf results

    # Returns
    # =======
    # Nothing
    # ----------------------------------------------------------

    
    # Convergence Time
    # ----------------------------------------------------------
    if cfg["CONVT"] == 1:
        print( '\nPlot Map of Convergence Time ...')
        # Call Plot Function
        plotCONVT()

    # HPE RMS Post-Convergence Time
    # ---------------------------------------------------------- 
    if cfg["HPE-RMS"] == 1:
        print( '\nPlot Map of HPE-RMS Post-Convergence Time ...')
        # Call Plot Function
        plotHpeRms()
    
    # VPE RMS Post-Convergence Time
    # ---------------------------------------------------------- 
    if cfg["VPE-RMS"] == 1:
        print( '\nPlot Map of VPE-RMS Post-Convergence Time ...')
        # Call Plot Function
        plotVpeRms()
    
    # HPE 95% Percentile Post-Convergence Time
    # ---------------------------------------------------------- 
    if cfg["HPE95"] == 1:
        print( '\nPlot Map of HPE 95% Percentile Post-Convergence Time ...')
        # Call Plot Function
        plotHpe95()
    
    # VPE 95% Percentile Post-Convergence Time
    # ---------------------------------------------------------- 
    if cfg["VPE95"] == 1:
        print( '\nPlot Map of VPE 95% Percentile Post-Convergence Time ...')
        # Call Plot Function
        plotVpe95()
    
    # Minimum Number of Satellites
    # ---------------------------------------------------------- 
    if cfg["NSVMIN"] ==1:
        print( '\nPlot Map of Minimum Number of Satellites ...')
        # Call Plot Function
        plotNSVMIN()
    
    # Maximum Number of Satellites
    # ---------------------------------------------------------- 
    if cfg["NSVMAX"] ==1:
        print( '\nPlot Map of Maximum Number of Satellites ...')
        # Call Plot Function
        plotNSVMAX()

    # Maximum PDOP
    # ---------------------------------------------------------- 
    if cfg["PDOPMAX"] ==1:
        print( '\nPlot Map of Maximum PDOP ...')
        # Call Plot Function
        plotPDOP()
    
    # Maximum HDOP
    # ---------------------------------------------------------- 
    if cfg["HDOPMAX"] ==1:
        print( '\nPlot Map of Maximum HDOP ...')
        # Call Plot Function
        plotHDOP()
    
    # Maximum VDOP
    # ---------------------------------------------------------- 
    if cfg["VDOPMAX"] ==1:
        print( '\nPlot Map of Maximum VDOP ...')
        # Call Plot Function
        plotVDOP()


def plotHpeHist(XpeData, HpeFile):
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "HPE Histogram"

    PlotConf["yLabel"] = "PDF"

    PlotConf["xLabel"] = "HPE Histogram [m]"

    PlotConf["Grid"] = 1

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["Color"] = {}

    PlotConf["BarPlot"] = True
    PlotConf["WidthBar"] = 0.001
    Label = "0"

    # Variables
    binmin_values = XpeData[XpeIdx["BINMIN"]]
    freq_values = XpeData[XpeIdx["FREQ"]]

    # Total area behind histogram
    total_area = sum(freq_values)

    # Calculate the probability density function (PDF)
    pdf = [freq_values[i] / total_area for i in range(len(binmin_values))]

    PlotConf["xData"][Label] = XpeData[XpeIdx["BINMIN"]]
    PlotConf["yData"][Label] = pdf
    PlotConf["Color"][Label] = 'Cyan'

    # Prepare Legend
    min_value = round(min(binmin_values),3)
    max_value = round(max(binmin_values),3)

    PlotConf["LegendText"] = f'Min: {min_value}\nMax: {max_value}'

    # init plot
    Folder = "HPEHIST"
    initXpePlot(HpeFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)


def plotVpeHist(XpeData, VpeFile):
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "VPE Histogram"

    PlotConf["yLabel"] = "PDF"

    PlotConf["xLabel"] = "VPE Histogram [m]"

    PlotConf["Grid"] = 1

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["Color"] = {}

    PlotConf["BarPlot"] = True
    PlotConf["WidthBar"] = 0.001
    Label = "0"

    # Variables
    binmin_values = XpeData[XpeIdx["BINMIN"]]
    freq_values = XpeData[XpeIdx["FREQ"]]

    # Total area behind histogram
    total_area = sum(freq_values)

    # Calculate the probability density function (PDF)
    pdf = [freq_values[i] / total_area for i in range(len(binmin_values))]

    PlotConf["xData"][Label] = XpeData[XpeIdx["BINMIN"]]
    PlotConf["yData"][Label] = pdf
    PlotConf["Color"][Label] = 'Cyan'

    # Prepare Legend
    min_value = round(min(binmin_values),3)
    max_value = round(max(binmin_values),3)

    PlotConf["LegendText"] = f'Min: {min_value}\nMax: {max_value}'

    # init plot
    Folder = "VPEHIST"
    initXpePlot(VpeFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Generate HistPlots
def generateXpeHistPlots(HpeFile, VpeFile):
    # Purpose: generate output plots regarding XPE HIST results

    # Returns
    # =======
    # Nothing
    # ----------------------------------------------------------

    
    # HPE-HIST
    # ----------------------------------------------------------
    if cfg["HPE-HIST"] == 1:  
        XpeData = read_csv(HpeFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[XpeIdx["BINID"], XpeIdx["BINMIN"], XpeIdx["BINMAX"], XpeIdx["NUMSAMP"], XpeIdx["FREQ"]])
        
        print( '\nPlot HPE Histogram ...')
        # Call Plot Function
        plotHpeHist(XpeData, HpeFile)
    
    # VPE-HIST
    # ----------------------------------------------------------
    if cfg["HPE-HIST"] == 1:  
        XpeData = read_csv(VpeFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[XpeIdx["BINID"], XpeIdx["BINMIN"], XpeIdx["BINMAX"], XpeIdx["NUMSAMP"], XpeIdx["FREQ"]])
        
        print( '\nPlot VPE Histogram ...')
        # Call Plot Function
        plotVpeHist(XpeData, VpeFile)




# ------------- END -------------