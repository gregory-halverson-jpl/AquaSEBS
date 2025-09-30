from typing import Union
import numpy as np
from datetime import datetime
from rasters import Raster, RasterGeometry
from GEOS5FP import GEOS5FP
from check_distribution import check_distribution

from .constants import *

def water_heat_flux(
        WST_C: Union[Raster, np.ndarray],
        albedo: Union[Raster, np.ndarray] = None,
        Ta_C: Union[Raster, np.ndarray] = None,
        RH: Union[Raster, np.ndarray] = None,
        Td_C: Union[Raster, np.ndarray] = None,
        windspeed_mps: Union[Raster, np.ndarray] = None,
        SWnet: Union[Raster, np.ndarray] = None,
        geometry: RasterGeometry = None,
        time_UTC: datetime = None,
        GEOS5FP_connection: GEOS5FP = None,
        resampling: str = RESAMPLING_METHOD):
    """
    Calculate water heat flux based on input parameters.

    This function computes the water heat flux, which represents the energy exchange
    between a water surface and the atmosphere. The calculation is based on the AquaSEBS
    model, incorporating factors such as water surface temperature, dew-point temperature,
    wind speed, and net shortwave radiation.

    References:
    - AquaSEBS model: http://www.mdpi.com/2072-4292/8/7/583

    Parameters:
    :param WST_C: Water surface temperature in Celsius.
    :param Ta_C: Air temperature in Celsius (optional, can be inferred).
    :param RH: Relative humidity as a fraction (0-1) (optional, can be inferred).
    :param Td_C: Dew-point temperature in Celsius (optional, can be inferred).
    :param windspeed_mps: Wind speed in meters per second (optional, can be inferred).
    :param SWnet: Net shortwave radiation in Watts per square meter (optional, can be inferred).
    :param geometry: Raster geometry for spatial data (optional).
    :param time_UTC: UTC timestamp for temporal data (optional).
    :param GEOS5FP_connection: Connection to GEOS5FP data source (optional).
    :param resampling: Resampling method for spatial data (default: RESAMPLING_METHOD).

    Returns:
    :return: Water heat flux in Watts per square meter.
    """
    # If geometry is not provided, try to infer from surface temperature raster
    if geometry is None and isinstance(WST_C, Raster):
        geometry = WST_C.geometry

    # Create GEOS5FP connection if not provided
    if GEOS5FP_connection is None:
        GEOS5FP_connection = GEOS5FP()

    if WST_C is None:
        raise ValueError("water surface temperature (WST_C) not given")
    
    check_distribution(WST_C, "WST_C")

    if Td_C is None and geometry is not None and time_UTC is not None:
        # Retrieve air temperature if not provided, using GEOS5FP and geometry/time
        if Ta_C is None:
            Ta_C = GEOS5FP_connection.Ta_C(
                time_UTC=time_UTC,
                geometry=geometry,
                resampling=resampling
            )

        check_distribution(Ta_C, "Ta_C")
        
        # Retrieve relative humidity if not provided, using GEOS5FP and geometry/time
        if RH is None and geometry is not None and time_UTC is not None:
            RH = GEOS5FP_connection.RH(
                time_UTC=time_UTC,
                geometry=geometry,
                resampling=resampling
            )

        check_distribution(RH, "RH")

        # Calculate dew-point temperature in Celsius
        Td_C = Ta_C - ((100 - RH * 100) / 5.0)
    

    if Td_C is None:
        raise ValueError("dew-point temperature (Td_C) not given")

    check_distribution(Td_C, "Td_C")

    if windspeed_mps is None and geometry is not None and time_UTC is not None:
        # Retrieve wind speed in meters per second if not provided, using GEOS5FP and geometry/time
        windspeed_mps = GEOS5FP_connection.wind_speed(
            time_UTC=time_UTC,
            geometry=geometry,
            resampling=resampling
        )

    if windspeed_mps is None:
        raise ValueError("wind-speed (windspeed_mps) not given")

    check_distribution(windspeed_mps, "windspeed_mps")

    if SWnet is None and geometry is not None and time_UTC is not None:
        SWin = GEOS5FP_connection.SWin(
            time_UTC=time_UTC,
            geometry=geometry,
            resampling=resampling
        )

        check_distribution(SWin, "SWin")

        if albedo is None:
            albedo = GEOS5FP_connection.ALBEDO(
                time_UTC=time_UTC,
                geometry=geometry,
                resampling=resampling
            )
        
        check_distribution(albedo, "albedo")

        SWnet = SWin * (1 - albedo)
    
    if SWnet is None:
        raise ValueError("net shortwave radiation (SWnet) not given")

    check_distribution(SWnet, "SWnet")

    # Calculate temperature difference (Tn)
    Tn = 0.5 * (WST_C - Td_C)  # Half the difference between water surface temperature and dew-point temperature
    check_distribution(Tn, "Tn")

    # Calculate evaporation efficiency (η)
    η = 0.35 + 0.015 * WST_C + 0.0012 * (Tn ** 2)  # Accounts for baseline efficiency, temperature, and non-linear effects
    check_distribution(η, "η")

    # Scale wind speed (S)
    S = 3.3 * windspeed_mps  # Wind enhances evaporation and heat exchange
    check_distribution(S, "S")

    # Calculate heat transfer coefficient (β)
    β = 4.5 + 0.05 * WST_C + (η + 0.47) * S  # Combines temperature, evaporation efficiency, and wind effects
    check_distribution(β, "β")

    # Calculate effective temperature (Te)
    Te = Td_C + SWnet * β  # Combines dew-point temperature and radiation effects
    check_distribution(Te, "Te")

    # Calculate water heat flux (W)
    W_Wm2 = β * (Te - WST_C)  # Final energy exchange rate between water surface and atmosphere
    check_distribution(W_Wm2, "W_Wm2")

    return W_Wm2
