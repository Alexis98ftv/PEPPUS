#!/usr/bin/env python

########################################################################
# PEPPUS/SRC/Perf.py:
# This is the PERF Module of PEPPUS tool
#
#  Project:        PEPPUS
#  File:           Perf.py
#  Date(YY/MM/DD): 06/07/2024
#
#   Author: Alexis Díaz López
#
# -----------------------------------------------------------------
# Date       | Author             | Action
# -----------------------------------------------------------------
#   
########################################################################

# Import External and Internal functions and Libraries
#----------------------------------------------------------------------
import sys, os
# Add path to find all modules
Common = os.path.dirname(os.path.dirname(
    os.path.abspath(sys.argv[0]))) + '/COMMON'
sys.path.insert(0, Common)
from collections import OrderedDict
from COMMON import GnssConstants as Const
from InputOutput import RcvrIdx
import numpy as np


def initializePerfInfo(Rcvr, Doy):
    # Prepare some outputs
    # ---------------------------------
    # Get Receiver Acronym
    Acr = Rcvr[RcvrIdx["ACR"]] 
    # Get Receiver Reference Longitude
    Lon = Rcvr[RcvrIdx["LON"]] 
    # Get Receiver Reference Latitude
    Lat = Rcvr[RcvrIdx["LAT"]]
    # Max number of Satellites 
    N = Const.MAX_NUM_SATS_CONSTEL # 36
    

    # Initialize output
    PerfInfo = OrderedDict({
        "Rcvr": Acr,            # Receiver Acronym with 4 characters
        "Lon": Lon,             # [DEG] Receiver Reference Longitude
        "Lat": Lat,             # [DEG] Receiver Reference Latitude
        "Doy": Doy,             # Day of the year
        "Samples": 0,           # Number of total samples processed 
        "Convt": 0,             # [s] Convergence Time (time when XPE drops under a configured Threshold)
        "NsvMin": N,            # Minimum number satellites used in PVT in the day
        "NsvMax": 0,            # Maximum number satellites used in PVT in the day
        "HpeRms": 0.0,          # [m] RMS of the Horizontal Position Error
        "VpeRms": 0.0,          # [m] RMS of the Vertical Position Error
        "Hpe95": 0.0,           # [m] 95% Percentile of HPE
        "Vpe95": 0.0,           # [m] 95% Percentile of VPE
        "HpeMax": 0.0,          # [m] Maximum reached HPE
        "VpeMax": 0.0,          # [m] Maximum reached VPE
        "PdopMax": 0.0,         # Maximum of Position DOP
        "HdopMax": 0.0,         # Maximum of Horizontal DOP
        "VdopMax": 0.0,         # Maximum of Vertical DOP
    }) # End of PosInfo

    return PerfInfo

# End of initializePerfInfo()

def updatePerfEpoch(Conf, PerfInfo, Sod, NumSat, HPE, VPE, PDOP, HDOP, VDOP, HpeHist, VpeHist):
    
    # Store absolute values
    HPE = abs(HPE)
    VPE = abs(VPE)

    # Convergence Time
    if PerfInfo["Convt"] == 0:
        # XPE Convergence Threshold [cm]
        if (HPE < Conf["XPE_TH"][0]/100) and (VPE < Conf["XPE_TH"][1]/100):
            PerfInfo["Convt"] = Sod

    # Statistics POST Convergence Time
    if PerfInfo["Convt"] != 0:
        
        # Number of samples
        PerfInfo["Samples"] += 1

        # Min and Max number of satellites used
        if NumSat < PerfInfo["NsvMin"]: PerfInfo["NsvMin"] = NumSat
        if NumSat > PerfInfo["NsvMax"]: PerfInfo["NsvMax"] = NumSat

        # Maximum HPE and VPE
        if HPE > PerfInfo["HpeMax"]: PerfInfo["HpeMax"] = HPE
        if VPE > PerfInfo["VpeMax"]: PerfInfo["VpeMax"] = VPE
        
        # Maximum PDOP HDOP VDOP 
        if PDOP > PerfInfo["PdopMax"]: PerfInfo["PdopMax"] = PDOP
        if HDOP > PerfInfo["HdopMax"]: PerfInfo["HdopMax"] = HDOP
        if VDOP > PerfInfo["VdopMax"]: PerfInfo["VdopMax"] = VDOP

        # RMS of HPE and VPE
        PerfInfo["HpeRms"] = np.sqrt( \
            (PerfInfo["HpeRms"]**2 * (PerfInfo["Samples"] - 1) + HPE**2) / PerfInfo["Samples"])
        PerfInfo["VpeRms"] = np.sqrt( \
            (PerfInfo["VpeRms"]**2 * (PerfInfo["Samples"] - 1) + VPE**2) / PerfInfo["Samples"])

        # Percentiles - Update Histograms 
        # ----------------------------------
        # Account for the sample in the histogram
        updateHist(HpeHist, HPE, 0.001)
        updateHist(VpeHist, VPE, 0.001)


# End of updatePerfEpoch()

def computeFinalPerf(HpeHist, VpeHist, PerfInfo, Conf):
    # Get the Cumulative Distribution Function
    # -----------------
    CdfHpe = computeCdfFromHistogram(HpeHist, PerfInfo["Samples"])
    CdfVpe = computeCdfFromHistogram(VpeHist, PerfInfo["Samples"])
    
    # 95% Percentile HPE and VPE
    # -----------------
    PerfInfo["Hpe95"] = computePercentile(CdfHpe, 95) 
    PerfInfo["Vpe95"] = computePercentile(CdfVpe, 95) 
    
    # Prepare HPE and VPE Histogram to write
    # -----------------
    HpeHistFinal = prepare_hist(HpeHist, float(Conf["STEP_BIN"]))
    VpeHistFinal = prepare_hist(VpeHist, float(Conf["STEP_BIN"]))
    
    return HpeHistFinal, VpeHistFinal

    


# End of computeFinalPerf()

#####################################
# EXTERNAL FUNCTION
#####################################

# Function to update a histogram with a new sample
def updateHist(Hist, Value, Resolution):
    # Get the bin representative
    Bin = float(int(Value/Resolution)) * Resolution
    
    # Add one more sample to the bin, if it exists
    if Bin in Hist:
        Hist[Bin] = Hist[Bin] + 1

    # Create the bin with one samples if it doesn't exist
    else:
        Hist[Bin] = 1
# End of updateHist()

# Compute the CDF from a Histogram
def computeCdfFromHistogram(Histogram, NSamples):
    # Sort histogram
    SortedHist = OrderedDict({})
    for key in sorted(Histogram.keys()):
        SortedHist[key] = Histogram[key]

    # Initialize CDF and number of samples
    Cdf = OrderedDict({})
    CumulatedSamples = 0

    # Cumulate the frequencies
    for Bin, Samples in SortedHist.items():
        CumulatedSamples = CumulatedSamples + Samples
        Cdf[Bin] = float(CumulatedSamples) / NSamples

    return Cdf
# End of computeCdfFromHistogram()

# Compute the Percentile from the CDF
def computePercentile(Cdf, Percentile):
    for Bin, Freq in Cdf.items():
        # If the cumulated frequency exceeds the Percentile
        # we're trying to find, we found our Percentile
        if (Freq * 100) > Percentile:
            return Bin

    return Bin
# End of computePercentile()

# Prepare Histogram to write
def prepare_hist(hist_dict, step):
    hist_final = []

    for idx, (bin_value, num_samples) in enumerate(sorted(hist_dict.items())):
        bin_id = str(idx).zfill(4)  # Pad with zeros to make it four digits
        bin_min = round(bin_value, 3)
        bin_max = round(bin_value + step, 3)
        num_samples = num_samples
        freq = num_samples / sum(hist_dict.values())

        bin_dict = OrderedDict({
            "BINID": bin_id,
            "BINMIN": bin_min,
            "BINMAX": bin_max,
            "NUMSAMP": num_samples,
            "FREQ": freq
        })

        hist_final.append(bin_dict)

    return hist_final
# End of prepare_hist()

# ------------- END ------------- #