#!/bin/bash

from thorlab_loader.builder import ThorlabBuilder

b = ThorlabBuilder(input_folder="/Users/tanmay/LenevoINFN/Work/UTokyo/InFile/beada_001/ChanA_001_001_001_001.tif")
arr, meta = b.build()

b.save_as_ome_tiff("output.ome.tiff")
