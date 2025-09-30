from .water_heat_flux import water_heat_flux

def AquaSEBS():
    # dew-point temperature in Celsius
    Td_C = Ta_C - ((100 - RH * 100) / 5.0)
    self.diagnostic(Td_C, "Td_C", date_UTC, target)

    if wind_speed is None:
        wind_speed = self.wind_speed(time_UTC=time_UTC, geometry=geometry)

    # water heat flux
    W = water_heat_flux(
        ST_C=ST_C,
        Td_C=Td_C,
        windspeed_mps=wind_speed,
        SWnet=SWnet
    )

    W = rt.clip(W, 0, W_MAX_PROPORTION * Rn)
    W = W.mask(water)
    self.diagnostic(W, "W", date_UTC, target, blank_OK=True)

    # calculate soil evaporation (LEs) from relative surface wetness, soil moisture constraint,
    # priestley taylor coefficient, epsilon = delta / (delta + gamma), net radiation of the soil,
    # and soil heat flux
    LE_soil = rt.clip((fwet + fREW * (1 - fwet)) * PT_ALPHA * epsilon * (Rn_soil - G), 0, None)
    self.diagnostic(LE_soil, "LE_soil", date_UTC, target)

    # canopy transpiration

    # calculate net radiation of the canopy from net radiation of the soil
    Rn_canopy = Rn - Rn_soil
    self.diagnostic(Rn_canopy, "Rn_canopy", date_UTC, target)

    # calculate potential evapotranspiration (pET) from net radiation, and soil heat flux

    PET_water = PT_ALPHA * epsilon * (Rn - W)
    self.diagnostic(PET_water, "PET_water", date_UTC, target, blank_OK=True)
    PET_land = PT_ALPHA * epsilon * (Rn - G)
    self.diagnostic(PET_land, "PET_land", date_UTC, target)

    PET = rt.where(
        water,
        PET_water,
        PET_land
    )
