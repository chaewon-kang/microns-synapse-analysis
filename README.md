# microns-synapse-analysis

This repository provides practical notebooks for accessing the MICrONS([Microns Cubic Milimeter data](https://www.microns-explorer.org/cortical-mm3)), and running synapse based analyses that connect anatomy (dendritic skeletons, synapse coordinates, branch structure) with function (neural/synaptic functional properties).

## What can you do with this?
1. Querying synapses for selected neurons \
2. Preprocessing and annotating synapses by dendritic location/compartment \
3. Quantifying how neuron's functional variables such as preferred orientation and direction change across dendritic structure and distance from soma

## Repository Map
### Start here
[`00_quickstart.ipynb`](notebooks/00_quickstart.ipynb): Minimal end-to-end run to verify setup and MICrONS data access.
- **What it does:**
  - loads one example neuron and visualizes (1) skeleton morphology and (2) synapse locations onto the neuron in 2D plane (xy).
  - demonstrates dendritic labeling utilities (`branch_order`, `dendrites`, `segments`) and distance-to-soma coloring.
- **Output:** example plots below

<details>
<summary><b>00_quickstart example outputs (click to expand)</b></summary>
<br>

**(1) Postsynaptic neuron skeleton (2D projection).**  
Black: skeleton nodes. Red: soma.

<p align="center">
  <img src=>







- [`00_quickstart.ipynb`](notebooks/00_quickstart.ipynb) — Minimal end-to-end run to verify setup and MICrONS data access.
Here you can have a look at tables, synapses, and neuron's properties.
This quickstart demonstrates the visualization of synapses and skeletons on a 2D plane. Example 23 layer pyramidal neuron's synapse and skeleton examples are below.
Mind you that it seems synapses only captures dendrites because we can query either presynapse or postsynapses given a single post neuron, and we chose presyapses.
On the other hand, skeleton includes the entire structure of a neuron as you can see, you can see dendrites and axons.
[insert pic 1]
[insert pic 2]

Next, using a dendritic skeleton sorting algorithms (src/dendrites.py),  we can classify dendrite nodes into three different orders.
[insert pic 3]
[insert pic 4]
[insert pic 5]

Lastly, we can plot each skeleton's node and color them in regards to their distance to soma.
[insert pic 6]







## Under construction

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
