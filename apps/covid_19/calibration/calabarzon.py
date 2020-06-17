from autumn.constants import Region
from apps.covid_19.calibration import base


def run_calibration_chain(max_seconds: int, run_id: int):
    base.run_calibration_chain(
        max_seconds, run_id, Region.CALABARZON, PAR_PRIORS, TARGET_OUTPUTS, mode="autumn_mcmc",
    )


PAR_PRIORS = [
    {"param_name": "contact_rate", "distribution": "uniform", "distri_params": [0.010, 0.05],},
    {"param_name": "start_time", "distribution": "uniform", "distri_params": [0.0, 40.0],},
    # Add extra params for negative binomial likelihood
    {
        "param_name": "infection_deathsXall_dispersion_param",
        "distribution": "uniform",
        "distri_params": [0.1, 5.0],
    },
    {
        "param_name": "notifications_dispersion_param",
        "distribution": "uniform",
        "distri_params": [0.1, 5.0],
    },
    {
        "param_name": "prevXlateXclinical_icuXamong_dispersion_param",
        "distribution": "uniform",
        "distri_params": [0.1, 5.0],
    },
    {
        "param_name": "compartment_periods_calculated.incubation.total_period",
        "distribution": "gamma",
        "distri_mean": 5.0,
        "distri_ci": [4.4, 5.6],
    },
    {
        "param_name": "compartment_periods_calculated.total_infectious.total_period",
        "distribution": "gamma",
        "distri_mean": 7.0,
        "distri_ci": [4.5, 9.5],
    },
]

# Death counts:
death_times = [70, 71, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 104, 105, 106, 107, 108, 109, 110, 112, 113, 115, 118, 120, 123, 124, 126, 129, 131, 132, 133, 135, 136, 139, 143, 151, 152,]
death_values = [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 5, 4, 3, 2, 3, 2, 5, 7, 4, 2, 4, 4, 6, 7, 1, 1, 1, 4, 3, 3, 1, 1, 2, 1, 2, 1, 2, 1, 2, 2, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1,]

# notification data
notification_times = [51, 55, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 151, 153, 154, 155, 156, 158, 159, 160, 161,]
notification_counts = [1, 1, 1, 1, 1, 5, 7, 4, 3, 8, 7, 15, 10, 16, 13, 14, 17, 19, 18, 27, 30, 32, 27, 24, 19, 25, 23, 21, 26, 25, 18, 22, 30, 21, 26, 26, 45, 22, 27, 22, 24, 25, 24, 20, 22, 22, 26, 16, 11, 16, 13, 8, 11, 12, 3, 8, 3, 4, 3, 4, 8, 4, 10, 9, 9, 4, 17, 11, 4, 7, 9, 6, 14, 10, 13, 7, 5, 6, 12, 7, 7, 3, 8, 3, 5, 2, 18, 7, 4, 3, 9, 5, 3, 3, 3, 3, 5, 2, 1, 2, 1, 3, 1, 2,]

# ICU data
icu_times = [137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167,]
icu_counts = [60, 51, 52, 42, 72, 70, 50, 55, 58, 65, 48, 47, 63, 60, 62, 62, 58, 51, 60, 56, 45, 51, 47, 31, 39, 44, 32, 52, 45, 54, 66,]

TARGET_OUTPUTS = [
    {
        "output_key": "infection_deathsXall",
        "years": death_times,
        "values": death_values,
        "loglikelihood_distri": "negative_binomial",
    },
    {
        "output_key": "notifications",
        "years": notification_times,
        "values": notification_counts,
        "loglikelihood_distri": "negative_binomial",
    },
    {
        "output_key": "prevXlateXclinical_icuXamong",
        "years": icu_times,
        "values": icu_counts,
        "loglikelihood_distri": "negative_binomial",
    },
]
