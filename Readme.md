# colony_blob_bleacher

Python code for automated high-throughput FRAP (HiT-FRAP) image acquisition 
and analysis, accompanying:

**Sheu-Gruttadauria et al. (2026)** "Nucleolar dynamics are determined by the 
ordered assembly of the ribosome." *Journal to be added upon acceptance.*  
DOI: [to be updated]

Original acquisition framework developed by Xiaowei Yan and Nico Stuurman.  
Analysis code developed by J. Sheu-Gruttadauria.

---

## Overview

HiT-FRAP automates fluorescence recovery after photobleaching (FRAP) across 
hundreds of cells per experiment. This repository contains:

- **`acquisition/`** — Pycro-Manager scripts for automated colony detection, 
  blob identification, and photobleaching at the microscope
- **`analysis/`** — Python scripts for FRAP curve extraction, normalization, 
  and parameter fitting (mobile fraction, recovery half-time)
- **`shared/`** — Shared utilities used across acquisition and analysis
- **`conda_env/`** — Conda environment files for reproducible setup
- **`test/`** — Test scripts and example data

---

## Requirements

- Python 3.8+
- [Pycro-Manager](https://pycro-manager.readthedocs.io/) (for acquisition)
- Conda (recommended for environment management)

Install dependencies:
```bash
conda env create -f conda_env/environment.yml
conda activate colony_blob_bleacher
```

---

## Usage

### Acquisition
Run from the `acquisition/` directory with an active Micro-Manager instance.  
See scripts in `acquisition/` for configuration parameters (magnification, 
bleach ROI size, number of colonies).

### Analysis
Input: TIFF image series from Micro-Manager  
Output: Per-cell FRAP curves, fitted mobile fraction and t½ values, 
summary tables and figures

---

## Citation

If you use this code, please cite:  
Sheu-Gruttadauria et al. (2026) DOI: [to be updated]

---

## License

MIT License. See [LICENSE](LICENSE) for details.  
Original code forked from [xwyan1230/colony_blob_bleacher](https://github.com/xwyan1230/colony_blob_bleacher).
