from autumn.constants import Region
from apps.covid_19.calibration import base


def run_calibration_chain(max_seconds: int, run_id: int):
    base.run_calibration_chain(
        max_seconds, run_id, Region.CENTRAL_VISAYAS, PAR_PRIORS, TARGET_OUTPUTS, mode="autumn_mcmc",
    )


PAR_PRIORS = [
    {"param_name": "contact_rate", "distribution": "uniform", "distri_params": [0.010, 0.05],},
    {"param_name": "start_time", "distribution": "uniform", "distri_params": [0.0, 40.0],},
    # Add extra params for negative binomial likelihood
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

# notification data
notification_times = [48, 54, 62, 64, 66, 67, 68, 69, 70, 71, 72, 73, 75, 76, 77, 80, 82, 83, 84, 85, 88, 91, 95, 101, 103, 104, 105, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 146, 155, 156, 158, 159,]
notification_counts = [1, 1, 1, 1, 1, 2, 2, 1, 1, 3, 1, 2, 3, 1, 2, 1, 4, 3, 2, 1, 1, 1, 2, 1, 2, 2, 1, 1, 1, 2, 71, 1, 100, 40, 67, 19, 1, 57, 67, 47, 96, 27, 4, 3, 6, 2, 10, 66, 10, 5, 8, 5, 9, 20, 35, 25, 4, 3, 9, 13, 9, 12, 7, 7, 1, 1, 1, 3, 1, 1,]

# ICU data
icu_times = [137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167,]
icu_counts = [17, 17, 16, 17, 21, 23, 21, 26, 25, 26, 26, 27, 26, 26, 23, 25, 22, 31, 26, 38, 39, 27, 28, 30, 26, 28, 29, 36, 43, 35, 34,]

TARGET_OUTPUTS = [
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
