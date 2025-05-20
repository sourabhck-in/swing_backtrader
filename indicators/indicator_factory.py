class IndicatorFactory:
    """
    Factory for creating and managing indicators

    Provides centralized creation and registration of indicators,
    allowing for flexible instantiation and calculation.
    """

    def __init__(self):
        """Initialize the factory with an empty indicator registry"""
        self._indicators = {}

    def register_indicator(self, indicator_type, indicator_class):
        """
        Register an indicator type with its implementation class

        Parameters:
        -----------
        indicator_type : str
            Identifier for the indicator type
        indicator_class : class
            Class implementing the indicator
        """
        self._indicators[indicator_type] = indicator_class

    def create_indicator(self, indicator_type, **params):
        """
        Create an indicator instance based on type and parameters

        Parameters:
        -----------
        indicator_type : str
            Type of indicator to create
        **params : dict
            Parameters for the indicator

        Returns:
        --------
        BaseIndicator
            Instance of the requested indicator

        Raises:
        -------
        ValueError
            If indicator_type is not registered
        """
        if indicator_type not in self._indicators:
            raise ValueError(f"Unknown indicator type: {indicator_type}")

        indicator_class = self._indicators[indicator_type]
        return indicator_class(**params)

    def calculate_indicator(self, indicator_type, data, **params):
        """
        Create and calculate an indicator in one step

        Parameters:
        -----------
        indicator_type : str
            Type of indicator to calculate
        data : dict
            Price/volume data for calculation
        **params : dict
            Parameters for the indicator

        Returns:
        --------
        list or dict
            Calculated indicator values
        """
        indicator = self.create_indicator(indicator_type, **params)
        return indicator.calculate(data)
