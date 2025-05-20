class BaseIndicator:
    """
    Base class for all indicators with common functionality

    This serves as the foundation for all indicator implementations,
    ensuring consistent interfaces and behavior.
    """

    def __init__(self, name, params=None):
        """
        Initialize indicator with name and parameters

        Parameters:
        -----------
        name : str
            Indicator name
        params : dict, optional
            Parameter dictionary for the indicator
        """
        self.name = name
        self.params = params or {}

    def calculate(self, data):
        """
        Calculate indicator values

        Parameters:
        -----------
        data : dict
            Price/volume data with keys like 'open', 'high', 'low', 'close', 'volume'

        Returns:
        --------
        list or dict
            Calculated indicator values
        """
        raise NotImplementedError("Subclasses must implement calculate()")

    def __str__(self):
        """String representation of the indicator with parameters"""
        param_str = ", ".join([f"{k}={v}" for k, v in self.params.items()])
        return f"{self.name}({param_str})"
