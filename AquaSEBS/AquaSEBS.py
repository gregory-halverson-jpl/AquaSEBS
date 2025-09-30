from typing import Union
import numpy as np
from datetime import datetime
import rasters as rt
from rasters import Raster, RasterGeometry
from GEOS5FP import GEOS5FP
from check_distribution import check_distribution
from priestley_taylor import epsilon_from_Ta_C, GAMMA_PA
from verma_net_radiation import verma_net_radiation

from .constants import *

from .water_heat_flux import water_heat_flux

W_MAX_PROPORTION = 0.5  # Maximum proportion of net radiation that can be used for water heat flux
PT_ALPHA = 1.26  # Priestley-Taylor coefficient

## TODO use NASADEM surface water body extent to mask out land when processing on rasters

def AquaSEBS(
        WST_C: Union[Raster, np.ndarray],
        emissivity: Union[Raster, np.ndarray] = None,
        albedo: Union[Raster, np.ndarray] = None,
        Ta_C: Union[Raster, np.ndarray] = None,
        RH: Union[Raster, np.ndarray] = None,
        Td_C: Union[Raster, np.ndarray] = None,
        windspeed_mps: Union[Raster, np.ndarray] = None,
        SWnet: Union[Raster, np.ndarray] = None,
        Rn_Wm2: Union[Raster, np.ndarray] = None,
        W_Wm2: Union[Raster, np.ndarray] = None,
        SWin_Wm2: Union[Raster, np.ndarray] = None,
        geometry: RasterGeometry = None,
        time_UTC: datetime = None,
        GEOS5FP_connection: GEOS5FP = None,
        gamma_Pa: Union[Raster, np.ndarray, float] = GAMMA_PA,
        resampling: str = RESAMPLING_METHOD):
    # Compute net radiation if not provided, using albedo, ST_C, and emissivity
    if Rn_Wm2 is None and albedo is not None and WST_C is not None and emissivity is not None:
        # Retrieve incoming shortwave if not provided
        if SWin_Wm2 is None and geometry is not None and time_UTC is not None:
            SWin_Wm2 = GEOS5FP_connection.SWin(
                time_UTC=time_UTC,
                geometry=geometry,
                resampling=resampling
            )

        # Calculate net radiation using Verma et al. method
        Rn_results = verma_net_radiation(
            SWin_Wm2=SWin_Wm2,
            albedo=albedo,
            ST_C=ST_C,
            emissivity=emissivity,
            Ta_C=Ta_C,
            RH=RH,
            geometry=geometry,
            time_UTC=time_UTC,
            resampling=resampling,
            GEOS5FP_connection=GEOS5FP_connection
        )

        Rn_Wm2 = Rn_results["Rn_Wm2"]

    if Rn_Wm2 is None:
        raise ValueError("net radiation (Rn_Wm2) not given")

    if W_Wm2 is None:
        # water heat flux
        W_Wm2 = water_heat_flux(
            WST_C=WST_C,
            Ta_C=Ta_C,
            Td_C=Td_C,
            windspeed_mps=windspeed_mps,
            SWnet=SWnet,
            geometry=geometry,
            time_UTC=time_UTC,
            GEOS5FP_connection=GEOS5FP_connection,
            resampling=resampling
        )

        W_Wm2 = rt.clip(W_Wm2, 0, W_MAX_PROPORTION * Rn_Wm2)
    
    check_distribution(W_Wm2, "W_Wm2")

    epsilon = epsilon_from_Ta_C(
        Ta_C=Ta_C,
        gamma_Pa=gamma_Pa
    )

    LE_Wm2 = PT_ALPHA * epsilon * (Rn_Wm2 - W_Wm2)
    check_distribution(LE_Wm2, "LE_Wm2")

    return LE_Wm2

