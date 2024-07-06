#!/usr/bin/env python

########################################################################
# PEPPUS/SRC/Kpvt.py:
# This is the KPVT Module of PEPPUS tool
#
#  Project:        PEPPUS
#  File:           Kpvt.py
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
from COMMON.Coordinates import xyz2llh
from InputOutput import RcvrIdx, ObsIdx, CorrIdx
from Corrections import computeTropoMpp
from Perf import updatePerfEpoch
import numpy as np
np.set_printoptions(linewidth = 1000, suppress=True)


def computeKpvtSolution(
        Conf, Rcvr, ObsInfo, CorrInfo, X_prev, P_prev, Sod_Prev, PrevPreproObsInfo, PerfInfo, HpeHist, VpeHist):

    # Purpose: compute the PVT navigation solution through a Kalman Filter.

    #          More in detail, this function handles the following:
    #          tasks:

    #             *  Update State Vector through the Process Matrix [F]
    #             *  Update Covariance Matrix through the Process Noise Matrix [Q]
    #             *  Build the Observation [G] and Weighting Matrices [W]
    #             *  Build the [S] Matrix and DOP Matrix [D]
    #             *  Build the Measurement Residuals Vector [rho]
    #             *  Apply the Kalman Filter
    #             *  Estimate the Receiver Position Coordinates and Clock
    #             *  Estimate the Position Error (HPE, VPE)
    #             *  Estimate the DOPs (PDOP, GDOP, HDOP, VDOP)

    # Parameters
    # ==========
    # Conf: dict
    #         Configuration dictionary
    # Rcvr: list
    #         Receiver information: position, masking angle...
    # ObsInfo: list
    #         OBS info for current epoch
    #         ObsInfo[1][1] is the second field of the 
    #         second satellite
    # CorrInfo: dict
    #         Corrected measurements for current epoch per sat
    #         CorrInfo["G01"]["CorrectedPsr"]

    # Returns
    # =======
    # PosInfo: dict
    #         Receiver Position Information for current epoch
    #         PosInfo["HPE"]


    # Get receiver reference position
    RcvrRefPosXyz = np.array(\
                            (\
                                Rcvr[RcvrIdx["XYZ"]][0],
                                Rcvr[RcvrIdx["XYZ"]][1],
                                Rcvr[RcvrIdx["XYZ"]][2],
                            )
                        )


    # Max number of Satellites 
    N = Const.MAX_NUM_SATS_CONSTEL # 36

    # Get number of satellites in view and valid for solution
    NumSatVis = len(CorrInfo)
    NumSat = len(list(filter(lambda x: x[1]["Flag"] == 1, CorrInfo.items()))) #Note: x[0]=SatLabel
 
    # Get SoD
    Sod = int(float(ObsInfo[0][ObsIdx["SOD"]]))

    # Get DoY
    Doy = int(float(ObsInfo[0][ObsIdx["DOY"]]))

    # Initialize output
    PosInfo = OrderedDict({
        "Sod": 0.0,             # Second of day
        "Doy": 0,               # Day of year
        "Lon": 0.0,             # Receiver Estimated Longitude
        "Lat": 0.0,             # Receiver Estimated Latitude
        "Alt": 0.0,             # Receiver Estimated Altitude
        "Clk": 0.0,             # Receiver Estimated Clock Bias
        "Sol": 0,               # 0: No Solution; 1: OK
        "NumSatVis": 0,         # Number of Visible Satellites
        "NumSat": 0,            # Number of Satellites solution
        "Hpe": 0.0,             # HPE
        "Vpe": 0.0,             # VPE
        "Epe": 0.0,             # EPE
        "Npe": 0.0,             # NPE
        "Hdop": 0.0,            # HDOP
        "Vdop": 0.0,            # VDOP
        "Pdop": 0.0,            # PDOP
        "Tdop": 0.0,            # TDOP
        "Amb": np.zeros(N),     # Ambiguities of PRNs 1-32
    }) # End of PosInfo


    # Prepare outputs
    # Get SoD
    PosInfo["Sod"] = Sod
    # Get DoY
    PosInfo["Doy"] = Doy
    # Get Rcvr
    PosInfo["Rcvr"] = Rcvr[RcvrIdx["ACR"]]
    # Get NumSatVis
    PosInfo["NumSatVis"] = NumSatVis
    # Get NumSat 
    PosInfo["NumSat"] = NumSat
    
    # Compute solution if at least 4 satellites are usable
    if NumSat >= 4:
        
        # Recover previous values StateVector and CovMatrix for each satellite in view
        X_prev_sliced, P_prev_sliced, slice_idx = slicePrev(CorrInfo, X_prev, P_prev)

        # Build [G]: Observation Matrix
        G, Genu, mppList = buildGmatrix(CorrInfo, X_prev_sliced, NumSat)
        # Build [W]: Weighting Matrix
        W = buildWmatrix(CorrInfo, NumSat, Conf)

        # Compute DOPs (Ref: ESA GNSS Book Vol I Section 6.1.3.2)
        HDOP, VDOP, PDOP, TDOP = computeDOP(Genu)
        # PREPARE OUTPUT PosFile
        PosInfo["Hdop"] = HDOP
        PosInfo["Vdop"] = VDOP
        PosInfo["Pdop"] = PDOP
        PosInfo["Tdop"] = TDOP
        # -----------------------
        
        # Check if PDOP is below the configured threshold
        if PDOP <= Conf["PDOP_MAX"]:
            
            # Build Process Matrix [F]: Considerer all the states as constants
            F = buildFmatrix(NumSat)

            # DeltaT between Sod and Sod_Prev
            DeltaT = Sod - Sod_Prev
            # Store Sod in Sod_Prev
            Sod_Prev = Sod

            # Build Process Noise Matrix [Q]
            Q = buildQmatrix(NumSat, Conf, DeltaT)

            # Reset Ambiguities State and Covariance if ResetAmb flag is set to 1
            # Inflate Ambiguity Process Noise Sigma if a Cycle slip was detected
            # (ResetAmb = 2) settings it to Conf.CS_SIGMA
            
            resetAmbFunction(PrevPreproObsInfo, CorrInfo, X_prev_sliced, P_prev_sliced, Conf)

            # PREDICT new State and Covariance
            #-------------------------------------
            # Predict new State
            X_predict = F @ X_prev_sliced

            # Predict new Covariance
            P_predict = F @ P_prev_sliced @ F.T + Q

            # Compute Kalman Gain [K]
            #-------------------------------------
            S = G @ P_predict @ G.T + np.linalg.inv(W)
            K = P_predict @ G.T @ np.linalg.inv(S)

            # Get the estimated PVT solution: Position and Clock applying KF
            # Linearize the system around X_predict
            #-------------------------------------
            # Update Geometrical Range based on estimated Rcvr Position
            GeomRange = computeGeomRange(X_predict, CorrInfo)

            # Compute Measurement Residuals
            DeltaY = computeMeasurementResiduals(CorrInfo, GeomRange, X_predict, mppList)

            # Get Delta State
            DeltaX_predict = X_prev_sliced - X_predict   # 0 

            # Get Delta State with the Measurements
            DeltaX = DeltaX_predict + K @ (DeltaY - G @ DeltaX_predict)

            # Update State
            X = X_predict + DeltaX
            
            # Obtain the Estimated Position for RCVR
            Long_Est, Lat_Est, Alt_Est = xyz2llh(X[0],X[1],X[2])

            # Update Covariance Matrix
            I = np.eye(5+NumSat)
            P = (I - K @ G) @ P_predict

            # Get Position Errors in ENU
            HPE, VPE, EPE, NPE = computePositionErrors(Rcvr, X)


            # Update Performance intermediate information
            # -------------------------------------------
            updatePerfEpoch(Conf, PerfInfo, Sod, NumSat, HPE, VPE, PDOP, HDOP, VDOP, HpeHist, VpeHist)
            # -------------------------------------------
            
            # PREPARE OUTPUT PosFile
            PosInfo["Sol"] = 1
            PosInfo["Lon"] = Long_Est
            PosInfo["Lat"] = Lat_Est
            PosInfo["Alt"] = Alt_Est
            PosInfo["Clk"] = X[3]
            PosInfo["Hpe"] = HPE
            PosInfo["Vpe"] = VPE
            PosInfo["Epe"] = EPE
            PosInfo["Npe"] = NPE
            
            # PREPARE OUTPUT AmbFile
            PRN_Amb = np.array(slice_idx[5:])
            PosInfo["Amb"][PRN_Amb - 5] = X[5:]

            #Build again the whole matrix X (containing columns for each satellite)
            X_prev[slice_idx] = X
            P_prev[np.ix_(slice_idx, slice_idx)] = P

        # End of PDOP <= Conf["PDOP_MAX"]
    # End of NumSat >= 4
    
    #Keep the updated State Vector and Covariance for the next epoch
    return PosInfo, X_prev, P_prev, Sod_Prev

#######################################################
# EXTERNAL FUNCTIONS
#######################################################

def slicePrev(CorrInfo, X_prev, P_prev):
    # Obtain the positions of Sats with Flag = 1  
    PrnPos = [int(''.join(filter(str.isdigit, SatLabel))) - 1 for SatLabel, SatCorr in CorrInfo.items() if SatCorr['Flag'] == 1]

    # Obtain X,Y,Z,Clk and ZTd
    PosClkZtd = X_prev[:5]

    # Obtain the ambiguities for the usable satellites
    Ambiguities = X_prev[5:][PrnPos]

    # Crear X_0_sliced concatenando los primeros 5 valores y las columnas seleccionadas
    X_prev_sliced = np.concatenate((PosClkZtd, Ambiguities))

    # Obtain the index of the rows and columns we want for the matrix P_0_sliced
    slice_idx = np.hstack((np.arange(5), np.array(PrnPos)+5))

    # Create P_0_sliced using the selected rows and columns
    P_prev_sliced = P_prev[np.ix_(slice_idx, slice_idx)]
    
    return X_prev_sliced, P_prev_sliced, slice_idx

def buildGmatrix(CorrInfo, X_prev_sliced, NumSat):
    # Filter the satellites and extract data using list comprehensions
    filtered_satellites = [(sat[1]["SatX"], sat[1]["SatY"], sat[1]["SatZ"], sat[1]["Elevation"], sat[1]["Azimuth"]) for sat in CorrInfo.items() if sat[1]["Flag"] == 1]

    # Unpack the filtered data into separate lists
    satXlist, satYlist, satZlist, satElevlist, satAzimlist = zip(*filtered_satellites)

    # Compute mppList using vectorized computation
    mppList = np.array([computeTropoMpp(element) for element in satElevlist])

    raws = NumSat
    columns = 5 # X Y Z CLK Mpp
    
    #------------------------------------------------
    # Geometry Matrix in ECEF
    #------------------------------------------------
    geomrange = np.sqrt((satXlist - X_prev_sliced[0])**2 + (satYlist - X_prev_sliced[1])**2 + (satZlist - X_prev_sliced[2])**2)

    matrix = np.zeros((raws, columns))

    matrix[:, 0] = (X_prev_sliced[0] - satXlist) / geomrange
    matrix[:, 1] = (X_prev_sliced[1] - satYlist) / geomrange
    matrix[:, 2] = (X_prev_sliced[2] - satZlist) / geomrange
    matrix[:, 3] = 1  # CLK
    matrix[:, 4] = mppList
 
    # Ambiguities
    matrixAmb1 = np.zeros((NumSat,NumSat))  # Codes
    matrixAmb2 = np.eye(NumSat)            # Phases
    # Concatenate arrays horizontally
    matrixTop = np.hstack((matrix,matrixAmb1))
    matrixBot = np.hstack((matrix,matrixAmb2))

    # Concatenate arrays Vertically
    GmatrixECEF = np.vstack((matrixTop,matrixBot))

    #------------------------------------------------
    # Geometry Matrix in ENU
    #------------------------------------------------
    # Convertir elevación y azimut a radianes
    satElevlist_rad = np.radians(satElevlist)
    satAzimlist_rad = np.radians(satAzimlist)
    GmatrixENU = np.zeros((raws,4)) # X Y Z CLK
    # Calc cos and sin
    cos_elev = np.cos(satElevlist_rad)
    sin_elev = np.sin(satElevlist_rad)
    cos_azim = np.cos(satAzimlist_rad)
    sin_azim = np.sin(satAzimlist_rad)
    # Build G enu matrix
    GmatrixENU[:, 0] = -cos_elev * sin_azim  # X
    GmatrixENU[:, 1] = -cos_elev * cos_azim  # Y
    GmatrixENU[:, 2] = -sin_elev             # Z
    GmatrixENU[:, 3] = 1                     # CLK

    return GmatrixECEF, GmatrixENU, mppList

def buildWmatrix(CorrInfo, NumSat, Conf):
    # Obtain UERE for each satellite to build the matrix
    filtered_satellites = filter(lambda x: x[1]["Flag"] == 1, CorrInfo.items())
    uereList = [satCorr[1]["SigmaUere"] for satCorr in filtered_satellites]

    # UERE**2
    uereList = np.square(uereList)

    # Phase measurement sigma in CONF
    pSigmaList = [(Conf["PHASE_SIGMA"])**2] * NumSat

    # Weight = inverse of sigma
    uereWeightedList = [1/item for item in uereList]
    pSigmaWeightedList = [1/item for item in pSigmaList]

    matrixCode = np.diag(uereWeightedList)
    matrixPhase = np.diag(pSigmaWeightedList)
    matrixZero = np.zeros((NumSat,NumSat))

    # Concatenate arrays horizontally
    matrixTop = np.hstack((matrixCode,matrixZero))
    matrixBot = np.hstack((matrixZero,matrixPhase))
    # Concatenate arrays Vertically
    Wmatrix = np.vstack((matrixTop,matrixBot))
    
    return Wmatrix

def computeDOP(Genu):

    DOP = np.linalg.inv(np.dot(Genu.T,Genu))

    hdop = np.sqrt(DOP[0, 0] + DOP[1, 1])
    vdop = np.sqrt(DOP[2, 2])
    pdop = np.sqrt(DOP[0, 0] + DOP[1, 1] + DOP[2, 2])
    tdop = np.sqrt(DOP[3, 3])

    return hdop, vdop, pdop, tdop

def buildFmatrix(NumSat):

    Fdiagonal = [1]*(5+NumSat)
    F = np.diag(Fdiagonal)

    return F

def buildQmatrix(NumSat, Conf, DeltaT):
    n = 5 + NumSat

    Q = np.zeros((n, n))

    # Receiver Clock Process Noise sigma [m/sqrt(s)]
    Q[3][3] = (Conf["RCVRCLK_NOISE"]**2) * DeltaT
    # Delta ZTD Process Noise sigma [m/sqrt(h)]
    Q[4][4] = (Conf["DZTD_NOISE"]**2) * (DeltaT/Const.S_IN_H)

    return Q

def computeGeomRange(X_predict, CorrInfo):
    # Extracting satellite coordinates from CorrInfo
    SatX = np.array([sat["SatX"] for sat in CorrInfo.values() if sat["Flag"] == 1])
    SatY = np.array([sat["SatY"] for sat in CorrInfo.values() if sat["Flag"] == 1])
    SatZ = np.array([sat["SatZ"] for sat in CorrInfo.values() if sat["Flag"] == 1])

    # Calculate geometric range using vectorized operations
    GeomRange = np.sqrt((SatX - X_predict[0])**2 + (SatY - X_predict[1])**2 + (SatZ - X_predict[2])**2)

    return GeomRange

def computeMeasurementResiduals(CorrInfo, GeomRange, X_predict, mppList):
    filtered_corrections = [sat for sat in CorrInfo.values() if sat["Flag"] == 1]

    # Calculate residuals using vectorized operations
    CodeResiduals = np.array([sat["CorrCode"] - GeomRange[i] - X_predict[3] - X_predict[4] * mppList[i] for i, sat in enumerate(filtered_corrections)])
    PhaseResiduals = np.array([sat["CorrPhase"] - GeomRange[i] - X_predict[3] - X_predict[4] * mppList[i] - X_predict[5 + i] for i, sat in enumerate(filtered_corrections)])

    DeltaY = np.hstack((CodeResiduals, PhaseResiduals))

    return  DeltaY

def computePositionErrors(Rcvr, X):
    # B.2.2 From ECEF to ENU Coordinates
    # Obtain Lat, Lon from receiver REF xyz
    Lat = np.deg2rad(Rcvr[RcvrIdx["LAT"]])
    Lon = np.deg2rad(Rcvr[RcvrIdx["LON"]])
    #Create transformation matrix
    R = np.zeros((3,3)) 
    R[0][0] = -np.sin(Lon)
    R[0][1] = np.cos(Lon)
    R[1][0] = -np.cos(Lon) * np.sin(Lat)
    R[1][1] = -np.sin(Lon) * np.sin(Lat)
    R[1][2] = np.cos(Lat)
    R[2][0] = np.cos(Lon) * np.cos(Lat)
    R[2][1] = np.sin(Lon) * np.cos(Lat)
    R[2][2] = np.sin(Lat)
    # Create delta x,y,z as: Rcvr_xyz_EST - Rcvr_xyz_REF
    Delta_XYZ = [(X[0] - Rcvr[RcvrIdx["XYZ"]][0]), 
                 (X[1] - Rcvr[RcvrIdx["XYZ"]][1]), 
                 (X[2] - Rcvr[RcvrIdx["XYZ"]][2])]
    
    Delta_ENU = R @ Delta_XYZ
    D_E = Delta_ENU[0]
    D_N = Delta_ENU[1]
    D_U = Delta_ENU[2]

    HPE = np.sqrt((D_E**2)+(D_N**2))
    VPE = D_U # Remove absolute value for output. Abs for statistics

    return HPE, VPE, D_E, D_N

def resetAmbFunction(PrevPreproObsInfo, CorrInfo, X_prev_sliced, P_prev_sliced, Conf):
    # Reset Ambiguities State and Covariance if ResetAmb flag is set to 1
    # Inflate Ambiguity Process Noise Sigma if a Cycle slip was detected
    # (ResetAmb = 2) settings it to Conf.CS_SIGMA
    satsInView = [sat for sat, info in CorrInfo.items() if info["Flag"] == 1]

    # DATA GAP
    satsAmb1 = [sat for sat, info in CorrInfo.items() if info["Flag"] == 1 and PrevPreproObsInfo.get(sat, {}).get("ResetAmb", 0) == 1]
    Amb1idx = [idx for idx, sat in enumerate(satsInView) if sat in satsAmb1]

    if Amb1idx:
        for idx in Amb1idx:
            X_prev_sliced[5 + idx] = 0
            P_prev_sliced[5 + idx, :] = 0
            P_prev_sliced[:, 5 + idx] = 0
            P_prev_sliced[5 + idx, 5 + idx] = Conf["COVARIANCE_INI"][5]**2

        for sat in satsAmb1:
            PrevPreproObsInfo[sat]["ResetAmb"] = 0

    # CYCLE SLIP
    satsAmb2 = [sat for sat, info in CorrInfo.items() if info["Flag"] == 1 and PrevPreproObsInfo.get(sat, {}).get("ResetAmb", 0) == 2]
    Amb2idx = [idx for idx, sat in enumerate(satsInView) if sat in satsAmb2]

    if Amb2idx:
        for idx in Amb2idx:
            # CS sigma [m]
            P_prev_sliced[5 + idx, 5 + idx] = Conf["CS_SIGMA"]**2

        for sat in satsAmb2:
            PrevPreproObsInfo[sat]["ResetAmb"] = 0

#######################################################
# End of Kpvt.py
#######################################################