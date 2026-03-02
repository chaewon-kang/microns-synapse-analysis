import numpy as np
import pandas as pd
import math
from collections import deque
import caveclient

"""
    Here are collection of functions to calculate cluster dendrites
"""


# Set caveclient (used in synapse assignment)
# client = caveclient.CAVEclient('minnie65_public')
# client.version = 1300

# Distances
def soma_euclidean_dist(sk_swc):
    """
        Calculate Euclidean distance to soma
        This is to validate neurons; not really used for preprocessing
    """

    # Ensure sk_swc is a copy to avoid SettingWithCopyWarning
    sk_swc = sk_swc.copy()

    # Find the soma node
    soma_node = sk_swc[sk_swc['parent'] == -1]
    soma_coords = soma_node[['x', 'y', 'z']].values[0]

    # Vectorized Euclidean distance
    coords = sk_swc[['x', 'y', 'z']].values
    sk_swc['eucli_dist'] = np.linalg.norm(coords - soma_coords, axis=1)

    return sk_swc

def distance_bt_skeleton_nodes(sk_swc_dend_levels):
    """
        Check distances between each skeletons
    """
    distance_bt_nodes = []

    for index, row in sk_swc_dend_levels.iterrows():
        if row["parent"] == -1:
            continue

        parent_row = sk_swc_dend_levels[sk_swc_dend_levels['id'] == row['parent']]

        child_pos = np.array([row['x'], row['y'], row['z']])
        parent_pos = np.array([parent_row['x'], parent_row['y'], parent_row['z']])

        node_distance = (row['x'] - parent_row['x']) ** 2 + (row['y'] - parent_row['y']) ** 2 + (
                    row['z'] - parent_row['z']) ** 2
        node_distance = math.sqrt(node_distance)

        # node_distance = euclidean_distance(child_pos, parent_pos)

        # print(f"child location = {child_pos}")
        # print(f"parent location = {parent_pos}")
        # print(f"distance = {node_distance}")

        distance_bt_nodes.append(node_distance)

    return distance_bt_nodes

def compute_skeleton_tree_distances(sk_swc_dend_levels):
    """
        This calculates the tree distance to the soma.
        Note that this is different from Euclidean distance from soma
    """
    distance_from_soma = {}

    # Find soma node (root)
    soma_row = sk_swc_dend_levels[sk_swc_dend_levels["parent"] == -1]
    soma_id = int(soma_row["id"].values[0])  # Get soma ID (always 0)
    distance_from_soma[soma_id] = 0  # distance from soma to itself is 0

    # Convert dataframe to dictionary for faster lookup
    sk_dict = sk_swc_dend_levels.set_index("id").to_dict(orient="index")

    # Traverse the skeleton tree
    for node_id, node_data in sk_dict.items():
        parent_id = int(node_data["parent"])

        # Skip soma: Jumps back to for loop
        if parent_id == -1:
            continue

        # By putting None, we skip if parent_id does not exist. It will otherwise crash
        parent_data = sk_dict.get(parent_id, None)
        if parent_data is None:
            continue  # In case of missing parent, skip

        # Compute Euclidean distance between node and its parent
        node_pos = np.array([node_data["x"], node_data["y"], node_data["z"]])
        parent_pos = np.array([parent_data["x"], parent_data["y"], parent_data["z"]])
        segment_distance = (node_data["x"] - parent_data["x"]) ** 2 + (node_data["y"] - parent_data["y"]) ** 2 + (
                    node_data["z"] - parent_data["z"]) ** 2
        segment_distance = math.sqrt(segment_distance)

        # Accumulate distance from soma
        distance_from_soma[node_id] = distance_from_soma[parent_id] + segment_distance

    # Convert results to DataFrame
    sk_swc_dend_levels["distance_from_soma"] = sk_swc_dend_levels["id"].map(distance_from_soma)

    return sk_swc_dend_levels


def node_count_dendrite_branches(sk_swc, soma_parent_val=-1):
    """
    Count nodes in each dendritic branch (subtree) that stems from the soma's
    first-generation children.

    Parameters
    ----------
    sk_swc : pd.DataFrame
        Must contain columns ['id', 'parent'].
    soma_parent_val : int, default -1
        Value used in 'parent' column to mark the soma row.

    Returns
    -------
    dict
        {<first_level_child_id>: <number_of_nodes_in_that_branch>}
        (soma itself is not counted in any branch)
    """
    
    # Ensure sk_swc is a copy to avoid SettingWithCopyWarning
    sk = sk_swc.copy()

    # Find the soma node
    soma_node = sk_swc[sk_swc['parent'] == -1]
    soma_id = soma_node.iloc[0]['id']

    # Build parent -> [children] map once (big speedup)
    children_map = sk.groupby("parent")["id"].apply(list).to_dict()

    # First-generation children of the soma
    first_level_nodes = children_map.get(soma_id, [])


    # BFS traversal
    # store dendrite branches and their node counts
    dendrite_branches = {}
    visited_global = set()


    for root in first_level_nodes:
        stack = [root]
        nodes_in_branch = set()

        while stack:
            current = stack.pop()
            if current in nodes_in_branch:
                continue
            nodes_in_branch.add(current)

            # Push children
            for child in children_map.get(current, []):
                stack.append(child)

        dendrite_branches[root] = len(nodes_in_branch)
        # Track global visitation to catch cross-links (shouldn't happen in trees)
        overlap = visited_global.intersection(nodes_in_branch)
        if overlap:
            # Not raising; just flag in-case you want to inspect later.
            # print(f"Warning: branch {root} overlaps with previously visited nodes: {overlap}")
            pass
        visited_global.update(nodes_in_branch)

    return dendrite_branches

# Ordering
def assign_branch_order(sk_swc):
    """
       Dendritic ordering
       Assign different level everytime it bifurcates
       Breadth-First-Search traverse algorithm
       Usage:
           sk_swc_dend_levels = assign_branch_order(sk_swc_dend)
    """
    # Identify root node
    root_node = sk_swc.loc[sk_swc['parent'] == -1, 'id'].values[0]

    # Create dict to store node levels
    node_levels = {root_node: 0}

    # Group by parents and list child within {parent_id: [list_of_children]}
    child_map = sk_swc.groupby("parent")["id"].apply(list).to_dict()

    # Traverse nodes breadth-first: [node, level]
    queue = [(root_node, 0)]

    while queue:
        node_id, level = queue.pop(0)  # FIFO queue for BFS

        # If the node has children, check how many
        children = child_map.get(node_id,
                                 [])  # Finds node_id key (parent) and brings their values (children), otherwise return []

        if len(children) > 1:
            new_level = level + 1
        else:
            new_level = level

        for child in children:
            node_levels[child] = new_level  # Update children's levels: [node, node_level]
            queue.append((child, new_level))  # Update queue same way:   [node, node_level]

    # Convert dict to DataFrame and merge with original
    levels_df = pd.DataFrame(list(node_levels.items()), columns=['id', 'branch_order'])
    sk_swc = sk_swc.merge(levels_df, on='id')

    return sk_swc
def assign_dendrites(sk_swc):
    """
        Cluster dendrites in each dendrite clusters (too circular? it is)
        input: sk_swc_dend_levels
    """

    # Find the soma node (parent = -1)
    soma_node = sk_swc[sk_swc['parent'] == -1]
    soma_id = soma_node.iloc[0]['id']

    # Find all direct children of soma
    soma_children = sk_swc[sk_swc['parent'] == soma_id]['id'].tolist()

    # Initialize clusters mapping
    node_to_cluster = {}

    # Assign each child of soma to its own cluster and traverse descendants
    for idx, root in enumerate(soma_children):
        cluster_id = idx + 1  # Assign unique cluster ids
        queue = deque([root])
        node_to_cluster[root] = cluster_id  # Assign root node to its own cluster

        while queue:
            node = queue.popleft()

            # Get children of the current node
            children = sk_swc[sk_swc['parent'] == node]['id'].tolist()
            for child in children:
                queue.append(child)
                node_to_cluster[child] = cluster_id  # Assign to same cluster as root

    # Assign the cluster ID in a new column
    sk_swc['dendrites'] = sk_swc['id'].map(node_to_cluster).fillna(-1).astype(int)

    return sk_swc
def assign_segments(sk_swc):
    """
    Assign segment IDs to dendrites within each branch order (br_level).
    - Segment numbering restarts at 1 for each br_level.
    - A new segment is assigned at every divergence.
    """

    # Ensure 'br_level' and 'parent' columns exist
    if 'dendrites' not in sk_swc.columns or 'parent' not in sk_swc.columns:
        raise ValueError("Error: 'dendrites' or 'parent' column not found in dataset.")

    # Initialize mappings
    node_to_segment = {}  # Map each node to a segment

    # Process each branch level separately
    for br_level in sk_swc['dendrites'].unique():
        subset = sk_swc[sk_swc['dendrites'] == br_level].copy()
        segment_counter = 1  # Restart segment numbering for each br_level

        # Find all root nodes within this branch level (nodes without parents in this level)
        root_nodes = subset[~subset['parent'].isin(subset['id'])]['id'].tolist()

        # Process each root separately
        for root in root_nodes:
            queue = deque([(root, segment_counter)])  # Start each root with a new segment
            segment_counter += 1

            while queue:
                node, segment_id = queue.popleft()
                node_to_segment[node] = segment_id

                # Get children of the current node
                children = subset[subset['parent'] == node]['id'].tolist()

                if len(children) == 1:
                    # Continue same segment if there's only one child
                    queue.append((children[0], segment_id))
                elif len(children) > 1:
                    # If divergence occurs, create new segments for each child
                    for child in children:
                        queue.append((child, segment_counter))
                        segment_counter += 1

    # Assign segment IDs to the dataframe
    sk_swc['segments'] = sk_swc['id'].map(node_to_segment).fillna(-1).astype(int)

    return sk_swc

# Synapse assignment
def synapse_to_skeleton_gpu(pre_synapse_df: pd.DataFrame, sk_swc_dend: pd.DataFrame):
    import cupy as xp

    """
        Assign synapses to skeleton nodes using CuPy.
        Returns:
            assignments_df['synapse_id', 'size', 'pre_pt_root_id', 'node_id', 'distance']
    """

    # ===== Extract coordinates and convert =====
    # Synapse's coordinates
    syn_xyz = xp.asarray(pre_synapse_df["post_pt_position"].apply(xp.asarray).to_list(), dtype = xp.float32)
    syn_xyz *= xp.asarray([4, 4, 40], dtype=xp.float32) / 1000.0

    # Skeleton node's coordinates
    node_xyz = xp.asarray(sk_swc_dend[["x", "y", "z"]].to_numpy(dtype=xp.float32))

    # == Compute nearest node for each synapse==
    diff   = syn_xyz[:, None, :] - node_xyz[None, :, :]       # (N,M,3)
    dist2  = xp.sum(diff ** 2, axis=-1)                       # (N,M)
    idx    = xp.argmin(dist2, axis=1)                         # (N,)
    dists  = xp.sqrt(dist2[xp.arange(len(idx)), idx])         # (N,)

    # Bring results back to host RAM
    idx, dists = map(xp.asnumpy, (idx, dists))

    # == Move results back to host if needed and build DataFrame ==

    assignments_df = pd.DataFrame({
        "synapse_id"     : pre_synapse_df["id"].values,
        "size"           : pre_synapse_df["size"].values,
        "pre_pt_root_id" : pre_synapse_df["pre_pt_root_id"].values,
        "node_id"        : sk_swc_dend["id"].values[idx],
        "distance"       : dists,
    })

    return assignments_df

def post_synapse_to_skeleton_gpu(post_synapse_df: pd.DataFrame, sk_swc_dend: pd.DataFrame):
    """
        Assign synapses to skeleton nodes using CuPy.
        Returns:
            assignments_df['synapse_id', 'size', 'post_pt_root_id', 'node_id', 'distance']
    """
    import cupy as xp

    # === Extract coordinates and convert ===
    # Synapse's coordinates
    syn_xyz = xp.asarray(post_synapse_df["pre_pt_position"].apply(xp.asarray).to_list(), dtype=xp.float32)
    syn_xyz *= xp.asarray([4, 4, 40], dtype=xp.float32) / 1000.0

    # Skeleton node's coordinates
    node_xyz = xp.asarray(sk_swc_dend[["x", "y", "z"]].to_numpy(dtype=xp.float32))

    # === Compute nearest node for each synapse ===
    diff   = syn_xyz[:, None, :] - node_xyz[None, :, :]       # (N,M,3)
    dist2  = xp.sum(diff ** 2, axis=-1)                       # (N,M)
    idx    = xp.argmin(dist2, axis=1)                         # (N,)
    dists  = xp.sqrt(dist2[xp.arange(len(idx)), idx])         # (N,)

    # Bring results back to host RAM
    idx, dists = map(xp.asnumpy, (idx, dists))

    # === Move results back to host if needed and build DataFrame ===
    assignments_df = pd.DataFrame({
        "synapse_id"      : post_synapse_df["id"].values,
        "size"            : post_synapse_df["size"].values,
        "post_pt_root_id" : post_synapse_df["post_pt_root_id"].values,
        "node_id"         : sk_swc_dend["id"].values[idx],
        "distance"        : dists,

    })

    return assignments_df





