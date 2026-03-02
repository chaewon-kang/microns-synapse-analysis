from joblib import Parallel, delayed
from tqdm import tqdm
import pandas as pd
import os

# def process_neuron(neuron):
#     cell_type = "23P_V1/"
#     dir_pre_synapse = "/media/DATA1/CK/python_script/MicronsBinder_03/results/skeleton/pre_synapse_data/"
#     dir_swc_dend = "/media/DATA1/CK/python_script/MicronsBinder_03/results/skeleton/skeleton_swc_data/skeleton_swc_clustered/"
#     dir_save = "/media/DATA1/CK/python_script/MicronsBinder_03/results/skeleton/synapse_assignments/"
#
#     file_name_pre_synapse = f"{neuron}_pre_synapse_df.pkl"
#     pre_synapse_df = pd.read_pickle(os.path.join(dir_pre_synapse, cell_type, file_name_pre_synapse))
#
#     file_name_dend_levels = f"{neuron}_sk_swc_dend_levels_all.csv"
#     sk_swc_dend = pd.read_csv(os.path.join(dir_swc_dend, cell_type, file_name_dend_levels))
#
#     assignments_df = synapse_to_skeleton(pre_synapse_df, sk_swc_dend)
#
#     file_name_assignments_df = f"{neuron}_assignments_df.csv"
#     assignments_df.to_csv(os.path.join(dir_save, cell_type, file_name_assignments_df))
#     print(neuron)
#     print("Done done")

if __name__ == "__main__":
    pass
    # # Load your list however you were doing in notebook
    # import pickle
    # with open('/media/DATA1/CK/python_script/MicronsBinder_03/results/skeleton/filtered_23P_neurons.pkl', 'rb') as f:
    #     filtered_23P= pickle.load(f)
    #
    # list_uniq_root_id = filtered_23P.index.tolist()
    #
    # results = Parallel(n_jobs=29)(
    #     delayed(process_neuron)(neuron) for neuron in tqdm(list_uniq_root_id)
    # )
    #
    # # Optional: print or log results
    # for res in results:
    #     print(res)
