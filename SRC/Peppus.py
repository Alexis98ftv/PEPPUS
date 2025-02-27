#!/usr/bin/env python

########################################################################
# Peppus.py:
# This is the Main Module of PEPPUS tool
#
#  Project:        PEPPUS
#  File:           Peppus.py
#  Date(YY/MM/DD): 06/07/2024
#
#   Author: Alexis Díaz López
#
#
# Usage:
#   Peppus.py $SCEN_PATH
########################################################################

import sys, os

# Update Path to reach COMMON
Common = os.path.dirname(
    os.path.abspath(sys.argv[0])) + '/COMMON'
sys.path.insert(0, Common)

# Import External and Internal functions and Libraries
#----------------------------------------------------------------------
from COMMON import GnssConstants as Const
from InputOutput import readConf
from InputOutput import processConf
from InputOutput import readRcvr
from InputOutput import createOutputFile
from InputOutput import readObsEpoch
from InputOutput import generatePreproFile
from InputOutput import readSatPos
from InputOutput import readSatClk
from InputOutput import readSatApo
from InputOutput import generateCorrFile
from InputOutput import generatePosFile
from InputOutput import generateAmbFile 
from InputOutput import generatePerfFile
from InputOutput import generateXpeFile
from InputOutput import PreproHdr, CorrHdr, PosHdr, AmbHdr, PerfHdr, HpeHdr, VpeHdr
from InputOutput import CSNEPOCHS, CSNPOINTS
from InputOutput import RcvrIdx, ObsIdx
from Preprocessing import runPreProcMeas
from PreprocessingPlots import generatePreproPlots
from Corrections import runCorrectMeas
from CorrectionsPlots import generateCorrPlots
from PerfPlots import generatePerfPlots, generateXpeHistPlots
from Kpvt import computeKpvtSolution
from PosPlots import generatePosPlots
from Perf import initializePerfInfo, computeFinalPerf
from COMMON.Dates import convertJulianDay2YearMonthDay
from COMMON.Dates import convertYearMonthDay2Doy
import numpy as np

#----------------------------------------------------------------------
# INTERNAL FUNCTIONS
#----------------------------------------------------------------------

def displayUsage():
    sys.stderr.write("ERROR: Please provide path to SCENARIO as a unique argument\n")

#######################################################
# MAIN BODY
#######################################################

# Check InputOutput Arguments
if len(sys.argv) != 2:
    displayUsage()
    sys.exit()

# Extract the arguments
Scen = sys.argv[1]

# Select the Configuratiun file name
CfgFile = Scen + '/CFG/peppus.cfg'

# Read conf file
Conf = readConf(CfgFile)
# print(dump(Conf))

# Process Configuration Parameters
Conf = processConf(Conf)

# Select the RCVR Positions file name
RcvrFile = Scen + '/INP/RCVR/' + Conf["RCVR_FILE"]

# Read RCVR Positions file
RcvrInfo = readRcvr(RcvrFile)

# Print header
print( '------------------------------------')
print( '--> RUNNING PEPPUS:')
print( '------------------------------------')

# Loop over RCVRs
#-----------------------------------------------------------------------
for Rcvr in RcvrInfo.keys():
    # Display Message
    print( '\n***-----------------------------***')
    print( '*** Processing receiver: ' + Rcvr + '   ***')
    print( '***-----------------------------***')
    
    # Loop over Julian Days in simulation
    #-----------------------------------------------------------------------
    for Jd in range(Conf["INI_DATE_JD"], Conf["END_DATE_JD"] + 1):
        # Compute Year, Month and Day in order to build input file name
        Year, Month, Day = convertJulianDay2YearMonthDay(Jd)

        # Compute the Day of Year (DoY)
        Doy = convertYearMonthDay2Doy(Year, Month, Day)

        # Display Message
        print( '\n*** Processing Day of Year: ' + str(Doy) + ' ... ***')

        # Define the full path and name to the OBS INFO file to read
        ObsFile = Scen + \
            '/INP/OBS/' + "OBS_%s_Y%02dD%03d.dat" % \
                (Rcvr, Year % 100, Doy)

        # Display Message
        print("INFO: Reading file: %s..." %
        ObsFile)

        # Define the full path and name to the SATPOS file to read and open the file
        SatPosFile = Scen + \
            '/OUT/SAT/' + "SATPOS_Y%02dD%03d.dat" % \
                (Year % 100, Doy)
        SatPosInfo = readSatPos(SatPosFile)

        # Define the full path and name to the SATCLK file to read and open the file
        SatClkFile = Scen + \
            '/OUT/SAT/' + "SATCLK_Y%02dD%03d_30s.dat" % \
                (Year % 100, Doy)
        SatClkInfo = readSatClk(SatClkFile)
        
        # Define the full path and name to the SATAPO file to read and open the file
        SatApoFile = Scen + \
            '/OUT/SAT/' + Conf["SATAPO_FILE"]
        SatApoInfo = readSatApo(SatApoFile)


        ## OUTPUTS
        # If Preprocessing outputs are activated
        if Conf["PREPRO_OUT"] == 1:
            # Define the full path and name to the output PREPRO OBS file
            PreproObsFile = Scen + \
                '/OUT/PPVE/' + "PREPRO_OBS_%s_Y%02dD%03d.dat" % \
                    (Rcvr, Year % 100, Doy)

            # Create output file
            fpreprobs = createOutputFile(PreproObsFile, PreproHdr)

        # If Corrected outputs are activated
        if Conf["PCOR_OUT"] == 1:
            # Define the full path and name to the output PCOR file
            CorrFile = Scen + \
                '/OUT/PCOR/' + "PCOR_%s_Y%02dD%03d.dat" % \
                    (Rcvr, Year % 100, Doy)

            # Create output file
            fcorr = createOutputFile(CorrFile, CorrHdr)
        
        # If PVT outputs are activated
        if Conf["KPVT_OUT"] == 1:
            # Define the full path and name to the output KPVT file
            PosFile = Scen + \
                '/OUT/KPVT/' + "POS_%s_Y%02dD%03d.dat" % \
                    (Rcvr, Year % 100, Doy)

            # Create output file
            fpos = createOutputFile(PosFile, PosHdr)

            AmbFile = Scen + \
                '/OUT/KPVT/' + "AMB_%s_Y%02dD%03d.dat" % \
                    (Rcvr, Year % 100, Doy)

            # Create output file
            famb = createOutputFile(AmbFile, AmbHdr)

        # If PERF outputs are activated
        if Conf["XPEHIST_OUT"] == 1:

            PerfFile = Scen + \
                '/OUT/PERF/' + "PERF_%s_Y%02dD%03d.dat" % \
                    (Rcvr, Year % 100, Doy)

            # Create output file
            fperf = createOutputFile(PerfFile, PerfHdr)

            
            HpeFile = Scen + \
                '/OUT/PERF/' + "HPE_%s_Y%02dD%03d.dat" % \
                    (Rcvr, Year % 100, Doy)

            # Create output file
            fhpe = createOutputFile(HpeFile, HpeHdr)

            VpeFile = Scen + \
                '/OUT/PERF/' + "VPE_%s_Y%02dD%03d.dat" % \
                    (Rcvr, Year % 100, Doy)

            # Create output file
            fvpe = createOutputFile(VpeFile, VpeHdr)
            

        # Initialize Variables
        EndOfFile = False
        ObsInfo = [None]
        PrevPreproObsInfo = {}
        for prn in range(1, Const.MAX_NUM_SATS_CONSTEL + 1):
            PrevPreproObsInfo["G%02d" % prn] = {
                "PrevEpoch": 86400,                                            # Previous SoD with measurements
                "PrevL1": 0.0,                                                 # Previous L1
                "PrevL2": 0.0,                                                 # Previous L2
                "PrevC1": 0.0,                                                 # Previous Smoothed C1
                "PrevP2": 0.0,                                                 # Previous Smoothed C2
                "PrevRej": 1,                                                  # Previous Rejection flag
                
                "CycleSlipBuffIdx": 0,                                         # Index of CS buffer
                "CycleSlipFlagIdx": 0,                                         # Index of CS flag array
                "GF_L_Prev": [0.0] * int(Conf["CYCLE_SLIPS"][CSNPOINTS]),      # Array with previous GF carrier phase observables
                "GF_Epoch_Prev": [0.0] * int(Conf["CYCLE_SLIPS"][CSNPOINTS]),  # Array with previous epochs
                "CycleSlipFlags": [0.0] * int(Conf["CYCLE_SLIPS"][CSNEPOCHS]), # Array with last cycle slips flags
                
                "PrevCode": Const.NAN,                                       # Previous Code IF
                "PrevPhase": Const.NAN,                                      # Previous Phase IF
                "PrevCodeRate": Const.NAN,                                   # Previous Code Rate IF
                "PrevPhaseRate": Const.NAN,                                  # Previous Phase Rate IF
                "PrevStec": Const.NAN,                                         # Previous STEC
                "PrevStecEpoch": Const.NAN,                                    # Previous STEC epoch
                
                "ResetAmb": 1,                                                 # Reset Ambiguities flag
            } # End of SatPreproObsInfo

        SatComPos_1 = {}
        Sod_1 = {}

        # Get receiver reference position
        RcvrRefPosXyz = np.array(\
                            (\
                                RcvrInfo[Rcvr][RcvrIdx["XYZ"]][0],
                                RcvrInfo[Rcvr][RcvrIdx["XYZ"]][1],
                                RcvrInfo[Rcvr][RcvrIdx["XYZ"]][2],
                            )
                        )
        # Before running the Kalman filter, initialize:
        # The state vector of parameters the KF shall estimate
        #-------------------------------------------------------

        # Initialize the State Vector
        X_prev = np.concatenate([
            RcvrRefPosXyz + 3,
            np.array([0, 0]),
            np.zeros(Const.MAX_NUM_SATS_CONSTEL)
        ]) # End of X_prev

        # Initialize the Covariance Matrix
        P_prev = np.diag(np.concatenate([
            np.square(Conf["COVARIANCE_INI"][:5]),  
            np.full(Const.MAX_NUM_SATS_CONSTEL, np.square(Conf["COVARIANCE_INI"][5]))  
        ])) # End of P_prev

        # Initialize the Sod_Prev to compute DeltaT in computeKpvtSolution()
        Sod_Prev = -1 # End of Sod_Prev

        # Initialize the Perf Dict to update it on fly (kpvt.py)
        PerfInfo = initializePerfInfo(RcvrInfo[Rcvr], Doy)

        # Initialize histograms of the parameters
        # we want to describe
        HpeHist = {}
        VpeHist = {}

        # Open OBS file
        with open(ObsFile, 'r') as fobs:
            # Read header line of OBS file
            fobs.readline()

            # LOOP over all Epochs of OBS file
            # ----------------------------------------------------------
            while not EndOfFile:

                # If ObsInfo is not empty
                if ObsInfo != []:

                    # Read Only One Epoch
                    ObsInfo = readObsEpoch(fobs)

                    # If ObsInfo is empty, exit loop
                    if ObsInfo == []:
                        break

                    # Preprocess OBS measurements
                    # ----------------------------------------------------------
                    PreproObsInfo = runPreProcMeas(Conf, RcvrInfo[Rcvr], ObsInfo, PrevPreproObsInfo)

                    # If PREPRO outputs are requested
                    if Conf["PREPRO_OUT"] == 1:
                        # Generate output file
                        generatePreproFile(fpreprobs, PreproObsInfo)

                    # Get SoD
                    Sod = int(float(ObsInfo[0][ObsIdx["SOD"]]))

                    # The rest of the analyses are executed every configured sampling rate
                    if(Sod % Conf["SAMPLING_RATE"] == 0):
                        # Correct measurements and estimate the variances with SBAS information
                        # ----------------------------------------------------------
                        CorrInfo = runCorrectMeas(Conf, RcvrInfo[Rcvr], ObsInfo, PreproObsInfo, 
                        SatPosInfo, SatClkInfo, SatApoInfo, SatComPos_1, Sod_1)
                        
                        # If PCOR outputs are requested
                        if Conf["PCOR_OUT"] == 1:
                            # Generate output file
                            generateCorrFile(fcorr, CorrInfo)

                        # Estimate the Kalman PVT solution 
                        # ----------------------------------------------------------
                        PosInfo, X_prev, P_prev, Sod_Prev = computeKpvtSolution(
                            Conf, RcvrInfo[Rcvr], ObsInfo, CorrInfo, 
                            X_prev, P_prev, Sod_Prev, PrevPreproObsInfo, 
                            PerfInfo, HpeHist, VpeHist
                            )

                        # If KPVT outputs are requested
                        if Conf["KPVT_OUT"] == 1:
                            # Generate output file
                            generatePosFile(fpos, PosInfo)
                            generateAmbFile(famb, PosInfo)
                        
                        

                # End of if ObsInfo != []:

                else:
                    EndOfFile = True

                # End of if ObsInfo != []:

            # End of while not EndOfFile:

        # End of with open(ObsFile, 'r') as f:

        # Compute the final Perf
        HpeHistFinal, VpeHistFinal = computeFinalPerf(HpeHist, VpeHist, PerfInfo, Conf)

        # If XPEHIST outputs are requested
        if Conf["XPEHIST_OUT"] == 1:
            # Generate output file
            # Generate PERF output file
            generateXpeFile(fhpe, HpeHistFinal, fvpe, VpeHistFinal)
            generatePerfFile(fperf, PerfInfo)

        # If PREPRO outputs are requested
        if Conf["PREPRO_OUT"] == 1:
            # Close PREPRO output file
            fpreprobs.close()

            # Display Message
            print("INFO: Reading file: %s and generating PREPRO figures..." %
            PreproObsFile)

            # Generate Preprocessing plots
            generatePreproPlots(PreproObsFile)

        # If PCOR outputs are requested
        if Conf["PCOR_OUT"] == 1:
            # Close PCOR output file
            fcorr.close()
        
            # Display Message
            print("INFO: Reading file: %s and generating PCOR figures..." %
            CorrFile)
        
            # Generate PCOR plots
            generateCorrPlots(CorrFile)
        
        # If KPVT outputs are requested
        if Conf["KPVT_OUT"] == 1:
            # Close KPVT output file
            fpos.close()
            famb.close()

            # Display Message
            print("INFO: Reading file: %s and generating POS figures..." %
            PosFile)
            # Generate KPVT-POS plots
            generatePosPlots(PosFile, AmbFile)

        # If PERF outputs are activated
        if Conf["XPEHIST_OUT"] == 1:
            # Close PERF output file
            fperf.close()
            fhpe.close()
            fvpe.close()

            # Display Message
            print("INFO: Reading files: %s and %s and generating the Hist figures..." % 
            (HpeFile, VpeFile))
            # Generate PERF-HIST plots
            generateXpeHistPlots(HpeFile, VpeFile)
        
        

    # End of JD loop

# End of RCVR loop

# PEPPUS PERFORMANCES
# ----------------------------------------------
# Display Message
print('\nINFO: Reading files and generating the Performances...')
generatePerfPlots()
# ----------------------------------------------

print( '\n------------------------------------')
print( '--> END OF PEPPUS ANALYSIS')
print( '------------------------------------')

#######################################################
# End of Peppus.py
#######################################################
