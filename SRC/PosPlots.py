#!/usr/bin/env python

########################################################################
# PEPPUS/SRC/PosPlots.py:
# This is the PosPlots Module of PEPPUS tool
#
#  Project:        PEPPUS
#  File:           PosPlots.py
#  Date(YY/MM/DD): 06/07/2024
#
#   Author: Alexis Díaz López
#
########################################################################

import sys, os

from pandas import read_csv
from InputOutput import PosIdx, AmbIdx
sys.path.append(os.getcwd() + '/' + \
    os.path.dirname(sys.argv[0]) + '/' + 'COMMON')
from COMMON.Plots import generatePlot
import numpy as np
from COMMON import GnssConstants as Const


def initPlot(PosFile, PlotConf, Title, Label):
    PosFileName = os.path.basename(PosFile)
    PosFileNameSplit = PosFileName.split('_')
    Rcvr = PosFileNameSplit[1]
    DatepDat = PosFileNameSplit[2]
    Date = DatepDat.split('.')[0]
    Year = Date[1:3]
    Doy = Date[4:]

    if "xLabel" not in PlotConf:
        PlotConf["xLabel"] = "Hour of Day %s" % Doy

    PlotConf["Title"] = "%s from %s on Year %s"\
        " DoY %s" % (Title, Rcvr, Year, Doy)

    PlotConf["Path"] = sys.argv[1] + '/OUT/KPVT/figures/%s/' % Label + \
        '%s_%s_Y%sD%s.png' % (Label, Rcvr, Year, Doy)

# Plot Confg
cfg = {
    "EstCLK"        : 1,
    "HPE-VPE"       : 1,
    "DOP"           : 1,
    "HPE"           : 1,
    "AMB"           : 1,
    "AMB-Zoom"      : 1
}

def plotEstimatedClock(PosFile, PosData):
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "Estimated Receiver Clock"

    PlotConf["yLabel"] = "Estimated Receiver Clock [m]"

    PlotConf["xTicks"] = range(0, 25)
    PlotConf["xLim"] = [0, 24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 1.5


    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["Color"] = {}

    PlotConf["Legend"] = True
    Label = "CLKEST"

    filter_flag = PosData[PosIdx["SOL"]] == 1
    f_outlayer = PosData[PosIdx["SOD"]] != 60

    PlotConf["xData"][Label] = PosData[PosIdx["SOD"]][filter_flag][f_outlayer] / Const.S_IN_H
    PlotConf["yData"][Label] = PosData[PosIdx["CLKEST"]][filter_flag][f_outlayer]
    PlotConf["Color"][Label] = 'g'

    # init plot
    Folder = "CLKEST"
    initPlot(PosFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotPE(PosFile, PosData):
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "Position Errors"

    PlotConf["yLabel"] = "Position Errors [m]"

    PlotConf["xTicks"] = range(0, 25)
    PlotConf["xLim"] = [0, 24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 1.5


    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["Color"] = {}

    PlotConf["Legend"] = True
    Label = ["VPE", "HPE"]
    Colors = ["green", "red"]

    filter_flag = PosData[PosIdx["SOL"]] == 1

    for idx, label in enumerate(Label):
        PE = PosData[PosIdx[label]][filter_flag]
        PE = np.array(np.abs(PE))
        PlotConf["Color"][label] = Colors[idx]

        PlotConf["xData"][label] = PosData[PosIdx["SOD"]][filter_flag] / Const.S_IN_H
        PlotConf["yData"][label] = PE

    # init plot
    Folder = "PE"
    initPlot(PosFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotDOP(PosFile, PosData):
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "DOP"

    PlotConf["DoubleAx"] = "NSV"

    PlotConf["yLabel"] = "DOP"
    PlotConf["y2Label"] = "Number of Satellites used"
    PlotConf["y2Ticks"] = range(0,14)
    PlotConf["y2Lim"] = [0,13]

    PlotConf["xTicks"] = range(0, 25)
    PlotConf["xLim"] = [0, 24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '|'
    PlotConf["LineWidth"] = 1.5


    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    PlotConf["Color"] = {}

    PlotConf["Legend"] = True
    Label = ["TDOP", "PDOP", "VDOP", "HDOP"]
    Colors = ["gray", "blue", "green", "lightblue"] #red

    filter_flag = PosData[PosIdx["SOL"]] == 1

    for idx, label in enumerate(Label):
        DOP = PosData[PosIdx[label]][filter_flag]
        DOP = np.array(np.abs(DOP))
        PlotConf["Color"][label] = Colors[idx]

        PlotConf["xData"][label] = PosData[PosIdx["SOD"]][filter_flag] / Const.S_IN_H
        PlotConf["yData"][label] = DOP

    PlotConf["Color"]["NSV"] = "orange"
    PlotConf["xData"]["NSV"] = PosData[PosIdx["SOD"]][filter_flag] / Const.S_IN_H
    PlotConf["zData"]["NSV"] = PosData[PosIdx["NSV"]][filter_flag]

    # init plot
    Folder = "DOP"
    initPlot(PosFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotHPE(PosFile, PosData):
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "Horizontal Position Error vs DOP"

    PlotConf["yLabel"] = "NPE [m]"

    PlotConf["xLabel"] = "EPE [m]"

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 1.5

    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "HDOP"
    

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    
    Label = 0

    filter_flag = PosData[PosIdx["SOL"]] == 1

    PlotConf["xData"][Label] = PosData[PosIdx["EPE"]][filter_flag]
    PlotConf["yData"][Label] = PosData[PosIdx["NPE"]][filter_flag]
    PlotConf["zData"][Label] = PosData[PosIdx["HPE"]][filter_flag]

    # init plot
    Folder = "HPE"
    initPlot(PosFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotAMB(AmbFile, PosData):
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "Estimated Ambiguities"

    PlotConf["yLabel"] = "Estimated Ambiguities [m]"

    PlotConf["xTicks"] = range(0, 25)
    PlotConf["xLim"] = [0, 24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '|'
    PlotConf["LineWidth"] = 1

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}

    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "PRN"
    PlotConf["ColorBarTicks"] = range(1, 33)
    PlotConf["ColorBarMin"] = 1
    PlotConf["ColorBarMax"] = 32
    
    for i in range(1, 33):
        Label = f"G{i:02d}"
        filter_flag = PosData[AmbIdx[Label]] != 0.000
        PlotConf["xData"][Label] = PosData[AmbIdx["SOD"]][filter_flag] / Const.S_IN_H
        PlotConf["yData"][Label] = PosData[AmbIdx[Label]][filter_flag]
        PlotConf["zData"][Label] = [i] * len(PosData[AmbIdx[Label]][filter_flag])

    # init plot
    Folder = "AMB"
    initPlot(AmbFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def plotAMBZ(AmbFile, PosData):
    PlotConf = {}

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,6.6)
    Title = "Estimated Ambiguities"

    PlotConf["yLabel"] = "Estimated Ambiguities [m]"
    PlotConf["yLim"] = [-8, 8]

    PlotConf["xTicks"] = range(0, 25)
    PlotConf["xLim"] = [0, 24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '|'
    PlotConf["LineWidth"] = 1

    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}

    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "PRN"
    PlotConf["ColorBarTicks"] = range(1, 33)
    PlotConf["ColorBarMin"] = 1
    PlotConf["ColorBarMax"] = 32
    
    for i in range(1, 33):
        Label = f"G{i:02d}"
        filter_flag = PosData[AmbIdx[Label]] != 0.000
        PlotConf["xData"][Label] = PosData[AmbIdx["SOD"]][filter_flag] / Const.S_IN_H
        PlotConf["yData"][Label] = PosData[AmbIdx[Label]][filter_flag]
        PlotConf["zData"][Label] = [i] * len(PosData[AmbIdx[Label]][filter_flag])

    # init plot
    Folder = "AMBZoom"
    initPlot(AmbFile, PlotConf, Title, Folder)
    # Call generatePlot from Plots library
    generatePlot(PlotConf)


# Generate PosPlots
def generatePosPlots(PosFile, AmbFile):
    # Purpose: generate output plots regarding KPVT POS results

    # Parameters
    # ==========
    # PosFile: str
    #         Path to KPVT POS output file
    # Rcvr: str
    #           Receiver information

    # Returns
    # =======
    # Nothing
    # ----------------------------------------------------------

    
    # Time of Flight
    # ----------------------------------------------------------
    if (cfg["EstCLK"] == 1):
        PosData = read_csv(PosFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PosIdx["SOD"], PosIdx["CLKEST"], PosIdx["SOL"]])

        print( '\nPlot Estimated ReceiverClock ...')

        # Call Plot Function
        plotEstimatedClock(PosFile, PosData)
    
    if (cfg["HPE-VPE"] == 1):
        PosData = read_csv(PosFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PosIdx["SOD"], PosIdx["HPE"], PosIdx["VPE"], PosIdx["SOL"]])

        print( '\nPlot Estimated Position Errors ...')

        # Call Plot Function
        plotPE(PosFile, PosData)
    
    if (cfg["DOP"] == 1):
        PosData = read_csv(PosFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PosIdx["SOD"], PosIdx["SOL"], PosIdx["TDOP"], PosIdx["PDOP"], PosIdx["HDOP"], PosIdx["VDOP"], PosIdx["NSV"]])

        print( '\nPlot DOP ...')

        # Call Plot Function
        plotDOP(PosFile, PosData)
    
    if (cfg["HPE"] == 1):
        PosData = read_csv(PosFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PosIdx["SOD"], PosIdx["SOL"], PosIdx["HPE"], PosIdx["NPE"], PosIdx["EPE"]])

        print( '\nPlot HPE scatter ...')

        # Call Plot Function
        plotHPE(PosFile, PosData)
    
    if (cfg["AMB"] == 1):
        PosData = read_csv(AmbFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[AmbIdx["SOD"], AmbIdx["G01"], 
                AmbIdx["G02"], AmbIdx["G03"], AmbIdx["G04"], AmbIdx["G05"], AmbIdx["G06"], 
                AmbIdx["G07"], AmbIdx["G08"], AmbIdx["G09"], AmbIdx["G10"], AmbIdx["G11"],
                AmbIdx["G12"], AmbIdx["G13"], AmbIdx["G14"], AmbIdx["G15"], AmbIdx["G16"], 
                AmbIdx["G17"], AmbIdx["G18"], AmbIdx["G19"], AmbIdx["G20"], AmbIdx["G21"],
                AmbIdx["G22"], AmbIdx["G23"], AmbIdx["G24"], AmbIdx["G25"], AmbIdx["G26"], 
                AmbIdx["G27"], AmbIdx["G28"], AmbIdx["G29"], AmbIdx["G30"], AmbIdx["G31"],
                AmbIdx["G32"]])

        print( '\nPlot Ambiguities ...')

        # Call Plot Function
        plotAMB(AmbFile, PosData)
    
    if (cfg["AMB-Zoom"] == 1):
        PosData = read_csv(AmbFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[AmbIdx["SOD"], AmbIdx["G01"], 
                AmbIdx["G02"], AmbIdx["G03"], AmbIdx["G04"], AmbIdx["G05"], AmbIdx["G06"], 
                AmbIdx["G07"], AmbIdx["G08"], AmbIdx["G09"], AmbIdx["G10"], AmbIdx["G11"],
                AmbIdx["G12"], AmbIdx["G13"], AmbIdx["G14"], AmbIdx["G15"], AmbIdx["G16"], 
                AmbIdx["G17"], AmbIdx["G18"], AmbIdx["G19"], AmbIdx["G20"], AmbIdx["G21"],
                AmbIdx["G22"], AmbIdx["G23"], AmbIdx["G24"], AmbIdx["G25"], AmbIdx["G26"], 
                AmbIdx["G27"], AmbIdx["G28"], AmbIdx["G29"], AmbIdx["G30"], AmbIdx["G31"],
                AmbIdx["G32"]])

        print( '\nPlot Ambiguities Zoomed...')

        # Call Plot Function
        plotAMBZ(AmbFile, PosData)
    
