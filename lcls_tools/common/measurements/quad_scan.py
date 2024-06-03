from lcls_tools.common.devices.screen import Screen
from lcls_tools.common.image_processing.image_processing import ImageProcessor
from lcls_tools.common.data_analysis.fit.projection import ProjectionFit
from lcls_tools.common.measurements.measurement import Measurement
import numpy as np


class QuadScanMeasurement(Measurement):
    """
    ScreenBeamProfileMeasurement class that allows for background subtraction and roi cropping
    ------------------------
    Arguments:
    name: str (name of measurement default is beam_profile),
    device: 
    ------------------------
    Methods:
    single_measure: measures device and returns raw and processed image
    measure: does multiple measurements and has an option to fit the image profiles
    """

    name: str = "quad_scan"
    screen_measurement: ScreenBeamProfileMeasurement
    device: Magnet
    quadrupole_strengths: list 
    rmat_x: list
    rmat_y: list

    
    def measure(self) -> dict:
        results = []
        for val in self.quadrupole_strengths:
            self.device.bctrl = val
            res  = self.screen_measurement.measure()
            results.append(res)
            
        #TODO: data processing using emitOpt