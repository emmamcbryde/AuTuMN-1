import numpy


def get_seasonal_forcing(
        period: float, shift: float, prop_amplitude: float, average_value: float
):
    """
    Factory function to get a trigonometric/sinusoidal function (using cosine) to represent seasonal forcing of
    transmission in a model.
    Note that the time unit is not specified (as elsewhere in the repository), so the period is not assumed.

    :param period: float
        Time to complete an entire cycle of forcing
    :param shift: float
        Time at which the peak value will be reached
    :param prop_amplitude: float
        Amplitude of the forcing function relative to the average value
        Note that the amplitude is HALF of the total variation in the function
    :param average_value: float
        Average value of the function, mid-way between peak and trough values
    :return:
        The seasonal forcing function
    """

    amplitude = prop_amplitude * average_value

    def seasonal_forcing(time):
        return \
            numpy.cos(
                (time - shift) * 2. * numpy.pi / period
            ) * \
            amplitude + \
            average_value

    return seasonal_forcing


if __name__ == "__main__":
    period, shift, amplitude, average = 365., 173., 0.5, 0.04
    x_values = numpy.linspace(0., period, 20)
    forcing_function = get_seasonal_forcing(period, shift, amplitude, average)
    for i in x_values:
        print(f"date: {i}, \t value: {forcing_function(i)}")
