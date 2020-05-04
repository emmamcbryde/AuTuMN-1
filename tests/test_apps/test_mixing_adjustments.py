from apps.covid_19.matrices import *


def test_plot_mixing_adjustments():

    # Victoria Baseline
    _mixing_params = {'other_locations_times': [72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
                                                90, 91, 92, 93],
                      'other_locations_values': [1.0, 0.951510855, 0.893323881, 0.815741249, 0.796345591, 0.670273814,
                                                 0.544202037, 0.51510855, 0.5054107210000001, 0.4763172339999999, 0.43752591799999996, 0.3502454570000001, 0.27266282500000005, 0.22417367999999993, 0.22417367999999993, 0.20477802199999995, 0.20477802199999995, 0.20477802199999995, 0.20477802199999995, 0.17568453500000003, 0.17568453500000003, 0.16598670599999998], 'work_times': [78.0, 79.0, 81.0, 82.0, 84.0, 85.0, 86.0, 87.0, 91.0, 92.0], 'work_values': [1.0, 0.95, 0.95, 0.9, 0.9, 0.7, 0.7, 0.5, 0.5, 0.25], 'school_times': [84.0, 85.0], 'school_values': [1.0, 0.0]}
    # Victoria Scenario 1
    _mixing_params = {'other_locations_times': [72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93], 'other_locations_values': [1.0, 0.95, 0.89, 0.81, 0.79, 0.66, 0.53, 0.5, 0.49, 0.45999999999999996, 0.41999999999999993, 0.33000000000000007, 0.25, 0.19999999999999996, 0.19999999999999996, 0.17999999999999994, 0.17999999999999994, 0.17999999999999994, 0.17999999999999994, 0.15000000000000002, 0.15000000000000002, 0.14], 'work_times': [78.0, 79.0, 81.0, 82.0, 84.0, 85.0, 86.0, 87.0, 91.0, 92.0], 'work_values': [1.0, 0.95, 0.95, 0.9, 0.9, 0.7, 0.7, 0.5, 0.5, 0.25], 'school_times': [84.0, 85.0, 121.0, 123.0], 'school_values': [1.0, 0.0, 0.0, 1.0]}

    # Victoria Scenarios 2 and 3
    _mixing_params = {'other_locations_times': [72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 121, 123], 'other_locations_values': [1.0, 0.95, 0.89, 0.81, 0.79, 0.66, 0.53, 0.5, 0.49, 0.45999999999999996, 0.41999999999999993, 0.33000000000000007, 0.25, 0.19999999999999996, 0.19999999999999996, 0.17999999999999994, 0.17999999999999994, 0.17999999999999994, 0.17999999999999994, 0.15000000000000002, 0.15000000000000002, 0.14, 0.14, 1.0], 'work_times': [78.0, 79.0, 81.0, 82.0, 84.0, 85.0, 86.0, 87.0, 91.0, 92.0, 121.0, 123.0], 'work_values': [1.0, 0.95, 0.95, 0.9, 0.9, 0.7, 0.7, 0.5, 0.5, 0.25, 0.25, 1.0], 'school_times': [84.0, 85.0, 121.0, 123.0], 'school_values': [1.0, 0.0, 0.0, 1.0], 'age_13_times': [121.0, 123.0], 'age_13_values': [1.0, 0.2], 'age_14_times': [121.0, 123.0], 'age_14_values': [1.0, 0.2], 'age_15_times': [121.0, 123.0], 'age_15_values': [1.0, 0.2]}

    _npi_effectiveness_range = {'work': [1.,1.], 'other_locations': [0.8, 1.], 'school': [1.,1.]}


    plot_mixing_params_over_time(_mixing_params, _npi_effectiveness_range)
