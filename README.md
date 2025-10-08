# AquaSEBS

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/AquaSEBS.svg)](https://badge.fury.io/py/AquaSEBS)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**AquaSEBS** is a Python package for estimating water surface evaporation and energy balance components over freshwater and saline water bodies using satellite remote sensing data and meteorological inputs. The package implements the AquaSEBS (Aquatic Surface Energy Balance System) model, which adapts the Surface Energy Balance System (SEBS) for application over water surfaces.

## Overview

AquaSEBS provides physics-based estimation of:
- **Latent heat flux (evaporation)**
- **Water heat flux**
- **Net radiation components**

The model accounts for the effects of water salinity on evaporation rates and uses the equilibrium temperature model (ETM) approach for accurate water heat flux calculations.

## Key Features

- **Multi-source data integration**: Combines satellite remote sensing data with meteorological inputs
- **Salinity correction**: Accounts for reduced evaporation rates in saline water bodies
- **Automated data retrieval**: Integrates with GEOS-5 FP and NASADEM for meteorological and topographic data
- **Flexible input handling**: Supports both raster and array data formats
- **Physics-based approach**: Implements validated energy balance equations from peer-reviewed research
- **Water masking**: Automatically identifies water bodies using NASADEM surface water body extent

## Scientific Background

AquaSEBS is based on the methodology described in:

> Abdelrady, A.; Timmermans, J.; Vekerdy, Z.; Salama, M.S. **Surface Energy Balance of Fresh and Saline Waters: AquaSEBS**. *Remote Sens.* 2016, 8, 583. https://doi.org/10.3390/rs8070583

The implementation has been validated and further developed in:

> Fisher, J.B.; Dohlen, M.B.; Halverson, G.H.; Collison, J.W.; Hook, S.J.; Hulley, G.C. **Remotely sensed terrestrial open water evaporation**. *Sci. Rep.* 2023, 13, 8217. https://doi.org/10.1038/s41598-023-34921-2

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
WST_C = your_water_surface_temperature_data  # In Celsius

# Run AquaSEBS model
results = AquaSEBS(
    WST_C=WST_C,
    geometry=geometry, 
    time_UTC=time_UTC
)

# Access results
latent_heat = results["LE_Wm2"]  # W/m²
water_heat_flux = results["W_Wm2"]  # W/m²
```

### Advanced Usage with Custom Inputs

```python
# Provide additional meteorological inputs for better accuracy
results = AquaSEBS(
    WST_C=water_surface_temperature,
    Ta_C=air_temperature,
    RH=relative_humidity,
    windspeed_mps=wind_speed,
    albedo=surface_albedo,
    emissivity=surface_emissivity,
    geometry=geometry,
    time_UTC=time_UTC,
    water=water_mask,  # Optional water body mask
    mask_non_water_pixels=True
)
```

### Water Heat Flux Calculation

```python
from AquaSEBS import water_heat_flux

# Calculate water heat flux component
whf_results = water_heat_flux(
    WST_C=water_surface_temperature,
    Ta_C=air_temperature,  
    Td_C=dew_point_temperature,
    windspeed_mps=wind_speed,
    SWnet=net_shortwave_radiation,
    geometry=geometry,
    time_UTC=time_UTC
)

water_heat_flux_Wm2 = whf_results["W_Wm2"]
```

## Model Components

### Energy Balance Equation

AquaSEBS implements the surface energy balance equation:

$$R_n = LE + H + W$$

Where:
- $R_n$ = Net radiation (W/m²)
- $LE$ = Latent heat flux (W/m²) - **calculated using Priestley-Taylor**
- $H$ = Sensible heat flux (W/m²) - *derived as residual*
- $W$ = Water heat flux (W/m²) - **calculated using equilibrium temperature model**

### Water Heat Flux Model

The water heat flux is calculated using the equilibrium temperature model:

$$W = \beta (T_e - WST)$$

Where:
- $\beta$ = Thermal exchange coefficient
- $T_e$ = Equilibrium temperature  
- $WST$ = Water surface temperature

### Salinity Correction

For saline water bodies, evaporation is reduced according to:

$$E_s = \sigma \cdot E_{fresh}$$

Where $\sigma$ is the salinity reduction factor based on water salinity concentration.

## Data Requirements

### Required Inputs
- **Water Surface Temperature (WST_C)**: From thermal infrared satellite data (e.g., Landsat, MODIS, ECOSTRESS)

### Optional Inputs (automatically retrieved if not provided)
- **Air Temperature (Ta_C)**: From GEOS-5 FP
- **Relative Humidity (RH)**: From GEOS-5 FP  
- **Wind Speed (windspeed_mps)**: From GEOS-5 FP
- **Surface Albedo**: From GEOS-5 FP
- **Incoming Solar Radiation**: From GEOS-5 FP
- **Water Mask**: From NASADEM Surface Water Body extent

## Validation and Accuracy

AquaSEBS has been validated against:
- Eddy covariance measurements over Lake IJsselmeer (Netherlands)
- Field measurements from Lake Tana (Ethiopia) and Lake Victoria (Africa)
- ECMWF ERA-Interim reanalysis data

**Typical accuracies:**
- Latent heat flux: 4-5% relative RMSE for freshwater lakes
- Water heat flux: 6-9% relative RMSE
- Salinity effects: Up to 27% evaporation reduction for hypersaline water

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
- `WST_C`: Water surface temperature in Celsius
- `geometry`: RasterGeometry object defining study area
- `time_UTC`: datetime object for observation time
- `Ta_C`: Air temperature (optional)
- `RH`: Relative humidity (optional) 
- `windspeed_mps`: Wind speed in m/s (optional)
- `albedo`: Surface albedo (optional)
- `emissivity`: Surface emissivity (optional)
- Additional parameters for customization

**Returns:**
Dictionary containing instantaneous energy balance components and derived products.

#### `water_heat_flux()`
Calculate water heat flux using equilibrium temperature model.

**Parameters:**
Similar to `AquaSEBS()` but focused on water heat flux calculation.

**Returns:**
Dictionary with water heat flux and intermediate variables.

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
- **Documentation**: [Coming soon]
- **PyPI**: https://pypi.org/project/AquaSEBS/
- **Issues**: https://github.com/JPL-Evapotranspiration-Algorithms/AquaSEBS/issues
