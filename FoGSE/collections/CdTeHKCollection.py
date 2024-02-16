"""
CdTe collection to handle the read-in CdTe data.
"""

from copy import copy

import numpy as np
import matplotlib.pyplot as plt

class CdTeHKCollection:
    
    def __init__(self, parsed_data, old_data_time=0):
        # bring in the parsed data
        _, self.event_dataframe, _ = parsed_data
        
        # define all the strip sizes in CdTe detectors
        self.strip_bins, self.side_strip_bins, self.adc_bins = self.channel_bins()
        
        # for easy remapping of channels
        self.channel_map = self.remap_strip_dict()

        # dont include data more than a second older than the previous frames latest data
        self.new_entries = self.event_dataframe['ti']>=0#old_data_time
        self.latest_data_time = np.max(self.event_dataframe['ti'])
        # self.latest_data_time = np.max(self.event_dataframe['ti'][np.where(self.event_dataframe['unixtime']==self.latest_unixtime)])
        
        # filter the counts somehow, go for crude single strip right now
        # self.f_data = self.filter_counts(event_dataframe=self.event_dataframe)
        self.f_data = self.filter_counts_grades(event_dataframe=self.event_dataframe, grade_al="max_adc", grade_pt="max_adc")
        
        # get more physical information about detector geometry
        self.strip_width_edges = self.strip_widths()
        self.pixel_area = self.pixel_areas()