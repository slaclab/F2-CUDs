from pydm.widgets.image import PyDMImageView
from numpy import flip

class InvertedPyDMImage(PyDMImageView):
    """
    subclass to flip iamge in X/Y - performance intensive :(
    """
    def __init__(self, im_ch, w_ch, parent=None, args=None):
        PyDMImageView.__init__(self, parent=parent, image_channel=im_ch, width_channel=w_ch)

    def process_image(self, image): return flip(image)