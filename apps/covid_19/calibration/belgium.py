from apps.covid_19.calibration import base
from autumn.constants import Region
from apps.covid_19.mixing_optimisation.utils import (
    get_prior_distributions_for_opti,
    get_target_outputs_for_opti,
)


country = Region.BELGIUM

PAR_PRIORS = get_prior_distributions_for_opti()
# TARGET_OUTPUTS = get_target_outputs_for_opti(country, data_start_time=50, update_jh_data=False)
TARGET_OUTPUTS = [{'output_key': 'notifications', 'years': [50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173], 'values': [0, 0, 0, 0, 4, 0, 0, 2, 5, 3, 13, 4, 11, 34, 30, 48, 43, 67, 48, 61, 74, 0, 342, 342, 0, 403, 407, 676, 63, 1294, 1035, 665, 967, 1427, 1452, 2129, 2885, 2546, 2433, 2619, 3009, 4324, 4244, 4450, 3735, 5903, 3802, 3634, 5491, 4344, 8681, 5233, 5288, 4342, 5252, 4603, 4617, 5599, 5525, 5850, 4676, 4301, 4451, 4583, 5386, 4913, 4463, 4309, 3996, 4076, 6032, 6201, 4806, 4339, 3985, 4406, 6111, 5614, 4649, 3896, 3923, 3877, 3403, 3242, 3446, 3560, 3450, 3534, 2711, 2412, 2615, 3287, 2959, 2405, 1625, 4043, 2013, 1887, 2095, 1604, 1936, 1570, 1653, 1871, 1805, 1650, 1557, 1326, 1205, 1741, 1003, 1266, 1541, 1425, 1514, 968, 1279, 1115, 1218, 1346, 1295, 1221, 958], 'loglikelihood_distri': 'negative_binomial'}, {'output_key': 'infection_deathsXall', 'years': [50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173], 'values': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 4, 0, 2, 1, 18, 15, 22, 16, 34, 43, 36, 56, 35, 74, 149, 186, 183, 284, 294, 214, 374, 382, 670, 652, 714, 760, 644, 568, 1038, 1034, 1103, 1152, 839, 686, 744, 1044, 842, 1029, 935, 1115, 498, 559, 1172, 837, 727, 1005, 843, 420, 338, 909, 795, 674, 739, 621, 315, 288, 693, 649, 539, 626, 346, 268, 210, 627, 494, 428, 384, 468, 170, 160, 545, 363, 338, 351, 282, 118, 121, 134, 412, 377, 324, 215, 113, 556, 324, 359, 176, 357, 204, 77, 55, 286, 245, 151, 202, 181, 36, 38, 233, 184, 135, 173, 128, 43, 15], 'loglikelihood_distri': 'negative_binomial'}]

MULTIPLIERS = {}


def run_calibration_chain(max_seconds: int, run_id: int):
    base.run_calibration_chain(
        max_seconds, run_id, country, PAR_PRIORS, TARGET_OUTPUTS, mode="autumn_mcmc",
    )


if __name__ == "__main__":
    for i in range(len(TARGET_OUTPUTS)):
        print(TARGET_OUTPUTS[i]['output_key'])
        print(TARGET_OUTPUTS[i]['years'])
        print([[v] for v in TARGET_OUTPUTS[i]['values']])
        print()

    run_calibration_chain(
        30, 1
    )  # first argument only relevant for autumn_mcmc mode (time limit in seconds)
