"""Script for formatting USGS finite fault data into a CSV file readable by GeoClaw's dtopotools module"""
def get_csv(url, param_fname, csv_fname):
    import clawpack.clawutil.data
    import os    
    try:
        CLAW = os.environ['CLAW']
    except:
        raise Exception("*** Must first set CLAW enviornment variable")
    scratch_dir = os.path.join(CLAW, 'geoclaw', 'scratch')
    clawpack.clawutil.data.get_remote_file(url, output_dir=scratch_dir, file_name=param_fname, verbose=True)
    
    import pandas as pd
    df = pd.read_csv(os.path.join(scratch_dir,param_fname), skiprows=9, delim_whitespace=True)
    df.columns = ['latitude', 'longitude', 'depth', 'slip', 'rake', 'strike', 'dip', 'rupture_time', 'rise_time', 'fall_time', 'mo']
    # length/width can be automated, but for convenience, they're manually written here
    df['length'] = 12.00
    df['width'] = 8.80
    # rigidity = (moment seismicity) / (slip * area)
    # cm * km * km = 10^4 m^3
    df['mu'] = df['mo'] / (10**4 * df['length'] * df['width'] * df['slip']) 
    df.drop(['fall_time', 'mo'], axis=1, inplace=True)
    df.to_csv(csv_fname, index=False)