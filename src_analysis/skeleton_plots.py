from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib as mpl
import matplotlib.patches as mpatches
import plotly.graph_objects as go

# Colormap
def red_black_blue_cmap():
    """ Custom colormap for red-black-blue """
    colors = [(1, 0, 0),  # Red (start)
              (0, 0, 0),  # Black (middle)
              (0, 0, 1)]   # Blue (end)

    # create list of colors [0 1] from red-black-blue there are 256 colors in between equidistantly
    return mcolors.LinearSegmentedColormap.from_list("RedBlackBlue", colors, N=256)


def plot_skeleton_nodes(sk_swc):
    """ Basic skeleton plot"""
    # Plot all nodes
    plt.figure(figsize=(8, 8))
    plt.scatter(sk_swc['x'], sk_swc['y'], color='gray', label='All Nodes', s=0.1)

    # Plot soma
    mask_soma = sk_swc["parent"] == -1
    soma_df = sk_swc[mask_soma]
    plt.scatter(soma_df["x"], soma_df["y"], color="red", s=10, label="Soma")

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('All nodes')
    plt.legend()

    plt.axis('equal')  # Ensures equal aspect ratio
    plt.gca().invert_yaxis()
    plt.autoscale()  # Autoscale axes based on data
    plt.show()


def plot_skeleton_nodes_with_edges(sk_swc):
    """Plot skeleton nodes with connecting lines based on parent-child relationships."""
    plt.figure(figsize=(8, 8))

    # Draw lines (edges) between nodes and their parents
    for _, row in sk_swc.iterrows():
        parent_id = row['parent']
        if parent_id != -1:
            parent_row = sk_swc[sk_swc['id'] == parent_id]
            if not parent_row.empty:
                x_values = [row['x'], parent_row.iloc[0]['x']]
                y_values = [row['y'], parent_row.iloc[0]['y']]
                plt.plot(x_values, y_values, color='black', linewidth=0.3)

    # Plot all nodes
    plt.scatter(sk_swc['x'], sk_swc['y'], color='black', s=0.1, label='All Nodes')

    # Plot soma
    soma_df = sk_swc[sk_swc["parent"] == -1]
    plt.scatter(soma_df["x"], soma_df["y"], color="red", s=10, label="Soma")

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Skeleton with Connections')
    plt.legend()
    plt.axis('equal')
    plt.gca().invert_yaxis()
    plt.autoscale()
    plt.show()


def plot_skeleton_by_levels_2d(sk_swc_dend_levels, level_type, level_you_want, root_id, dir_name, save):
    fig, ax = plt.subplots(figsize=(8, 8))

    # --- filter levels ---
    if isinstance(level_you_want, int):
        filtered_df = sk_swc_dend_levels[
            (sk_swc_dend_levels[level_type] <= level_you_want) &
            (sk_swc_dend_levels[level_type] >= 1)
        ]
    elif level_you_want == "max":
        filtered_df = sk_swc_dend_levels[sk_swc_dend_levels[level_type] >= 1]
    else:
        raise ValueError("check level_you_want; must be integer or 'max'.")

    # guard: empty
    if filtered_df.empty:
        # still save an empty diagnostic figure if requested
        ax.set_title(f"{root_id} - empty after filtering ({level_type})")
        if save:
            outdir = Path(dir_name)
            outdir.mkdir(parents=True, exist_ok=True)
            plt.savefig(outdir / f"{root_id}_{level_type}_2d.png", dpi=300, format="png")
            plt.close(fig)
            return
        plt.show()
        plt.close(fig)
        return

    # --- positions + levels ---
    x = filtered_df["x"].to_numpy()
    y = filtered_df["y"].to_numpy()
    levels = filtered_df[level_type].to_numpy()

    # colormap
    cmap = plt.get_cmap("jet")
    norm = plt.Normalize(levels.min(), levels.max())
    colors = cmap(norm(levels))

    ax.scatter(x, y, c=colors, s=5)

    # soma (if present)
    soma_df = sk_swc_dend_levels[sk_swc_dend_levels["id"] == 1]
    if not soma_df.empty:
        ax.scatter(
            soma_df["x"].to_numpy(),
            soma_df["y"].to_numpy(),
            color="red", marker="^", s=100, edgecolors="black"
        )

    # legend
    unique_levels = np.unique(levels)
    legend_patches = [mpatches.Patch(color=cmap(norm(lv)), label=f"Level {lv}") for lv in unique_levels]
    ax.legend(handles=legend_patches, title="Node Levels", loc="upper right")

    # axes
    ax.invert_yaxis()
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title(f"Skeleton dendrites colored by {level_type}")

    # save/show
    if save:
        outdir = Path(dir_name)
        outdir.mkdir(parents=True, exist_ok=True)
        plt.savefig(outdir / f"{root_id}_{level_type}_2d.png", dpi=300, format="png")
        plt.close(fig)
        return

    plt.show()
    plt.close(fig)



def plot_skeleton_by_levels_3d(sk_swc_dend_levels, level_type, level_you_want):
    """
    Plot skeleton dendrties in 3d by centrifugal level

    Parameters:
        sk_swc_dend_levels: DataFrame containing SWC file filtered by dendrites and added centrifugal level.
        level_type: select between "cf_level" or "br_level"
        level_you_want: specify how many levels you want to visualize.
                        - If an integer, only visualize levels ≤ level_you_want
                        - If "max", visualize all levels
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Filter levels
    if isinstance(level_you_want, int):
        filtered_df = sk_swc_dend_levels[(sk_swc_dend_levels[level_type] <= level_you_want) &
                                         (sk_swc_dend_levels[level_type] >= 1)]
    elif level_you_want == "max":
        filtered_df = sk_swc_dend_levels[sk_swc_dend_levels[level_type] >= 1]  # Exclude levels < 1
    else:
        raise ValueError("check level_you_want; must be integer or 'max'.")

    # Extract node positions
    x = filtered_df['x'].values
    y = filtered_df['y'].values
    z = filtered_df['z'].values
    levels = filtered_df[level_type].values

    # Create colormap for levels
    cmap = plt.get_cmap('jet')
    norm = plt.Normalize(min(levels), max(levels))
    colors = [cmap(norm(level)) for level in levels]

    # Plot nodes
    ax.scatter(x, z, y, c=colors, s=5)

    # Plot soma (assuming ID 1 is the soma)
    soma_df = sk_swc_dend_levels[sk_swc_dend_levels['id'] == 1]  # Use 1 instead of 0 if needed
    if not soma_df.empty:
        soma_x = soma_df['x'].values
        soma_y = soma_df['y'].values
        soma_z = soma_df['z'].values
        ax.scatter(soma_x, soma_z, soma_y, color='red', s=100, edgecolors='black', label="Soma")

        # Create legend
    unique_levels = np.unique(levels)
    legend_patches = [mpatches.Patch(color=cmap(norm(level)), label=f"Level {level}") for level in unique_levels]

    # Add legend to the plot
    ax.legend(handles=legend_patches, title="Node Levels", loc="upper right")

    # Autoscale the axes
    ax.set_box_aspect([1, 1, 1])  # Keep equal aspect ratio

    # Axis labels
    ax.set_xlabel("X")
    ax.set_ylabel("Z")
    ax.set_zlabel("Y")
    ax.set_title(f"3D Skeleton Structure")

    plt.show()


def plot_skeleton_by_levels_3d_interactive(sk_swc_dend_levels, level_type, level_you_want, root_id, dir_name, save):
    """
    Plot skeleton dendrites in 3D interactively by centrifugal level using Plotly.

    Parameters:
        sk_swc_dend_levels: DataFrame containing SWC file filtered by dendrites and added centrifugal level
        level_type: select between "cf_level" or "br_level"
        level_you_want: specify how many levels you want to visualize.
                        - If an integer, only visualize levels ≤ level_you_want
                        - If "max", visualize all levels
    """
    # Filter levels
    # if isinstance(level_you_want, int):
    #     filtered_df = sk_swc_dend_levels[(sk_swc_dend_levels[level_type] <= level_you_want) &
    #                                      (sk_swc_dend_levels[level_type] >= 1)]
    # elif level_you_want == "max":
    #     filtered_df = sk_swc_dend_levels[sk_swc_dend_levels[level_type] >= 1]  # Exclude levels < 1
    # else:
    #     raise ValueError("check level_you_want; must be integer or 'max'.")

    if isinstance(level_you_want, int):
        filtered_df = sk_swc_dend_levels[(sk_swc_dend_levels[level_type] <= level_you_want)]
    elif level_you_want == "max":
        filtered_df = sk_swc_dend_levels  # Exclude levels < 1
    else:
        raise ValueError("check level_you_want; must be integer or 'max'.")

    # Extract node positions
    x = filtered_df['x'].values
    y = filtered_df['y'].values
    z = filtered_df['z'].values
    levels = filtered_df[level_type].values

    # Create colormap for levels
    cmap = mpl.colormaps['jet']
    norm = plt.Normalize(min(levels), max(levels))
    colors = [cmap(norm(level)) for level in levels]
    colors_hex = [f'rgba({int(c[0] * 255)},{int(c[1] * 255)},{int(c[2] * 255)},1)' for c in colors]

    # Create scatter plot
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(size=3, color=colors_hex),
        text=[f'Level {lvl}' for lvl in levels],
        hoverinfo='text'
    ))

    # Draw edges (connect parent-child)
    edge_x = []
    edge_y = []
    edge_z = []

    for _, row in filtered_df.iterrows():
        parent_id = row['parent']
        if parent_id != -1:
            parent_row = filtered_df[filtered_df['id'] == parent_id]
            if not parent_row.empty:
                px, py, pz = parent_row[['x', 'y', 'z']].values[0]
                edge_x.extend([px, row['x'], None])
                edge_y.extend([py, row['y'], None])
                edge_z.extend([pz, row['z'], None])

    fig.add_trace(go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(color='gray', width=1),
        hoverinfo='none'
    ))

    # Add Soma as a Sphere
    soma = filtered_df[filtered_df['id'] == 0]
    if not soma.empty:
        soma_x, soma_y, soma_z = soma[['x', 'y', 'z']].values[0]
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 10)
        sphere_x = 5 * np.outer(np.cos(u), np.sin(v)) + soma_x
        sphere_y = 5 * np.outer(np.sin(u), np.sin(v)) + soma_y
        sphere_z = 5 * np.outer(np.ones(np.size(u)), np.cos(v)) + soma_z

        fig.add_trace(go.Surface(
            x=sphere_x, y=sphere_y, z=sphere_z,
            colorscale=[[0, 'black'], [1, 'black']],
            showscale=False,
            opacity=0.4
        ))

    # Set layout
    fig.update_layout(
        title="3D Skeleton Structure (Interactive)",
        width=1200,
        height=900,
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z'
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )

    # Save file if you want
    if save == True:
        fname = f"{root_id}_{level_type}_3d_interactive.png"
        fig.write_image(dir_name + fname)

    # Full screen option, only when we're looking for single neuron
    if not save:
        from IPython.display import display
        display(fig)


from pathlib import Path
import matplotlib.pyplot as plt

def plot_skeleton_distance_2d(sk_swc_dend_levels_all, root_id, dir_name, save, view="xy"):
    """Plot skeleton nodes by distance_from_soma (expects compute_skeleton_tree_distances already run)."""

    fig, ax = plt.subplots(figsize=(8, 6))

    # guard: empty
    if sk_swc_dend_levels_all is None or sk_swc_dend_levels_all.empty:
        ax.set_title(f"{root_id} - empty distance plot")
        if save:
            outdir = Path(dir_name)
            outdir.mkdir(parents=True, exist_ok=True)
            plt.savefig(outdir / f"{root_id}_soma_dist_{view}_2d.png", dpi=300, format="png")
            plt.close(fig)
            return
        plt.show()
        plt.close(fig)
        return

    # Normalize distance for colormap scaling
    dist = sk_swc_dend_levels_all["distance_from_soma"]
    norm = plt.Normalize(dist.min(), dist.max())

    # Select coordinate pairs based on chosen view
    if view == "xy":
        x, y = sk_swc_dend_levels_all["x"], sk_swc_dend_levels_all["y"]
        xlabel, ylabel = "X", "Y"
    elif view == "xz":
        x, y = sk_swc_dend_levels_all["x"], sk_swc_dend_levels_all["z"]
        xlabel, ylabel = "X", "Z"
    elif view == "yz":
        x, y = sk_swc_dend_levels_all["y"], sk_swc_dend_levels_all["z"]
        xlabel, ylabel = "Y", "Z"
    else:
        raise ValueError("Invalid view. Choose 'xy', 'xz', or 'yz'.")

    # Plot skeleton
    cmap_jet = plt.get_cmap("jet")
    scatter = ax.scatter(x, y, c=dist, norm=norm, cmap=cmap_jet, s=5)

    # Labels and title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(f"Skeleton distance plot ({view})")

    # Aspect + axes
    ax.invert_yaxis()
    ax.set_aspect("equal", adjustable="box")

    # Colorbar
    plt.colorbar(scatter, ax=ax)

    # Save or show
    if save:
        outdir = Path(dir_name)
        outdir.mkdir(parents=True, exist_ok=True)
        out_path = outdir / f"{root_id}_soma_dist_{view}_2d.png"
        plt.savefig(out_path, dpi=300, format="png")
        plt.close(fig)
        return

    plt.show()
    plt.close(fig)


def plot_skeleton_distance_3d(sk_swc_dend_levels_all):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Normalize distance for colormap scaling
    norm = plt.Normalize(sk_swc_dend_levels_all["distance_from_soma"].min(),
                         sk_swc_dend_levels_all["distance_from_soma"].max())

    # Use the custom colormap
    rkb_cmap = red_black_blue_cmap()
    x = sk_swc_dend_levels_all["x"]
    y = sk_swc_dend_levels_all["y"]
    z = sk_swc_dend_levels_all["z"]

    # Plot
    # scatter = ax.scatter(x, z, y, c =  sk_swc_dend_levels_all["distance_from_soma"], norm = norm,
    #                      cmap = rkb_cmap, s = 5)
    cmap_jet = plt.get_cmap("jet")
    scatter = ax.scatter(x, z, y, c=sk_swc_dend_levels_all["distance_from_soma"], norm=norm,
                         cmap=cmap_jet, s=5)

    # Plot soma
    soma_df = sk_swc_dend_levels_all[sk_swc_dend_levels_all['id'] == 0]  # Use 1 instead of 0 if needed
    if not soma_df.empty:
        soma_x = soma_df['x'].values
        soma_y = soma_df['y'].values
        soma_z = soma_df['z'].values
        ax.scatter(soma_x, soma_z, soma_y, color='red', s=100, edgecolors='black', label="Soma")

        # Autoscale the axes
    ax.set_box_aspect([1, 1, 1])  # Keep equal aspect ratio

    # Axis labels
    ax.set_xlabel("X")
    ax.set_ylabel("Z")
    ax.set_zlabel("Y")
    ax.set_title(f"3D Skeleton Structure")

    plt.show()


def plot_skeleton_distance_3d_interactive(sk_swc_dend_levels_all, root_id, dir_name, save):
    """
    Plot skeleton nodes in 3D interactively, colored by their distance from the soma.

    Parameters:
        sk_swc_dend_levels_all: DataFrame containing skeleton data with "x", "y", "z", and "distance_from_soma".
    """

    # Extract node positions
    x = sk_swc_dend_levels_all["x"].values
    y = sk_swc_dend_levels_all["y"].values
    z = sk_swc_dend_levels_all["z"].values
    distances = sk_swc_dend_levels_all["distance_from_soma"].values

    # Unapproved pretty colorscale
    # cmap = plt.get_cmap("coolwarm")  # Choose a colormap
    # norm = plt.Normalize(min(distances), max(distances))
    # colors = [cmap(norm(d)) for d in distances]
    # colors_hex = [f'rgba({int(c[0]*255)},{int(c[1]*255)},{int(c[2]*255)},1)' for c in colors]

    # Ugly but practical colorscale
    # cmap = red_black_blue_cmap()
    cmap = plt.get_cmap("jet")
    norm = plt.Normalize(min(distances), max(distances))
    colors_hex = [cmap(norm(d)) for d in distances]

    # Create scatter plot
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(size=3, color=colors_hex),
        text=[f'Distance: {d:.2f}' for d in distances],
        hoverinfo='text'
    ))

    # Draw edges (connect parent-child if such information exists)
    edge_x, edge_y, edge_z = [], [], []

    for _, row in sk_swc_dend_levels_all.iterrows():
        parent_id = row.get('parent', -1)  # Default to -1 if no parent column
        if parent_id != -1:
            parent_row = sk_swc_dend_levels_all[sk_swc_dend_levels_all['id'] == parent_id]
            if not parent_row.empty:
                px, py, pz = parent_row[['x', 'y', 'z']].values[0]
                edge_x.extend([px, row['x'], None])
                edge_y.extend([py, row['y'], None])
                edge_z.extend([pz, row['z'], None])

    fig.add_trace(go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(color='gray', width=1),
        hoverinfo='none'
    ))

    # Add Soma as a Sphere
    soma = sk_swc_dend_levels_all[sk_swc_dend_levels_all['id'] == 0]
    if not soma.empty:
        soma_x, soma_y, soma_z = soma[['x', 'y', 'z']].values[0]
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 10)
        sphere_x = 5 * np.outer(np.cos(u), np.sin(v)) + soma_x
        sphere_y = 5 * np.outer(np.sin(u), np.sin(v)) + soma_y
        sphere_z = 5 * np.outer(np.ones(np.size(u)), np.cos(v)) + soma_z

        fig.add_trace(go.Surface(
            x=sphere_x, y=sphere_y, z=sphere_z,
            colorscale=[[0, 'black'], [1, 'black']],
            showscale=False,
            opacity=0.4
        ))

    # Set layout
    fig.update_layout(
        title="3D Skeleton Distance Plot (Interactive)",
        width=1200,
        height=900,
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z'
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )

    # Save file if you want
    if save == True:
        fname = f"{root_id}_soma_dist_3d_interactive.png"
        fig.write_image(dir_name + fname)

    #Full screen option
    from IPython.display import display
    display(fig)

# Mesh plot (optional; check details)
""" 
    Check mesh file (you can do neuroglancer actually)
"""

def downsample_mesh(vertices, faces, sample_fraction=0.1):
    """ Downsamples the number of vertices and faces by selecting a fraction of them. """
    num_vertices = len(vertices)
    sampled_indices = np.random.choice(num_vertices, int(sample_fraction * num_vertices), replace=False)
    sampled_vertices = vertices[sampled_indices]

    # Filter faces to keep only those with all vertices in sampled set
    face_mask = np.all(np.isin(faces, sampled_indices), axis=1)
    sampled_faces = faces[face_mask]

    return sampled_vertices, sampled_faces


def plot_3d_mesh(mesh, sample_fraction=0.1):
    # Extract vertices and faces
    vertices, faces = downsample_mesh(mesh.vertices, mesh.faces, sample_fraction)

    # Get x, y, z coordinates of sampled vertices
    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]

    # Create a 3D mesh object
    mesh_plot = go.Mesh3d(
        x=x, y=y, z=z,
        i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
        color='lightblue', opacity=0.5
    )

    # Create scatter plot for vertices (optional)
    scatter_plot = go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(size=2, color='grey', opacity=0.5),
        name='Vertices'
    )

    # Create figure and add traces
    # fig = go.Figure(data=[mesh_plot, scatter_plot])
    fig = go.Figure(data=scatter_plot)
    fig.update_layout(
        scene=dict(
            xaxis_title='X (nm)',
            yaxis_title='Y (nm)',
            zaxis_title='Z (nm)'
        ),
        title='3D Mesh Visualization (Downsampled)',
        autosize=True,
        width=1400,
        height=1000,
    )

    fig.show()

# Example usage with a sample mesh file
# mesh = trimesh.load_mesh("path_to_your_mesh.obj")
# plot_3d_mesh(mesh, sample_fraction=0.1)