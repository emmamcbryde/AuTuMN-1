

def stratify_by_age(model_to_stratify, age_strata, mixing_matrix):
    """
    Stratify model by age
    Note that because the string passed is 'agegroup' rather than 'age', the standard SUMMER demography is not triggered
    """
    age_breakpoints = [int(i_break) for i_break in age_strata]
    age_params = {}
    model_to_stratify.stratify(
        "agegroup",
        age_breakpoints,
        [],
        {},
        adjustment_requests=age_params,
        mixing_matrix=mixing_matrix,
        verbose=False,
    )
    return model_to_stratify


def stratify_by_location(model_to_stratify, location_mixing, location_strata):
    props_location = {'a': 0.333, 'b': 0.333, 'c': 0.334}
    model_to_stratify.stratify(
        "location",
        location_strata,
        [],
        requested_proportions=props_location,
        verbose=False,
        entry_proportions=props_location,
        mixing_matrix=location_mixing,
    )
    return model_to_stratify
