# 🌾 AgroForgeSIM Example Scenarios

This directory contains reproducible input datasets for testing, demonstrations, and CI validation of **AgroForgeSIM**.

---

## 📁 Files Overview

### `scenario_maize.yaml`
A complete YAML configuration describing a single maize field for simulation.  
It defines:
- Field metadata (ID, name, area, crop type)
- Management details (plant date, density, irrigation)
- Soil root-zone capacity
- Weather source reference (`weather_csv`)

Used in:
- `backend/cli.py simulate`
- API endpoint `/api/simulate`
- Integration and regression tests

**Schema alignment:** Matches engine models and CLI input specification.

---

### `weather_sample.csv`
Example **10-day** weather dataset used by the maize scenario.

**Columns:**
| Column  | Description                  | Unit         |
|---------|------------------------------|--------------|
| `date`  | Calendar date                | YYYY-MM-DD   |
| `tmin`  | Minimum daily temperature    | °C           |
| `tmax`  | Maximum daily temperature    | °C           |
| `rain`  | Daily rainfall               | mm/day       |
| `rad`   | Shortwave radiation sum      | MJ/m²/day    |
| `et0`   | Reference evapotranspiration | mm/day       |

This format is required by the engine’s `parse_weather_csv()` utility and is compatible with the `WeatherDay` model.

---

## 🚀 Quick Run (CLI)

Run the sample maize scenario directly:

```bash
# Activate your virtual environment first, if needed
python backend/cli.py simulate backend/examples/scenario_maize.yaml
