# microns-synapse-analysis

This repository provides practical notebooks for accessing the MICrONS([Microns Cubic Milimeter data](https://www.microns-explorer.org/cortical-mm3)), and running synapse based analyses that connect anatomy (dendritic skeletons, synapse coordinates, branch structure) with function (neural/synaptic functional properties).

## What can you do with this?
1. Querying synapses for selected neurons \
2. Preprocessing and annotating synapses by dendritic location/compartment \
3. Quantifying how neuron's functional variables such as preferred orientation and direction change across dendritic structure and distance from soma

## Repository Map
### Start here
- [`00_quickstart.ipynb`](notebooks/00_quickstart.ipynb) — Minimal end-to-end run to verify setup and MICrONS data access.


### Data access
- [`01_data_query_and_save.ipynb`](notebooks/01_data_query_and_save.ipynb) — Query MICrONS tables and save local, analysis-ready files.

### Preprocessing + synapse→dendrite assignment
- [`02_preprocessing_assignment.ipynb`](notebooks/02_preprocessing_assignment.ipynb) — Clean tables and assign synapses to dendritic structure (e.g., distance-to-soma / compartments).

### Analyses
- [`03_analysis_basal_apical.ipynb`](notebooks/03_analysis_basal_apical.ipynb) — Core dendrite-centric analyses (basal vs apical comparisons).
- [`03_Stat_input_vs_distance.ipynb`](notebooks/03_Stat_input_vs_distance.ipynb) — Summary statistics vs distance-to-soma (binned trends).
- [`04_inhibitory_analysis.ipynb`](notebooks/04_inhibitory_analysis.ipynb) — Variant of the pipeline focused on inhibitory neurons.

### 3D visualization
- [`05_Skeleton_Mesh_Tutorial.ipynb`](notebooks/05_Skeleton_Mesh_Tutorial.ipynb) — Skeleton/mesh rendering tutorial for qualitative inspection.
- [`06_3D_video_skeletons.ipynb`](notebooks/06_3D_video_skeletons.ipynb) — Export rotating 3D videos from skeletons/meshes.
