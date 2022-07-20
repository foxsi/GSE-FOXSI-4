import numpy as np

class AbstractDetector:
    def __init__(self):
        self.name = ""
        self.institution = ""
        self.response = None     # how should this be captured? response.energy.fit(adc_bin) etc?
        
        self.temperature = np.array([])
        pass

    def __hash__(self) -> int:
        pass

    def __iter__(self):
        pass

    def __eq__(self, __o: object) -> bool:
        pass

class AbstractStripDetector(AbstractDetector):
    def __init__(self):
        super().__init__()
        
        self.strips = None      # thinking variable pitch: how to store strip info?
        # another "Strip" class including per-strip response info etc?
        pass

class AbstractPixelatedDetector(AbstractDetector):
    def __init__(self):
        super().__init__()

        self.pixels = None
        pass

class CdTeDetector(AbstractStripDetector):
    def __init__(self):
        super().__init__()
        pass

class TimepixDetector(AbstractPixelatedDetector):
    def __init__(self):
        super().__init__()
        pass

class CMOSDetector(AbstractPixelatedDetector):
    def __init__(self):
        super().__init__()
        pass