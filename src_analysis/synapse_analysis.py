import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib as mpl
import matplotlib.patches as mpatches
import plotly.graph_objects as go
import pandas as pd

"""
    Here are collection of methods helps with functional analysis of dendritic synapses
"""

def circular_mean(angles):
    """
        Compute average of two angles of orientation data [0 pi]
        problem is that since it's preferred orientation, we need to double the angle,
        otherwise the average of 0 and pi is going to be 2/pi (very wrong, since we assume 0 and pi as same direction)

        Doubles the angles to treat them as directions on a full circle,
        then halves the result to project back to [0, π).

    """
    angles = np.asarray(angles)
    doubled = 2 * angles
    mean_angle = np.arctan2(np.mean(np.sin(doubled)), np.mean(np.cos(doubled))) / 2

    return mean_angle % np.pi  # ensures it lands in [0, π)


def plot_skeleton_nodes_dist(sk_swc, distance_threshold):
    plt.figure(figsize=(8, 8))

    # Mask for nodes within threshold
    mask_near_soma = sk_swc['distance_from_soma'] < distance_threshold
    mask_far_soma = ~mask_near_soma  # Nodes outside threshold

    # Plot nodes based on distance
    plt.scatter(sk_swc.loc[mask_far_soma, 'x'], sk_swc.loc[mask_far_soma, 'y'],
                color='royalblue', label='All Nodes (Far)', s=1.5)
    plt.scatter(sk_swc.loc[mask_near_soma, 'x'], sk_swc.loc[mask_near_soma, 'y'],
                color='dimgray', label=f'Nodes < {distance_threshold}', s=0.1)

    # Plot soma
    mask_soma = sk_swc["parent"] == -1
    soma_df = sk_swc[mask_soma]
    plt.scatter(soma_df["x"], soma_df["y"], color="red", marker="^", s=100, label="Soma")

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(f'Soma <{distance_threshold} Nodes')
    # plt.legend()

    plt.axis('equal')
    plt.autoscale()
    plt.show()



def assignment_df_mapping(assignment_df, sk_dend_levels, mapping_component, new_column_name):
    """
    Map a skeleton column (mapping_component) onto assignment_df using node_id -> id.
    """

    needed_ass = {"node_id"}
    needed_skel = {"id", mapping_component}

    if not needed_ass.issubset(assignment_df.columns):
        raise ValueError(f"assignment_df missing columns: {needed_ass - set(assignment_df.columns)}")
    if not needed_skel.issubset(sk_dend_levels.columns):
        raise ValueError(f"sk_dend_levels missing columns: {needed_skel - set(sk_dend_levels.columns)}")

    # dtype alignment to avoid all-NaN mapping due to int/str mismatch
    ass_ids = pd.to_numeric(assignment_df["node_id"], errors="coerce").astype("Int64")
    sk_ids  = pd.to_numeric(sk_dend_levels["id"], errors="coerce").astype("Int64")

    map_component = sk_dend_levels.assign(id=sk_ids).set_index("id")[mapping_component]
    assignment_df[new_column_name] = ass_ids.map(map_component)

    return assignment_df
