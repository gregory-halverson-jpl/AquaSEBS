# AquaSEBS

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/AquaSEBS.svg)](https://badge.fury.io/py/AquaSEBS)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**AquaSEBS** is a Python implementation of the Abdelrady et al. (2016) and Fisher et al. (2023) methodology for estimating water surface evaporation and energy balance components over freshwater and saline water bodies using satellite remote sensing data and meteorological inputs. The package implements the AquaSEBS (Aquatic Surface Energy Balance System) model, which combines Abdelrady et al.'s equilibrium temperature model for water heat flux with Fisher et al.'s adaptation for complete evaporation estimation using the Priestley-Taylor approach.

Gregory H. Halverson (they/them)<br>
[gregory.h.halverson@jpl.nasa.gov](mailto:gregory.h.halverson@jpl.nasa.gov)<br>
NASA Jet Propulsion Laboratory 329G

## Overview

This package implements the **Abdelrady et al. (2016) and Fisher et al. (2023) combined methodology** for physics-based estimation of:
- **Latent heat flux (evaporation)** using Priestley-Taylor equation (Fisher et al., 2023 adaptation)
- **Water heat flux** using equilibrium temperature model (Abdelrady et al., 2016)
- **Net radiation components** using Verma et al. method

The implementation follows the Abdelrady et al. (2016) formulations for water heat flux exactly, combined with Fisher et al. (2023) adaptations for complete evaporation estimation, accounting for the effects of water salinity on evaporation rates.

## Key Features

- **Combined methodology**: Integrates Abdelrady et al. (2016) water heat flux with Fisher et al. (2023) evaporation framework
- **Faithful implementation**: Exact reproduction of Abdelrady et al. (2016) equations and coefficients for water heat flux
- **Remote sensing optimized**: Follows Fisher et al. (2023) adaptations for satellite-based evaporation estimation
- **Multi-source data integration**: Combines satellite remote sensing data with meteorological inputs
- **Salinity correction**: Implements Turk (1970) salinity reduction factor as specified in original methodology
- **Automated data retrieval**: Integrates with GEOS-5 FP and NASADEM for meteorological and topographic data
- **Flexible input handling**: Supports both raster and array data formats
- **Water masking**: Automatically identifies water bodies using NASADEM surface water body extent

## Scientific Background and Methodology

This package is a faithful Python implementation combining the **Abdelrady et al. (2016) water heat flux methodology** with the **Fisher et al. (2023) remote sensing evaporation approach**. Abdelrady et al. developed the equilibrium temperature model for water heat flux calculation, while Fisher et al. adapted and integrated this with the Priestley-Taylor equation for complete evaporation estimation from satellite data. The water heat flux equations, coefficients, and computational steps follow the original Abdelrady et al. (2016) publication exactly, while the overall evaporation framework follows Fisher et al. (2023).

### Theoretical Foundation

The surface energy balance for water bodies follows the fundamental equation:

$$R_n = LE + H + W \quad \text{(Eq. 1, Abdelrady et al., 2016)}$$

Where:
- $R_n$ = Net radiation ($\text{W}\,\text{m}^{-2}$) - total energy available at the water surface
- $LE$ = Latent heat flux ($\text{W}\,\text{m}^{-2}$) - energy used for evaporation
- $H$ = Sensible heat flux ($\text{W}\,\text{m}^{-2}$) - energy transferred to the atmosphere via convection
- $W$ = Water heat flux ($\text{W}\,\text{m}^{-2}$) - energy stored in or released from the water body

### Water Heat Flux Calculation (Equilibrium Temperature Model)

The water heat flux is calculated using the equilibrium temperature model (ETM) as developed by **Abdelrady et al. (2016), Equations 8-13** and integrated into the complete evaporation framework by **Fisher et al. (2023)**. This approach, originally developed by Edinger et al. (1968) and adapted for remote sensing applications by Abdelrady et al., recognizes that there exists a theoretical equilibrium temperature where net heat exchange equals zero. Fisher et al. demonstrated how to combine this water heat flux calculation with Priestley-Taylor evapotranspiration for complete energy balance estimation. The implementation follows the exact formulations from both papers.

#### Step 1: Temperature Difference Calculation

$$T_n = 0.5 \times (WST - T_d) \quad \text{(Eq. 8, Abdelrady et al., 2016)}$$

Where:
- $T_n$ = Temperature difference parameter ($\text{°C}$)
- $WST$ = Water surface temperature ($\text{°C}$) - measured from thermal infrared satellite data
- $T_d$ = Dew point temperature ($\text{°C}$) - temperature at which air becomes saturated

**Scientific Reasoning**: The temperature difference between water surface and dew point drives evaporation. The factor of 0.5 represents an empirical relationship that accounts for the non-linear response of evaporation to temperature gradients.

#### Step 2: Evaporation Efficiency

$$\eta = 0.35 + 0.015 \times WST + 0.0012 \times T_n^2 \quad \text{(Eq. 9, Abdelrady et al., 2016)}$$

Where:
- $\eta$ = Evaporation efficiency (dimensionless)
- Where:
- $0.35$ = Baseline evaporation efficiency [dimensionless] - minimum efficiency under neutral conditions
- $0.015$ = Temperature dependence coefficient [$\text{°C}^{-1}$] - linear temperature sensitivity
- $0.0012$ = Non-linear temperature effect coefficient [$\text{°C}^{-2}$] - captures enhanced efficiency at high temperatures

**Scientific Reasoning**: Evaporation efficiency increases with water temperature and atmospheric stability. The baseline value represents minimum efficiency under neutral conditions, while the temperature terms account for enhanced molecular activity and vapor pressure differences at higher temperatures.

#### Step 3: Wind Speed Scaling

$$S = 3.3 \times u \quad \text{(Eq. 10, Abdelrady et al., 2016)}$$

Where:
- $S$ = Scaled wind speed factor [dimensionless] - wind enhancement of evaporation
- $u$ = Wind speed at reference height [$\text{m}\,\text{s}^{-1}$] - typically measured at 2-10m above surface
- $3.3$ = Empirical scaling coefficient [$\text{s}\,\text{m}^{-1}$] - derived from field measurements over water bodies

**Scientific Reasoning**: Wind enhances evaporation by removing saturated air from the water surface and bringing in drier air. The scaling factor converts wind speed into an evaporation enhancement parameter based on field measurements over water bodies.

#### Step 4: Thermal Exchange Coefficient

$$\beta = 4.5 + 0.05 \times WST + (\eta + 0.47) \times S \quad \text{(Eq. 11, Abdelrady et al., 2016)}$$

Where:
- $\beta$ = Thermal exchange coefficient [$\text{W}\,\text{m}^{-2}\,\text{°C}^{-1}$] - overall heat transfer efficiency
- $4.5$ = Base thermal conductance [$\text{W}\,\text{m}^{-2}\,\text{°C}^{-1}$] - minimum heat transfer under calm conditions
- $0.05$ = Temperature sensitivity coefficient [$\text{W}\,\text{m}^{-2}\,\text{°C}^{-2}$] - enhanced transfer at higher temperatures
- $0.47$ = Wind enhancement baseline [dimensionless] - minimum wind effect on thermal exchange

**Scientific Reasoning**: The thermal exchange coefficient represents the efficiency of heat transfer between water and atmosphere. It increases with temperature (enhanced molecular motion) and wind (improved mixing), with the evaporation efficiency providing additional enhancement.

#### Step 5: Equilibrium Temperature

$$T_e = T_d + \frac{SW_{net}}{\beta} \quad \text{(Eq. 12, Abdelrady et al., 2016)}$$

Where:
- $T_e$ = Equilibrium temperature ($\text{°C}$)
- $SW_{net}$ = Net shortwave radiation ($\text{W}\,\text{m}^{-2}$) - solar energy absorbed by water surface

**Scientific Reasoning**: The equilibrium temperature represents the theoretical water surface temperature at which net heat exchange would be zero. It increases with available solar energy and decreases with thermal exchange efficiency.

#### Step 6: Water Heat Flux

$$W = \beta \times (T_e - WST) \quad \text{(Eq. 13, Abdelrady et al., 2016)}$$

**Scientific Reasoning**: The water heat flux is proportional to the difference between equilibrium and actual water temperatures. Positive values indicate energy storage in the water body (warming), while negative values indicate energy release (cooling).

### Latent Heat Flux Calculation (Priestley-Taylor Method)

The latent heat flux is calculated using the Priestley-Taylor equation, which is well-suited for water surfaces where aerodynamic resistance is minimal:

$$LE = \alpha \times \frac{\Delta}{\Delta + \gamma} \times (R_n - W) \quad \text{(Priestley and Taylor, 1972)}$$

Where:
- $\alpha$ = Priestley-Taylor coefficient (1.26 for water surfaces)
- $\Delta$ = Slope of saturation vapor pressure curve ($\text{kPa}\,\text{°C}^{-1}$)
- $\gamma$ = Psychrometric constant ($0.066\,\text{kPa}\,\text{°C}^{-1}$)
- $\Delta/(\Delta + \gamma)$ = Energy partitioning factor

**Scientific Reasoning**: The Priestley-Taylor method assumes that evaporation from water surfaces is primarily energy-limited rather than aerodynamically limited. The coefficient α=1.26 accounts for the enhanced evaporation from free water surfaces compared to land surfaces.

### Net Radiation Calculation

Net radiation is calculated using the Verma et al. method when not provided directly:

$$R_n = SW_{in} \times (1 - \alpha_{surf}) + LW_{in} - LW_{out}$$

Where:
- $SW_{in}$ = Incoming shortwave radiation ($\text{W}\,\text{m}^{-2}$)
- $\alpha_{surf}$ = Surface albedo (dimensionless)
- $LW_{in}$ = Incoming longwave radiation ($\text{W}\,\text{m}^{-2}$)
- $LW_{out}$ = Outgoing longwave radiation ($\text{W}\,\text{m}^{-2}$)

### Salinity Correction

For saline water bodies, evaporation is reduced according to Turk (1970):

$$\sigma = 1.025 - 0.0246 \times \exp(0.00879 \times S) \quad \text{(Eq. 19, Abdelrady et al., 2016)}$$

Where:
- $\sigma$ = Salinity reduction factor (dimensionless)
- $S$ = Water salinity ($\text{g}\,\text{L}^{-1}$)

**Scientific Reasoning**: Dissolved salts reduce vapor pressure according to Raoult's law, thereby decreasing evaporation rates. The exponential relationship captures the non-linear effect of increasing salinity concentrations.

### Key References

1. **Abdelrady, A.; Timmermans, J.; Vekerdy, Z.; Salama, M.S.** Surface Energy Balance of Fresh and Saline Waters: AquaSEBS. *Remote Sens.* 2016, 8, 583. https://doi.org/10.3390/rs8070583

2. **Fisher, J.B.; Dohlen, M.B.; Halverson, G.H.; Collison, J.W.; Hook, S.J.; Hulley, G.C.** Remotely sensed terrestrial open water evaporation. *Sci. Rep.* 2023, 13, 8217. https://doi.org/10.1038/s41598-023-34921-2

3. **Edinger, J.E.; Duttweiler, D.W.; Geyer, J.C.** The Response of Water Temperatures to Meteorological Conditions. *Water Resour. Res.* 1968, 4, 1137–1143.

4. **Priestley, C.H.B.; Taylor, R.J.** On the Assessment of Surface Heat Flux and Evaporation Using Large-Scale Parameters. *Mon. Weather Rev.* 1972, 100, 81–92.

5. **Turk, L.J.** Evaporation of Brine: A field study on the Bonneville Salt Flats, Utah. *Water Resour. Res.* 1970, 6, 1209–1215.

## Installation

### From PyPI (Recommended)

```bash
pip install AquaSEBS
```

### From Source

```bash
git clone https://github.com/JPL-Evapotranspiration-Algorithms/AquaSEBS.git
cd AquaSEBS
pip install -e .[dev]
```

### Dependencies

AquaSEBS requires Python 3.10+ and depends on several specialized packages:

- `numpy` - Numerical computations
- `rasters` - Raster data handling
- `GEOS5FP` - GEOS-5 FP meteorological data access
- `NASADEM` - NASA DEM and surface water data
- `priestley-taylor` - Priestley-Taylor evapotranspiration calculations
- `ECOv002-granules` - ECOSTRESS data processing
- Additional scientific computing libraries

## Quick Start

### Basic Usage

```python
import numpy as np
from datetime import datetime
from AquaSEBS import AquaSEBS
from rasters import RasterGeometry

# Define study area geometry
geometry = RasterGeometry.from_bounds(
    left=-120.0, bottom=35.0, right=-119.0, top=36.0,
    pixel_size=0.01  # ~1km resolution
)

# Specify observation time
time_UTC = datetime(2023, 7, 15, 18, 0)  # Landsat overpass time

# Water surface temperature (required input)
WST_C = your_water_surface_temperature_data  # [°C] Celsius

# Run AquaSEBS model
results = AquaSEBS(
    WST_C=WST_C,
    geometry=geometry, 
    time_UTC=time_UTC
)

# Access results
latent_heat = results["LE_Wm2"]  # W⋅m⁻²
water_heat_flux = results["W_Wm2"]  # W⋅m⁻²
```

### Advanced Usage with Custom Inputs

```python
# Provide additional meteorological inputs for better accuracy
results = AquaSEBS(
    WST_C=water_surface_temperature,     # [°C] Water surface temperature
    Ta_C=air_temperature,                # [°C] Air temperature at 2m height
    RH=relative_humidity,                # [0-1] Relative humidity fraction
    windspeed_mps=wind_speed,            # [m/s] Wind speed at reference height
    albedo=surface_albedo,               # [0-1] Surface reflectance fraction
    emissivity=surface_emissivity,       # [0-1] Surface thermal emissivity
    geometry=geometry,
    time_UTC=time_UTC,
    water=water_mask,                    # [boolean] Water body mask
    mask_non_water_pixels=True
)
```

### Water Heat Flux Calculation

```python
from AquaSEBS import water_heat_flux

# Calculate water heat flux component
whf_results = water_heat_flux(
    WST_C=water_surface_temperature,     # [°C] Water surface temperature
    Ta_C=air_temperature,                # [°C] Air temperature  
    Td_C=dew_point_temperature,          # [°C] Dew point temperature
    windspeed_mps=wind_speed,            # [m/s] Wind speed
    SWnet=net_shortwave_radiation,       # [W/m²] Net shortwave radiation
    geometry=geometry,
    time_UTC=time_UTC
)

water_heat_flux_Wm2 = whf_results["W_Wm2"]  # [W/m²] Water heat flux output
```

## Model Components

### Energy Balance Equation

AquaSEBS implements the surface energy balance equation:

$$R_n = LE + H + W$$

Where:
- $R_n$ = Net radiation ($\text{W}\,\text{m}^{-2}$)
- $LE$ = Latent heat flux ($\text{W}\,\text{m}^{-2}$) - **calculated using Priestley-Taylor**
- $H$ = Sensible heat flux ($\text{W}\,\text{m}^{-2}$) - *derived as residual*
- $W$ = Water heat flux ($\text{W}\,\text{m}^{-2}$) - **calculated using equilibrium temperature model**

### Water Heat Flux Model

The water heat flux is calculated using the equilibrium temperature model:

$$W = \beta (T_e - WST)$$

Where:
- $\beta$ = Thermal exchange coefficient ($\text{W}\,\text{m}^{-2}\,\text{°C}^{-1}$)
- $T_e$ = Equilibrium temperature ($\text{°C}$)
- $WST$ = Water surface temperature ($\text{°C}$)

### Salinity Correction

For saline water bodies, evaporation is reduced according to:

$$E_s = \sigma \cdot E_{fresh}$$

Where $\sigma$ is the salinity reduction factor based on water salinity concentration.

## Data Requirements

### Required Inputs
- **Water Surface Temperature (WST_C)** [$\text{°C}$]: From thermal infrared satellite data (e.g., Landsat, MODIS, ECOSTRESS)
  - Typical range: 0-50°C for natural water bodies
  - Accuracy requirement: ±0.5°C for reliable evaporation estimates

### Optional Inputs (automatically retrieved if not provided)
- **Air Temperature (Ta_C)** [$\text{°C}$]: From GEOS-5 FP meteorological data
  - Used for psychrometric calculations and dew point estimation
- **Relative Humidity (RH)** [dimensionless, 0-1]: From GEOS-5 FP
  - Converted internally to dew point temperature for ETM calculations
- **Wind Speed (windspeed_mps)** [$\text{m}\,\text{s}^{-1}$]: From GEOS-5 FP
  - Reference height: 2m above surface
  - Enhanced evaporation at speeds >3 m/s
- **Surface Albedo** [dimensionless, 0-1]: From GEOS-5 FP
  - Typical water values: 0.05-0.15 depending on solar angle and conditions
- **Incoming Solar Radiation (SWin)** [$\text{W}\,\text{m}^{-2}$]: From GEOS-5 FP
  - Used to calculate net shortwave radiation with albedo
- **Water Mask** [boolean]: From NASADEM Surface Water Body extent
  - Identifies water pixels for focused calculations

## Validation and Accuracy

AquaSEBS has been validated against:
- Eddy covariance measurements over Lake IJsselmeer (Netherlands)
- Field measurements from Lake Tana (Ethiopia) and Lake Victoria (Africa)
- ECMWF ERA-Interim reanalysis data

**Typical accuracies:**
- **Latent heat flux** [$\text{W}\,\text{m}^{-2}$]: 4-5% relative RMSE for freshwater lakes
  - Absolute accuracy: ±10-25 W/m² for typical evaporation rates of 200-500 W/m²
- **Water heat flux** [$\text{W}\,\text{m}^{-2}$]: 6-9% relative RMSE  
  - Most sensitive to water surface temperature accuracy (±0.5°C requirement)
- **Salinity effects**: Up to 27% evaporation reduction for hypersaline water (>200 g/L)
  - Minimal effect (<1%) for freshwater and brackish water (<20 g/L)

## Examples and Notebooks

The `notebooks/` directory contains Jupyter notebooks demonstrating:

- `Water Heat Flux.ipynb` - Water heat flux calculations and validation
- `Water Masking.ipynb` - Water body identification and masking
- `Water Surface Latent Heat Flux.ipynb` - Complete evaporation estimation workflow

## Command Line Interface

Build and test the package using the provided Makefile:

```bash
# Install in development mode
make install

# Run tests  
make test

# Build distribution
make build

# Clean build artifacts
make clean
```

## API Reference

### Main Functions

#### `AquaSEBS()`
Main function for complete energy balance calculation.

**Parameters:**
- `WST_C`: Water surface temperature [$\text{°C}$] - from thermal infrared satellite data
- `geometry`: RasterGeometry object defining study area [spatial coordinates]
- `time_UTC`: datetime object for observation time [UTC timestamp]
- `Ta_C`: Air temperature [$\text{°C}$] - optional, auto-retrieved from GEOS-5 FP if not provided
- `RH`: Relative humidity [dimensionless, 0-1] - optional, auto-retrieved from GEOS-5 FP
- `windspeed_mps`: Wind speed [$\text{m}\,\text{s}^{-1}$] - optional, auto-retrieved from GEOS-5 FP
- `albedo`: Surface albedo [dimensionless, 0-1] - optional, auto-retrieved from GEOS-5 FP
- `emissivity`: Surface emissivity [dimensionless, 0-1] - optional, required for net radiation calculation
- `Td_C`: Dew point temperature [$\text{°C}$] - optional, calculated from Ta_C and RH if not provided
- `Rn_Wm2`: Net radiation [$\text{W}\,\text{m}^{-2}$] - optional, calculated using Verma method if not provided
- `SWnet`: Net shortwave radiation [$\text{W}\,\text{m}^{-2}$] - optional, calculated from incoming SW and albedo
- `water`: Water body mask [boolean array] - optional, auto-retrieved from NASADEM if not provided
- Additional parameters for model customization

**Returns:**
Dictionary containing instantaneous energy balance components and derived products:
- `LE_Wm2`: Latent heat flux [$\text{W}\,\text{m}^{-2}$] - energy used for evaporation
- `W_Wm2`: Water heat flux [$\text{W}\,\text{m}^{-2}$] - energy stored in water body
- `Rn_Wm2`: Net radiation [$\text{W}\,\text{m}^{-2}$] - total available energy
- `epsilon`: Psychrometric parameter [dimensionless] - energy partitioning factor
- `beta`: Thermal exchange coefficient [$\text{W}\,\text{m}^{-2}\,\text{°C}^{-1}$] - heat transfer efficiency
- `Te`: Equilibrium temperature [$\text{°C}$] - theoretical zero net heat exchange temperature
- `Tn`: Temperature difference parameter [$\text{°C}$] - driving force for evaporation
- `eta`: Evaporation efficiency [dimensionless] - atmospheric stability factor
- Additional intermediate variables from sub-calculations

#### `water_heat_flux()`
Calculate water heat flux using equilibrium temperature model.

**Parameters:**
- `WST_C`: Water surface temperature [$\text{°C}$] - required input
- `Ta_C`: Air temperature [$\text{°C}$] - optional, auto-retrieved from GEOS-5 FP
- `Td_C`: Dew point temperature [$\text{°C}$] - optional, calculated from Ta_C and RH
- `windspeed_mps`: Wind speed [$\text{m}\,\text{s}^{-1}$] - optional, auto-retrieved from GEOS-5 FP
- `SWnet`: Net shortwave radiation [$\text{W}\,\text{m}^{-2}$] - optional, calculated from SWin and albedo
- Other parameters similar to `AquaSEBS()` function

**Returns:**
Dictionary with water heat flux and intermediate variables:
- `W_Wm2`: Water heat flux [$\text{W}\,\text{m}^{-2}$] - main output
- `beta`: Thermal exchange coefficient [$\text{W}\,\text{m}^{-2}\,\text{°C}^{-1}$]
- `Te`: Equilibrium temperature [$\text{°C}$]
- `Tn`: Temperature difference [$\text{°C}$]
- `eta`: Evaporation efficiency [dimensionless]
- `S`: Scaled wind speed factor [dimensionless]
- All input variables passed through for reference

## Contributing

We welcome contributions! Please see our contributing guidelines and submit pull requests to the main repository.

### Development Setup

```bash
# Clone repository
git clone https://github.com/JPL-Evapotranspiration-Algorithms/AquaSEBS.git
cd AquaSEBS

# Create development environment
mamba create -n AquaSEBS -c conda-forge python=3.10
mamba activate AquaSEBS

# Install in development mode
pip install -e .[dev]

# Run tests
pytest
```

## Authors and Attribution

**Authors:**
- **Gregory H. Halverson** - NASA Jet Propulsion Laboratory (gregory.h.halverson@jpl.nasa.gov)
- **Joshua B. Fisher** - Chapman University (jbfisher@chapman.edu)

**Original AquaSEBS methodology:**
- Ahmed Abdelrady, Joris Timmermans, Zoltán Vekerdy, Mhd. Suhyb Salama

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Acknowledgments

This research was supported by:
- NASA Jet Propulsion Laboratory
- Chapman University  
- European Space Agency (ESA) Alcantara project
- University of Twente (ITC)

## Citation

If you use AquaSEBS in your research, please cite:

```bibtex
@article{abdelrady2016aquasebs,
  title={Surface Energy Balance of Fresh and Saline Waters: AquaSEBS},
  author={Abdelrady, Ahmed and Timmermans, Joris and Vekerdy, Zolt{\'a}n and Salama, Mhd Suhyb},
  journal={Remote Sensing},
  volume={8},
  number={7},
  pages={583},
  year={2016},
  publisher={MDPI},
  doi={10.3390/rs8070583}
}

@article{fisher2023remotely,
  title={Remotely sensed terrestrial open water evaporation},
  author={Fisher, Joshua B and Dohlen, Mary B and Halverson, Gregory H and Collison, Jared W and Hook, Simon J and Hulley, Glynn C},
  journal={Scientific Reports},
  volume={13},
  number={1},
  pages={8217},
  year={2023},
  publisher={Nature Publishing Group},
  doi={10.1038/s41598-023-34921-2}
}
```

## Links

- **Homepage**: https://github.com/JPL-Evapotranspiration-Algorithms/AquaSEBS
- **PyPI**: https://pypi.org/project/AquaSEBS/
- **Issues**: https://github.com/JPL-Evapotranspiration-Algorithms/AquaSEBS/issues
