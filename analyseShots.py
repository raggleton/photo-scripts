#!/usr/bin/env python

"""
Do rough analysis of photos taken
"""


import os
import subprocess
from glob import glob
import numpy as np
import pandas as pd
from copy import deepcopy
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
sns.set(style="ticks", color_codes=True)


def get_file_info(filename, attributes):
    attr_str = " ".join(["-name %s" % att for att in attributes])
    data = subprocess.check_output("mdls %s '%s'" % (attr_str, filename), shell=True).decode().splitlines()
    data_dict = {}
    for entry in data:
        parts = entry.split("=")
        data_dict[parts[0].strip()] = parts[-1].strip()
    return data_dict


INFO_KEYS = {
    "aperture": "kMDItemFNumber",
    "focal_length": "kMDItemFocalLength",
    "exposure_time": "kMDItemExposureTimeSeconds",
    "iso": "kMDItemISOSpeed",
    "exposure_mode": "kMDItemExposureProgram"
}


MODE_MAP = {
    1: "M",
    2: "Auto",
    3: "AP",
    4: "TP",
}


def pairgrid_heatmap(x, y, **kws):
    # cmap = sns.light_palette(kws.pop("color"), as_cmap=True)
    new_kws = kws
    new_kws.pop('color')
    # plt.hist2d(x, y, cmap='Reds', cmin=1, **new_kws)
    plt.hist2d(x, y, cmap='viridis', cmin=1, **new_kws)


if __name__ == "__main__":
    cache_file = "shots.csv"
    df = None
    
    if os.path.isfile(cache_file):
        print("Reading from cache file")
        df = pd.read_csv(cache_file)

    start_dir = "../*"
    entries = glob(os.path.join(start_dir, "*.ARW"))

    if (os.path.isfile(cache_file) and (len(df.index) != len(entries))) or not os.path.isfile(cache_file):
        print("Rebuilding dataframe")
        print("Iterating over %d files" % len(entries))
        data = []
        for filename in entries:
            this_info = get_file_info(filename, list(INFO_KEYS.values()))
            this_dict = {k: float(this_info[v]) for k, v in INFO_KEYS.items()}
            this_dict["filename"] = filename
            this_dict["exposure_mode"] = MODE_MAP[int(this_dict["exposure_mode"])]
            data.append(this_dict)

        df = pd.DataFrame(data)
    
        with open(cache_file, 'w') as f:
            df.to_csv(f, index=False)

    # log certain columns + rename them for the plot
    rename_cols = ['exposure_time', 'iso']
    for cname in rename_cols:
        df[cname] = df[cname].apply(np.log10)
        df.rename(columns={cname: cname + " [log10]"}, inplace=True)
    
    # categorise exposure modes
    df.exposure_mode = df.exposure_mode.astype('category')

    print (df.describe())

    # Make plots
    interesting_vars = list(df.columns.values)[:]
    interesting_vars.remove('filename')
    interesting_vars.remove('exposure_mode')
    # g = sns.pairplot(df, hue='exposure_mode', vars=interesting_vars, markers='x', 
    #                  diag_kws={'bins': 20, 'histtype': 'step', 'linewidth': 2},
    #                  plot_kws={'s': 3})
    g = sns.PairGrid(df, vars=interesting_vars, hue='exposure_mode')
    g = g.map_diag(plt.hist, bins=20, histtype='step', linewidth=2)
    g = g.map_lower(pairgrid_heatmap, bins=20)
    g = g.map_upper(plt.scatter, marker='x', s=3)
    g = g.add_legend()
    plt.savefig("pairplot.pdf")
