import unittest
import os
import numpy as np
from lcls_tools.common.image_processing.image_processing import ImageProcessor
from lcls_tools.common.image_processing.roi import RectangularROI

class TestImageCreator():
    def create_test_image(self, size: tuple, center: list, radius: int):
        ''' 
        make img that is a circle in the center of the image with known
        standard dev and mean. no imports, no calls to external or
        internal files.
         '''
        image = np.zeros(size)
        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                distance = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
                if distance < radius:
                    image[y, x] = 1
        return image


class ImageProcessingTest(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.center = [400,400]
        self.size = (800,800)
        self.widths= (300,300)
        self.radius = 50
        self.image_creator = TestImageCreator()
        self.image = self.image_creator.create_test_image(size = self.size, center=self.center,radius = self.radius)

    def test_process(self):
        image_processor = ImageProcessor()
        image = image_processor.process(self.image)
        assert isinstance(image,np.ndarray)
        #test that any use case returns an ndarray
        roi = RectangularROI(center =self.center,xwidth=self.widths[0], ywidth=self.widths[1])
        image_processor = ImageProcessor(roi=roi)
        image = image_processor.process(self.image)
        assert isinstance(image,np.ndarray)

    def test_subtract_background(self):
        background_image = self.image_creator.create_test_image(size = self.size, center=self.center,radius = self.radius)
        image_processor = ImageProcessor(background_image=background_image)
        # if subtraction works with two exactly identical arrays then all values will be zero
        image = image_processor.subtract_background(self.image)
        assert image.all() == np.zeros(self.size).all()
