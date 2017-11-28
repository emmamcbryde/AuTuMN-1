
import autumn.spreadsheet as spreadsheet
import copy
import tool_kit
from curve import scale_up_function, freeze_curve
from Tkinter import *
import numpy


def make_constant_function(value):
    """
    Function that returns a function of constant returned value with a deliberately irrelevant argument,
    to maintain consistency with the number of arguments to other functions that take time as an argument.

    Args:
        value: The value for the created function to return
        time: Irrelevant argument to the returned function, but necessary for consistency with other functions
    Returns:
        constant: The constant function
    """

    def constant(time):
        return value
    return constant


def find_latest_value_from_year_dict(dictionary, ceiling):
    """
    Finds the value corresponding to the latest key that is not into the future.

    Args:
        dictionary: The dictionary to be interrogated
        ceiling: Upper limit of time to prevent entries into the future being included
    Returns:
        The value corresponding to the key found through this process
    """

    return dictionary[max([i for i in dictionary if i <= int(ceiling)])]


class Inputs:
    def __init__(self, gui_inputs, runtime_outputs, js_gui=None):

        # GUI inputs
        self.gui_inputs = gui_inputs
        self.country = gui_inputs['country']
        self.scenarios = self.gui_inputs['scenarios_to_run']

        # parameter structures
        self.original_data = None
        self.derived_data = {}
        self.time_variants = {}
        self.model_constants = {}
        self.scaleup_data = {}
        self.scaleup_fns = {}

        # uncertainty
        self.param_ranges_unc = []
        self.int_ranges_unc = []
        self.data_to_fit = {}
        # for incidence for ex, width of normal posterior relative to CI width in data
        self.outputs_unc = [{'key': 'incidence', 'posterior_width': None, 'width_multiplier': 2.}]
        self.alternative_distribution_dict = {'tb_prop_casefatality_untreated_smearpos': ['beta_mean_stdev', .7, .15],
                                              'tb_timeperiod_activeuntreated': ['gamma_mean_stdev', 3., .5],
                                              'tb_multiplier_treated_protection': ['gamma_mean_stdev', 1., .6]}

        # intervention uncertainty
        self.intervention_uncertainty = False
        if self.intervention_uncertainty:
            self.uncertainty_intervention = 'int_prop_decentralisation'
            self.scenarios.append(15)
            self.n_samples = 4
            self.intervention_param_dict \
                = {'int_prop_treatment_support_relative': ['int_prop_treatment_support_improvement'],
                   'int_prop_decentralisation': ['int_ideal_detection'],
                   'int_prop_xpert': ['int_prop_xpert_smearneg_sensitivity', 'int_prop_xpert_sensitivity_mdr',
                                      'int_timeperiod_await_treatment_smearneg_xpert'],
                   'int_prop_ipt': ['int_prop_ipt_effectiveness', 'int_prop_ltbi_test_sensitivity',
                                    'int_prop_infections_in_household'],
                   'int_prop_acf': ['int_prop_acf_detections_per_round'],
                   'int_prop_awareness_raising': ['int_multiplier_detection_with_raised_awareness']}
            self.gui_inputs['output_by_scenario'] = True

        # increment comorbidity
        self.increment_comorbidity = False
        if self.increment_comorbidity:
            self.comorbidity_to_increment = 'diabetes'
            self.comorbidity_prevalences = {1: .05, 2: .1, 3: .2, 4: .3, 5: .4, 6: .5}

        # model structure
        self.available_strains = ['_ds', '_mdr', '_xdr']
        self.available_organs = ['_smearpos', '_smearneg', '_extrapul']
        self.agegroups = None
        self.strains = ['']
        self.organ_status = ['']
        self.riskgroups = []
        self.vary_force_infection_by_riskgroup = self.gui_inputs['is_vary_force_infection_by_riskgroup']
        self.mixing = {}
        self.compartment_types = ['susceptible_fully', 'susceptible_immune', 'latent_early', 'latent_late', 'active',
                                  'detect', 'missed', 'treatment_infect', 'treatment_noninfect']
        self.histories = ['']

        # interventions
        self.irrelevant_time_variants = []
        self.relevant_interventions = {}
        self.interventions_to_cost = {}
        self.intervention_startdates = {}
        self.potential_interventions_to_cost \
            = ['vaccination', 'xpert', 'treatment_support_relative', 'treatment_support_absolute', 'smearacf',
               'xpertacf', 'ipt_age0to5', 'ipt_age5to15', 'decentralisation', 'improve_dst', 'bulgaria_improve_dst',
               'intensive_screening', 'ipt_age15up', 'ngo_activities', 'opendoors_activities', 'awareness_raising']
        self.freeze_times = {}

        # miscellaneous
        self.runtime_outputs = runtime_outputs
        self.mode = 'epi_uncertainty'
        self.js_gui = js_gui
        if self.js_gui: self.js_gui('init')
        self.plot_count = 0
        self.emit_delay = .1
        self.treatment_outcome_types = []
        self.include_relapse_in_ds_outcomes = True

    ''' master method '''

    def read_and_load_data(self):
        """
        Master method of this object, calling all sub-methods to read and process data and define model structure.
        """

        # read all required data
        self.add_comment_to_gui_window('Reading Excel sheets with input data.\n')
        self.original_data = spreadsheet.read_input_data_xls(True, self.find_keys_of_sheets_to_read(), self.country)

        # define treatment history structure (should ideally go in define_model_structure, but can't)
        self.define_treatment_history_structure()

        # process constant parameters (age breakpoints come from sheets still, so has to come before defining structure)
        self.process_model_constants()

        # define model structure
        self.define_model_structure()

        # process time-variant parameters
        self.process_time_variants()

        # has to go after time variants so that the proportion in each risk-group has been specified
        self.define_riskgroup_structure()

        # find parameters that require processing (including processes that require model structure to be defined)
        self.find_additional_parameters()

        # classify interventions as to whether they apply and are to be costed
        self.classify_interventions()

        # add compartment for IPT if implemented
        self.define_ipt_structure()

        # calculate time-variant functions
        self.find_scaleup_functions()

        # create mixing matrix (has to be run after scale-up functions, so can't go in model structure method)
        if self.vary_force_infection_by_riskgroup:
            self.create_mixing_matrix()
        else:
            self.mixing = {}

        # define compartmental structure
        self.define_compartment_structure()

        # uncertainty-related analysis
        self.process_uncertainty_parameters()

        # optimisation-related methods
        self.find_intervention_startdates()  # currently sitting with intervention classification methods, though

        # make sure user inputs make sense
        self.reconcile_user_inputs()

        # perform checks (undeveloped still)
        self.checks()

    ''' constant parameter processing methods '''

    # populate with first round of unprocessed parameters (called before model structure defined)

    def process_model_constants(self):
        """
        Master method to call methods for processing constant model parameters.
        """

        # note ordering to list of sheets to be worked through is important for hierarchical loading of constants
        sheets_with_constants = ['country_constants', 'default_constants']
        if self.gui_inputs['riskgroup_diabetes']: sheets_with_constants += ['diabetes']
        self.add_model_constant_defaults(sheets_with_constants)

        # add "by definition" hard-coded parameters
        self.add_universal_parameters()

    def add_model_constant_defaults(self, other_sheets_with_constants):
        """
        Populate model_constants with data from control panel, country sheet or default sheet hierarchically
        - such that the control panel is read in preference to the country data in preference to the default back-ups.

        Args:
            other_sheets_with_constants: The sheets of original_data which contain model constants
        """

        # populate hierarchically from the earliest sheet in the list as available
        for other_sheet in other_sheets_with_constants:
            if other_sheet in self.original_data:
                for item in self.original_data[other_sheet]:
                    if item not in self.model_constants:
                        self.model_constants[item] = self.original_data[other_sheet][item]

    def add_universal_parameters(self):
        """
        Sets parameters that should never be changed in any situation, i.e. "by definition" parameters (although note
        that the infectiousness of the single infectious compartment for models unstratified by organ status is now set
        in set_fixed_infectious_proportion, because it's dependent upon loading parameters in find_functions_or_params).
        """

        # proportion progressing to the only infectious compartment for models unstratified by organ status
        if self.gui_inputs['n_organs'] < 2:
            self.model_constants['epi_prop'] = 1.

        # infectiousness of smear-positive and extrapulmonary patients
        else:
            self.model_constants['tb_multiplier_force_smearpos'] = 1.
            self.model_constants['tb_multiplier_force_extrapul'] = 0.

        # no additional protection for new patients (tb_multiplier_treated_protection is used for additional immunity)
        if len(self.histories) > 1:
            self.model_constants['tb_multiplier_new_protection'] = 1.
        else:
            self.model_constants['tb_multiplier_protection'] = 1.

        # add a time period to treatment for models unstratified by organ status
        if len(self.organ_status) == 1:
            self.model_constants['program_timeperiod_await_treatment'] \
                = self.model_constants['program_timeperiod_await_treatment_smearpos']

        # reference group for susceptibility
        self.model_constants['tb_multiplier_fully_protection'] = 1.

    # derive further parameters (called after model structure defined)

    def find_additional_parameters(self):
        """
        Find additional parameters.
        Includes methods that require the model structure to be defined,
        so that this can't be run with process_model_constants.
        """

        # find risk group-specific parameters
        if len(self.riskgroups) > 1: self.find_riskgroup_progressions()

        # calculate rates of progression to active disease or late latency
        self.find_latency_progression_rates()

        # find the time non-infectious on treatment from the total time on treatment and the time infectious
        self.find_noninfectious_period()

        # derive some basic parameters for IPT
        # self.find_ipt_params()

    def find_latency_progression_rates(self):
        """
        Find early progression rates by age group and by risk group status - i.e. early progression to active TB and
        stabilisation into late latency.
        """

        time_early = self.model_constants['tb_timeperiod_early_latent']
        for agegroup in self.agegroups:
            for riskgroup in self.riskgroups:
                prop_early = self.model_constants['tb_prop_early_progression' + riskgroup + agegroup]

                # early progression rate is early progression proportion divided by early time period
                self.model_constants['tb_rate_early_progression' + riskgroup + agegroup] = prop_early / time_early

                # stabilisation rate is one minus early progression proportion divided by early time period
                self.model_constants['tb_rate_stabilise' + riskgroup + agegroup] = (1. - prop_early) / time_early

    def find_riskgroup_progressions(self):
        """
        Code to adjust the progression rates to active disease for various risk groups.
        """

        for riskgroup in self.riskgroups:

            # find age above which adjustments should be made, with default assumption of applying to all age-groups
            start_age = -1.
            if 'riskgroup_startage' + riskgroup in self.model_constants:
                start_age = self.model_constants['riskgroup_startage' + riskgroup]

            # make adjustments for each age group if required
            for agegroup in self.agegroups:
                if 'riskgroup_multiplier' + riskgroup + '_progression' in self.model_constants\
                        and tool_kit.interrogate_age_string(agegroup)[0][0] >= start_age:
                    self.model_constants['tb_prop_early_progression' + riskgroup + agegroup] \
                        = tool_kit.apply_odds_ratio_to_proportion(
                        self.model_constants['tb_prop_early_progression' + agegroup],
                        self.model_constants['riskgroup_multiplier' + riskgroup + '_progression'])
                    self.model_constants['tb_rate_late_progression' + riskgroup + agegroup] \
                        = self.model_constants['tb_rate_late_progression' + agegroup] \
                          * self.model_constants['riskgroup_multiplier' + riskgroup + '_progression']
                else:
                    self.model_constants['tb_prop_early_progression' + riskgroup + agegroup] \
                        = self.model_constants['tb_prop_early_progression' + agegroup]
                    self.model_constants['tb_rate_late_progression' + riskgroup + agegroup] \
                        = self.model_constants['tb_rate_late_progression' + agegroup]

    def find_noninfectious_period(self):
        """
        Very simple calculation to work out the periods of time spent non-infectious for each strain (plus inappropriate
        if required).
        """

        for strain in self.strains:
            self.model_constants['tb_timeperiod_noninfect_ontreatment' + strain] \
                = self.model_constants['tb_timeperiod_ontreatment' + strain] \
                  - self.model_constants['tb_timeperiod_infect_ontreatment' + strain]

    ''' methods to define model structure '''

    def define_treatment_history_structure(self):
        """
        Define the structure for tracking patients' treatment histories (i.e. whether they are treatment naive "_new"
        patients, or whether they are previously treated "_treated" patients. Note that the list was set to an empty
        string (for no stratification) in initialisation of this object.
        """

        if self.gui_inputs['is_treatment_history']: self.histories = ['_new', '_treated']

    def define_model_structure(self):
        """
        Master method to define all aspects of model structure.
        """

        self.define_age_structure()
        self.define_strain_structure()
        self.define_organ_structure()

    def define_age_structure(self):
        """
        Define the model's age structure based on the breakpoints provided in spreadsheets.
        """

        # describe and work out age stratification structure for model from the list of age breakpoints
        self.agegroups, _ = tool_kit.get_agegroups_from_breakpoints(self.model_constants['age_breakpoints'])

        # find ageing rates and age-weighted parameters
        if len(self.agegroups) > 1:
            self.find_ageing_rates()
            self.find_fixed_age_specific_parameters()

    def find_ageing_rates(self):
        """
        Calculate ageing rates as the reciprocal of the width of the age bracket.
        """

        for agegroup in self.agegroups:
            age_limits, _ = tool_kit.interrogate_age_string(agegroup)
            if 'up' not in agegroup:
                self.model_constants['ageing_rate' + agegroup] = 1. / (age_limits[1] - age_limits[0])

    def find_fixed_age_specific_parameters(self):
        """
        Find weighted age-specific parameters using age weighting code from tool_kit.
        """

        model_breakpoints = [float(i) for i in self.model_constants['age_breakpoints']]  # convert list of ints to float
        for param in ['early_progression_age', 'late_progression_age', 'tb_multiplier_child_infectiousness_age']:

            # extract age-stratified parameters in the appropriate form
            prog_param_vals = {}
            prog_age_dict = {}
            for constant in self.model_constants:
                if param in constant:
                    prog_param_string, prog_stem = tool_kit.find_string_from_starting_letters(constant, '_age')
                    prog_age_dict[prog_param_string], _ = tool_kit.interrogate_age_string(prog_param_string)
                    prog_param_vals[prog_param_string] = self.model_constants[constant]

            param_breakpoints = tool_kit.find_age_breakpoints_from_dicts(prog_age_dict)

            # find and set age-adjusted parameters
            prog_age_adjusted_params = \
                tool_kit.adapt_params_to_stratification(param_breakpoints, model_breakpoints, prog_param_vals,
                                                        parameter_name=param,
                                                        whether_to_plot=self.gui_inputs['output_age_calculations'])
            for agegroup in self.agegroups:
                self.model_constants[prog_stem + agegroup] = prog_age_adjusted_params[agegroup]

    def define_riskgroup_structure(self):
        """
        Work out the risk group stratification.
        """

        # create list of risk group names
        for item in self.gui_inputs:
            if item.startswith('riskgroup_'):
                riskgroup = item.replace('riskgroup', '')
                if self.gui_inputs[item] and 'riskgroup_prop' + riskgroup in self.time_variants:
                    self.riskgroups.append(riskgroup)
                elif self.gui_inputs[item]:
                    self.add_comment_to_gui_window(
                        'Stratification requested for %s risk group, but proportions not specified'
                        % tool_kit.find_title_from_dictionary(riskgroup))

        # add the null group
        if len(self.riskgroups) == 0:
            self.riskgroups.append('')
        else:
            self.riskgroups.append('_norisk')

        # ensure some starting proportion of births go to the risk group stratum if value not loaded earlier
        for riskgroup in self.riskgroups:
            if 'riskgroup_prop' + riskgroup not in self.model_constants:
                self.model_constants['riskgroup_prop' + riskgroup] = 0.

    def define_strain_structure(self):
        """
        Finds the strains to be present in the model from a list of available strains and the integer value for the
        number of strains selected.
        """

        # unstratified by strain
        if self.gui_inputs['n_strains'] == 0:

            # if the model isn't stratified by strain, use DS-TB time-periods for the single strain
            for timeperiod in ['tb_timeperiod_infect_ontreatment', 'tb_timeperiod_ontreatment']:
                self.model_constants[timeperiod] = self.model_constants[timeperiod + '_ds']

        # stratified
        else:
            self.strains = self.available_strains[:self.gui_inputs['n_strains']]
            if self.gui_inputs['is_misassignment']:
                self.treatment_outcome_types = copy.copy(self.strains)

                # if misassigned strain treated with weaker regimen
                for strain in self.strains[1:]:
                    for treated_as in self.strains:
                        if self.strains.index(treated_as) < self.strains.index(strain):
                            self.treatment_outcome_types.append(strain + '_as' + treated_as[1:])

    def define_organ_structure(self):
        """
        Defines the organ status stratification from the number of statuses selected.
        Note that "organ" is the simplest single-word term that I can currently think of to describe whether patients
        have smear-positive, smear-negative or extrapulmonary disease.
        """

        if self.gui_inputs['n_organs'] > 1: self.organ_status = self.available_organs[:self.gui_inputs['n_organs']]

    def define_ipt_structure(self):

        for scenario in self.scenarios:
            if 'agestratified_ipt' in self.relevant_interventions[scenario] \
                    or 'ipt' in self.relevant_interventions[scenario]:
                self.compartment_types.append('onipt')

    def create_mixing_matrix(self):
        """
        Creates model attribute for mixing between population risk groups, for use in calculate_force_infection_vars
        method below only.
        """

        # create mixing matrix separately for each scenario, just in case risk groups being managed differently
        self.mixing = {}

        # next tier of dictionary is the "to" risk group that is being infected
        for to_riskgroup in self.riskgroups:
            self.mixing[to_riskgroup] = {}

            # last tier of dictionary is the "from" risk group describing the make up of contacts
            for from_riskgroup in self.riskgroups:
                if from_riskgroup != '_norisk':

                    # use parameters for risk groups other than "_norisk" if available
                    if 'prop_mix' + to_riskgroup + '_from' + from_riskgroup in self.model_constants:
                        self.mixing[to_riskgroup][from_riskgroup] \
                            = self.model_constants['prop_mix' + to_riskgroup + '_from' + from_riskgroup]

                    # otherwise use the latest value for the proportion of the population with that risk factor
                    else:
                        self.mixing[to_riskgroup][from_riskgroup] \
                            = find_latest_value_from_year_dict(self.scaleup_data[0]['riskgroup_prop' + from_riskgroup],
                                                               self.model_constants['current_time'])

            # give the remainder to the "_norisk" group without any risk factors
            if sum(self.mixing[to_riskgroup].values()) >= 1.:
                self.add_comment_to_gui_window(
                    'Total of proportions of contacts for risk group %s greater than one. Model invalid.'
                    % to_riskgroup)
            self.mixing[to_riskgroup]['_norisk'] = 1. - sum(self.mixing[to_riskgroup].values())

    def define_compartment_structure(self):
        """
        Determines the compartment types required for model run,
        not including stratifications by age and risk groups, etc.
        """

        # add elaboration compartments to default list of mandatory compartments
        if self.gui_inputs['is_lowquality']: self.compartment_types += ['lowquality']
        if 'int_prop_novel_vaccination' in self.relevant_interventions:
            self.compartment_types += ['susceptible_novelvac']

    ''' time variant parameter processing methods '''

    def process_time_variants(self):
        """
        Master method to perform all preparation and processing tasks for time-variant parameters.
        Does not perform the fitting of functions to the data, which is done later in find_scaleup_functions.
        Note that the order of call is important and can lead to errors if changed.
        """

        self.extract_freeze_times()  # goes first to remove from time-variants before they are processed
        self.find_organ_proportions()
        if 'country_programs' in self.original_data: self.time_variants.update(self.original_data['country_programs'])
        self.add_time_variant_defaults()  # add any necessary time-variants from defaults if not in country programs
        self.load_vacc_detect_time_variants()
        self.convert_percentages_to_proportions()
        self.find_treatment_outcomes()
        self.find_irrelevant_treatment_timevariants()
        self.add_demo_dictionaries_to_timevariants()
        if self.gui_inputs['is_timevariant_organs']:
            self.add_organ_status_to_timevariants()
        else:
            self.find_average_organ_status()
        self.tidy_time_variants()
        self.adjust_param_for_reporting('program_prop_detect', 'Bulgaria', 0.95)  # Bulgaria thought CDR over-estimated

    # general and demographic methods

    def extract_freeze_times(self):
        """
        Extract the freeze_times for each scenario, if specified.
        """

        if 'country_programs' in self.original_data and 'freeze_times' in self.original_data['country_programs']:
            self.freeze_times.update(self.original_data['country_programs'].pop('freeze_times'))

    def find_organ_proportions(self):
        """
        Calculates dictionaries with proportion of cases progressing to each organ status by year, and adds these to
        the derived_data attribute of the object.
        """

        self.derived_data.update(tool_kit.calculate_proportion_dict(self.original_data['notifications'],
                                                                    ['new_sp', 'new_sn', 'new_ep']))

    def add_time_variant_defaults(self):
        """
        Populates time-variant parameters with defaults if those values aren't found in the manually entered
        country-specific data.
        """

        for program_var in self.original_data['default_programs']:

            # if the key isn't in available for the country
            if program_var not in self.time_variants:
                self.time_variants[program_var] = self.original_data['default_programs'][program_var]

            # otherwise if it's there and load_data is requested in the country sheet, populate for the missing years
            else:
                for year in self.original_data['default_programs'][program_var]:
                    if year not in self.time_variants[program_var] \
                            and 'load_data' in self.original_data['country_programs'][program_var] \
                            and self.original_data['country_programs'][program_var]['load_data'] == u'yes':
                        self.time_variants[program_var][year] \
                            = self.original_data['default_programs'][program_var][year]

    def load_vacc_detect_time_variants(self):
        """
        Adds vaccination and case detection time-variants to the manually entered data loaded from the spreadsheets.
        Note that the manual inputs over-ride the loaded data if both are present.
        """

        # vaccination
        if self.time_variants['int_perc_vaccination']['load_data'] == u'yes':
            for year in self.original_data['bcg']:
                if year not in self.time_variants['int_perc_vaccination']:
                    self.time_variants['int_perc_vaccination'][year] = self.original_data['bcg'][year]

        # case detection
        if self.time_variants['program_perc_detect']['load_data'] == u'yes':
            for year in self.original_data['tb']['c_cdr']:
                if year not in self.time_variants['program_perc_detect']:
                    self.time_variants['program_perc_detect'][year] = self.original_data['tb']['c_cdr'][year]

    def convert_percentages_to_proportions(self):
        """
        Converts time-variant dictionaries to proportions if they are loaded as percentages in their raw form.
        """

        for time_variant in self.time_variants.keys():
            if 'perc_' in time_variant:  # if a percentage
                prop_name = time_variant.replace('perc', 'prop')
                self.time_variants[prop_name] = {}
                for year in self.time_variants[time_variant]:
                    if type(year) == int or 'scenario' in year:  # to exclude load_data, smoothness, etc.
                        self.time_variants[prop_name][year] = self.time_variants[time_variant][year] / 1e2
                    else:
                        self.time_variants[prop_name][year] = self.time_variants[time_variant][year]

    # treatment outcome methods

    def find_treatment_outcomes(self):
        """
        Master method for working through all the processes for finding treatment outcome functions.
        """

        self.aggregate_treatment_outcomes()
        self.calculate_treatment_outcome_proportions()
        self.add_treatment_outcomes_to_timevariants()

    def aggregate_treatment_outcomes(self, include_hiv=True):
        """
        Sums the treatment outcome numbers from the Global TB Report to get aggregate values for the number of patients
        achieving 1) success, 2) death on treatment, 3) unfavourable outcomes other than death on treatment (termed
        default here.

        Args:
            include_hiv: Whether to include the HIV patients in calculations
                (because may not be needed for models with explicit HIV strata)
        """

        ''' up to 2011 fields for DS-TB '''

        # create string conversion structures for communcation between GTB report and AuTuMN
        hiv_statuses_to_include = ['']
        if include_hiv: hiv_statuses_to_include.append('hiv_')
        pre2011_map_gtb_to_autumn = {'_cmplt': '_success',
                                     '_cur': '_success',
                                     '_def': '_default',
                                     '_fail': '_default',
                                     '_died': '_death'}

        # by each outcome, find total number of patients achieving that outcome (up to 2011, with or without HIV)
        for outcome in pre2011_map_gtb_to_autumn:
            self.derived_data[self.strains[0] + '_new' + pre2011_map_gtb_to_autumn[outcome]] = {}
            self.derived_data[self.strains[0] + '_treated' + pre2011_map_gtb_to_autumn[outcome]] = {}

        # needs another loop to prevent the default dictionaries being blanked after working out default
        for outcome in pre2011_map_gtb_to_autumn:
            for hiv_status in hiv_statuses_to_include:

                # new outcomes are disaggregated by organ involvement and hiv status up to 2011
                for organ in ['sp', 'snep']:

                    # for smear-negative/extrapulmonary where cure isn't an outcome
                    if organ != 'snep' or outcome != '_cur':
                        self.derived_data[self.strains[0] + '_new' + pre2011_map_gtb_to_autumn[outcome]] \
                            = tool_kit.increment_dictionary_with_dictionary(
                            self.derived_data[self.strains[0] + '_new' + pre2011_map_gtb_to_autumn[outcome]],
                            self.original_data['outcomes'][hiv_status + 'new_' + organ + outcome])

                # re-treatment outcomes are only disaggregated by hiv status pre-2011
                self.derived_data[self.strains[0] + '_treated' + pre2011_map_gtb_to_autumn[outcome]] \
                    = tool_kit.increment_dictionary_with_dictionary(
                    self.derived_data[self.strains[0] + '_treated' + pre2011_map_gtb_to_autumn[outcome]],
                    self.original_data['outcomes'][hiv_status + 'ret' + outcome])

        ''' post-2011 fields for DS-TB '''

        # create string conversion structures
        hiv_statuses_to_include = ['newrel']
        if include_hiv: hiv_statuses_to_include.append('tbhiv')
        post2011_map_gtb_to_autumn = {'_succ': '_success',
                                      '_fail': '_default',
                                      '_lost': '_default',
                                      '_died': '_death'}

        # by each outcome, find total number of patients achieving that outcome
        for outcome in post2011_map_gtb_to_autumn:

            # new outcomes are disaggregated by hiv status post-2011
            for hiv_status in hiv_statuses_to_include:
                self.derived_data[self.strains[0] + '_new' + post2011_map_gtb_to_autumn[outcome]] \
                    = tool_kit.increment_dictionary_with_dictionary(
                    self.derived_data[self.strains[0] + '_new' + post2011_map_gtb_to_autumn[outcome]],
                    self.original_data['outcomes'][hiv_status + outcome])

            # previously treated outcomes (now excluding relapse) are not disaggregated post-2011
            self.derived_data[self.strains[0] + '_treated' + post2011_map_gtb_to_autumn[outcome]] \
                = tool_kit.increment_dictionary_with_dictionary(
                self.derived_data[self.strains[0] + '_treated' + post2011_map_gtb_to_autumn[outcome]],
                self.original_data['outcomes']['ret_nrel' + outcome])

        # add re-treatment rates on to new if the model is not stratified by treatment history
        if not self.gui_inputs['is_treatment_history']:
            for outcome in ['_success', '_default', '_death']:
                self.derived_data[self.strains[0] + outcome] = {}
                for history in ['_new', '_treated']:
                    self.derived_data[self.strains[0] + outcome] \
                        = tool_kit.increment_dictionary_with_dictionary(
                        self.derived_data[self.strains[0] + outcome],
                        self.derived_data[self.strains[0] + history + outcome])

        ''' MDR and XDR-TB '''

        # simpler because unaffected by 2011 changes
        for strain in self.strains[1:]:
            for outcome in post2011_map_gtb_to_autumn:
                self.derived_data[strain + post2011_map_gtb_to_autumn[outcome]] = {}
                self.derived_data[strain + post2011_map_gtb_to_autumn[outcome]] \
                    = tool_kit.increment_dictionary_with_dictionary(
                        self.derived_data[strain + post2011_map_gtb_to_autumn[outcome]],
                        self.original_data['outcomes'][strain[1:] + outcome])

        # duplicate outcomes by treatment history because not provided as disaggregated for resistant strains
        for history in self.histories:
            for outcome in ['_success', '_default', '_death']:
                for strain in self.strains[1:]:
                    self.derived_data[strain + history + outcome] \
                        = self.derived_data[strain + outcome]

    def calculate_treatment_outcome_proportions(self):
        """
        Find proportions by each outcome for later use in creating the treatment scale-up functions.
        """

        for history in self.histories:
            for strain in self.strains:
                self.derived_data.update(tool_kit.calculate_proportion_dict(
                    self.derived_data,
                    [strain + history + '_success', strain + history + '_death', strain + history + '_default'],
                    percent=False, floor=self.model_constants['tb_n_outcome_minimum'], underscore=False))

    def add_treatment_outcomes_to_timevariants(self):
        """
        Add treatment outcomes for all strains and treatment histories to the time variants attribute. Use the same
        approach as elsewhere to adding if requested and data not manually entered. Only done for success and death
        because default is derived from these.
        """

        for strain in self.strains:
            for outcome in ['_success', '_death']:
                for history in self.histories:
                    if self.time_variants['program_prop_treatment' + strain + history + outcome]['load_data'] == u'yes':
                        for year in self.derived_data['prop' + strain + history + outcome]:
                            if year not in self.time_variants['program_prop_treatment' + strain + history + outcome]:
                                self.time_variants['program_prop_treatment' + strain + history + outcome][year] \
                                    = self.derived_data['prop' + strain + history + outcome][year]

    # miscellaneous methods

    def find_irrelevant_treatment_timevariants(self):
        """
        Find treatment time-variant functions that are irrelevant to requested model structure (such as those specific
        to treatment history in models that are unstratified by treatment history, percentages and outcomes for strains
        not implemented in the current version of the model).
        """

        keep = {}
        for time_variant in self.time_variants:
            keep[time_variant] = True
            remove_on_strain = True
            strains = copy.copy(self.strains)
            if self.gui_inputs['is_misassignment']: strains.append('_inappropriate')
            for strain in strains:
                if strain in time_variant: remove_on_strain = False
            remove_on_history = True
            for history in self.histories:
                if history in time_variant: remove_on_history = False
            if len(self.histories) == 1:
                if '_new' in time_variant or '_treated' in time_variant: remove_on_history = True
            if 'program_prop_treatment' in time_variant and (remove_on_strain or remove_on_history):
                keep[time_variant] = False
            if 'program_perc_treatment' in time_variant: keep[time_variant] = False
            if not keep[time_variant]: self.irrelevant_time_variants += [time_variant]

    def add_demo_dictionaries_to_timevariants(self):
        """
        Add epidemiological time variant parameters to time_variants.
        Similarly to previous methods, only performed if requested and only populated where absent.
        """

        # for the two types of demographic parameters
        for demo_parameter in ['life_expectancy', 'rate_birth']:

            # if there are data available from the user-derived sheets and loading external data is requested
            if 'demo_' + demo_parameter in self.time_variants \
                    and self.time_variants['demo_' + demo_parameter]['load_data'] == u'yes':
                for year in self.original_data[demo_parameter]:
                    if year not in self.time_variants['demo_' + demo_parameter]:
                        self.time_variants['demo_' + demo_parameter][year] = self.original_data[demo_parameter][year]

            # if there are no data available from the user sheets
            else:
                self.time_variants['demo_' + demo_parameter] = self.original_data[demo_parameter]

    def add_organ_status_to_timevariants(self):
        """
        Populate organ status dictionaries where requested and not already loaded.
        """

        # conversion from GTB terminology to AuTuMN
        name_conversion_dict = {'_smearpos': '_sp', '_smearneg': '_sn'}

        # for the time variant progression parameters that are used (extrapulmonary just calculated as a complement)
        for organ in ['_smearpos', '_smearneg']:

            # populate absent values from derived data if input data available
            if 'epi_prop' + organ in self.time_variants:
                for year in self.derived_data['prop_new' + name_conversion_dict[organ]]:
                    if year not in self.time_variants['epi_prop' + organ]:
                        self.time_variants['epi_prop' + organ][year] \
                            = self.derived_data['prop_new' + name_conversion_dict[organ]][year]

            # otherwise if no input data available, just take the derived data straight from the loaded sheets
            else:
                self.time_variants['epi_prop' + organ] = self.derived_data['prop_new' + name_conversion_dict[organ]]

    def find_average_organ_status(self):
        """
        Determine proportion of incident cases that go to each organ status. If specified in input sheets, take the
        user-requested value. However if not, use the proportions of total notifications for the country being
        simulated.
        """

        name_conversion_dict = {'_smearpos': '_sp', '_smearneg': '_sn', '_extrapul': '_ep'}

        # if specific values requested
        if 'epi_prop_smearpos' in self.model_constants and 'epi_prop_smearneg' in self.model_constants:
            self.model_constants['epi_prop_extrapul'] \
                = 1. - self.model_constants['epi_prop_smearpos'] - self.model_constants['epi_prop_smearneg']

        # otherwise use aggregate notifications
        else:

            # count totals notified by each organ status and find denominator
            count_by_organ_status = {}
            for organ in name_conversion_dict.values():
                count_by_organ_status[organ] = numpy.sum(self.original_data['notifications']['new' + organ].values())
            total = numpy.sum(count_by_organ_status.values())

            # calculate proportions from totals
            for organ in name_conversion_dict:
                self.model_constants['epi_prop' + organ] = count_by_organ_status[name_conversion_dict[organ]] / total

    def tidy_time_variants(self):
        """
        Final tidying of time-variants, as described in comments to each line of code below.
        """

        for time_variant in self.time_variants:

            # add zero at starting time for model run to all program proportions
            if ('program_prop' in time_variant or 'int_prop' in time_variant) and '_death' not in time_variant:
                self.time_variants[time_variant][int(self.model_constants['start_time'])] = 0.

            # remove the load_data keys, as they have been used and are now redundant
            self.time_variants[time_variant] \
                = tool_kit.remove_specific_key(self.time_variants[time_variant], 'load_data')

            # remove keys for which values are nan
            self.time_variants[time_variant] = tool_kit.remove_nans(self.time_variants[time_variant])

    def adjust_param_for_reporting(self, param, country, adjustment_factor):
        """
        Adjust a parameter that is thought to be mis-reported by the country by a constant factor across the estimates
        for all years.

        Args:
            param: The string for the parameter to be adjusted
            country: The country to which this applies
            adjustment_factor: A float to multiply the reported values by to get the adjusted values
        """

        if self.country == country:
            for year in self.time_variants[param]:
                if type(year) == int: self.time_variants[param][year] *= adjustment_factor

    ''' classify interventions '''

    def classify_interventions(self):
        """
        Classify the interventions as to whether they are generally relevant, whether they apply to specific scenarios
        being run and whether they are to be costed.
        """

        self.find_irrelevant_time_variants()
        self.find_relevant_interventions()
        self.determine_organ_detection_variation()
        self.determine_riskgroup_detection_variation()
        self.find_potential_interventions_to_cost()
        self.find_interventions_to_cost()

    def find_irrelevant_time_variants(self):
        """
        List all the time-variant parameters that are not relevant to the current model structure (unstratified by
        the scenario being run).
        """

        for time_variant in self.time_variants:
            for strain in self.available_strains:

                # exclude programs relevant to strains that aren't included in the model
                if strain not in self.strains and strain in time_variant:
                    self.irrelevant_time_variants += [time_variant]

            # exclude time-variants that are percentages, irrelevant drug-susceptibility testing programs, inappropriate
            # treatment time-variants for single strain models, smear-negative parameters for unstratified models,
            # low-quality care sector interventions for models not including this.
            if 'perc_' in time_variant \
                    or (len(self.strains) < 2 and 'line_dst' in time_variant) \
                    or (len(self.strains) < 3 and 'secondline_dst' in time_variant) \
                    or ('_inappropriate' in time_variant
                                and (len(self.strains) < 2 or not self.gui_inputs['is_misassignment'])) \
                    or (len(self.organ_status) == 1 and 'smearneg' in time_variant) \
                    or ('lowquality' in time_variant and not self.gui_inputs['is_lowquality']) \
                    or (len(self.strains) > 1 and 'treatment_' in time_variant and 'timeperiod_' not in time_variant
                        and '_support' not in time_variant
                        and ('_ds' not in time_variant and 'dr' not in time_variant
                             and '_inappropriate' not in time_variant)):
                self.irrelevant_time_variants += [time_variant]

    def find_relevant_interventions(self):
        """
        Code to create lists of the programmatic interventions that are relevant to a particular scenario being run.

        Creates:
            self.relevant_interventions: A dict with keys scenarios and values lists of scenario-relevant programs
        """

        for scenario in self.scenarios:
            self.relevant_interventions[scenario] = []
            for time_variant in self.time_variants:
                for key in self.time_variants[time_variant]:
                    # if 1) not irrelevant to structure, 2) it is a programmatic time variant,
                    # 3) it hasn't been added yet, 4) it has a non-zero entry for any year or scenario value
                    if time_variant not in self.irrelevant_time_variants \
                            and ('program_' in time_variant or 'int_' in time_variant) \
                            and time_variant not in self.relevant_interventions[scenario] \
                            and ((type(key) == int and self.time_variants[time_variant][key] > 0.)
                                 or (type(key) == str and key == tool_kit.find_scenario_string_from_number(scenario))):
                        self.relevant_interventions[scenario] += [time_variant]

        # add terms for the IPT interventions to the list that refer to its general type without the specific age string
        for scenario in self.scenarios:
            for intervention in self.relevant_interventions[scenario]:
                if 'int_prop_ipt_age' in intervention:
                    self.relevant_interventions[scenario] += ['agestratified_ipt']
                elif 'int_prop_ipt' in intervention and 'community_ipt' not in intervention:
                    self.relevant_interventions[scenario] += ['ipt']

            # similarly, add universal terms for ACF interventions, regardless of the risk-group applied to
            riskgroups_to_loop = copy.copy(self.riskgroups)
            if '' not in riskgroups_to_loop: riskgroups_to_loop.append('')
            for riskgroup in riskgroups_to_loop:
                for acf_type in ['smear', 'xpert']:
                    for whether_cxr_screen in ['', 'cxr']:
                        intervention = 'int_prop_' + whether_cxr_screen + acf_type + 'acf' + riskgroup
                        if intervention in self.relevant_interventions[scenario]:
                            if '_smearpos' in self.organ_status:
                                self.relevant_interventions[scenario] += ['acf']
                            else:
                                self.add_comment_to_gui_window(
                                    intervention + ' not implemented as insufficient organ stratification structure')
                            if '_smearneg' not in self.organ_status and acf_type == 'xpert':
                                self.add_comment_to_gui_window(
                                    'Effect of ' + intervention
                                    + ' on smear-negatives not incorporated, as absent from model')

    def determine_organ_detection_variation(self):
        """
        Work out what we're doing with variation of detection rates by organ status (consistently for all scenarios).
        """

        # start with user request
        self.vary_detection_by_organ = self.gui_inputs['is_vary_detection_by_organ']

        # turn off and warn if model unstratified by organ status
        if len(self.organ_status) == 1 and self.vary_detection_by_organ:
            self.vary_detection_by_organ = False
            self.add_comment_to_gui_window(
                'Requested variation by organ status turned off, as model is unstratified by organ status.')

        for scenario in self.scenarios:
            # turn on and warn if Xpert requested but variation not requested
            if len(self.organ_status) > 1 and 'int_prop_xpert' in self.relevant_interventions[scenario] \
                    and not self.vary_detection_by_organ:
                self.vary_detection_by_organ = True
                self.add_comment_to_gui_window(
                    'Variation in detection by organ status added for Xpert implementation, although not requested.')

            # leave effect of Xpert on improved diagnosis of smear-negative disease turned off if no organ strata
            elif len(self.organ_status) == 1 and 'int_prop_xpert' in self.relevant_interventions[scenario]:
                self.add_comment_to_gui_window(
                    'Effect of Xpert on smear-negative detection not simulated as model unstratified by organ status.')

        # set relevant attributes
        self.organs_for_detection = ['']
        if self.vary_detection_by_organ: self.organs_for_detection = self.organ_status

    def determine_riskgroup_detection_variation(self):
        """
        Set variation in detection by risk-group according to whether ACF or intensive screening implemented (in any of
        the scenarios).
        """

        self.vary_detection_by_riskgroup = False
        for scenario in self.scenarios:
            for intervention in self.relevant_interventions[scenario]:
                if 'acf' in intervention or 'intensive_screening' in intervention or 'ngo' in intervention:
                    self.vary_detection_by_riskgroup = True
        self.riskgroups_for_detection = ['']
        if self.vary_detection_by_riskgroup: self.riskgroups_for_detection = self.riskgroups

    def find_potential_interventions_to_cost(self):
        """
        Creates a list of the interventions that could potentially be costed if they are requested - that is, the ones
        for which model.py has popsize calculations coded.
        """

        if len(self.strains) > 1:
            self.potential_interventions_to_cost += ['shortcourse_mdr']
            self.potential_interventions_to_cost += ['food_voucher_ds']
            self.potential_interventions_to_cost += ['food_voucher_mdr']
        for organ in self.organ_status:
            self.potential_interventions_to_cost += ['ambulatorycare' + organ]
        if self.gui_inputs['is_lowquality']:
            self.potential_interventions_to_cost += ['engage_lowquality']
        for riskgroup in ['_prison', '_indigenous', '_urbanpoor', '_ruralpoor']:
            if self.gui_inputs['riskgroup' + riskgroup]:
                self.potential_interventions_to_cost += ['xpertacf' + riskgroup, 'cxrxpertacf' + riskgroup]

    def find_interventions_to_cost(self):
        """
        Work out which interventions should be costed, selecting from the ones that can be costed in
        self.potential_interventions_to_cost.
        """

        for scenario in self.scenarios:
            self.interventions_to_cost[scenario] = []
            for intervention in self.potential_interventions_to_cost:
                if 'int_prop_' + intervention in self.relevant_interventions[scenario]:
                    self.interventions_to_cost[scenario] += [intervention]

        if self.intervention_uncertainty: self.interventions_to_cost[15] = self.interventions_to_cost[0]

    # actually has to be called later and is just required for optimisation

    def find_intervention_startdates(self):
        """
        Find the dates when the different interventions start and populate self.intervention_startdates
        """

        for scenario in self.scenarios:
            self.intervention_startdates[scenario] = {}
            for intervention in self.interventions_to_cost[scenario]:
                self.intervention_startdates[scenario][intervention] = None
                years_pos_coverage \
                    = [key for (key, value)
                       in self.scaleup_data[scenario]['int_prop_' + intervention].items() if value > 0.]
                if years_pos_coverage:  # i.e. some coverage present from start
                    self.intervention_startdates[scenario][intervention] = min(years_pos_coverage)

    ''' finding scale-up functions and related methods '''

    def find_scaleup_functions(self):
        """
        Master method for calculation of time-variant parameters/scale-up functions.
        """

        # extract data into structures for creating time-variant parameters or constant ones
        self.find_data_for_functions_or_params()

        # find scale-up functions or constant parameters
        if self.increment_comorbidity: self.create_comorbidity_scaleups()
        self.find_constant_functions()
        self.find_scaleups()

        # find the proportion of cases that are infectious for models that are unstratified by organ status
        if len(self.organ_status) < 2: self.set_fixed_infectious_proportion()

        # add parameters for IPT and treatment support
        self.add_missing_economics()

    def find_data_for_functions_or_params(self):
        """
        Method to load all the dictionaries to be used in generating scale-up functions to a single attribute of the
        class instance (to avoid creating heaps of functions for irrelevant programs).

        Creates: self.scaleup_data, a dictionary of the relevant scale-up data for creating scale-up functions in
            set_scaleup_functions within the model object. First tier of keys is the scenario to be run, next is the
            time variant parameter to be calculated.
        """

        for scenario in self.scenarios:
            self.scaleup_data[scenario] = {}

            # find the programs that are relevant and load them to the scaleup_data attribute
            for time_variant in self.time_variants:
                if time_variant not in self.irrelevant_time_variants:
                    self.scaleup_data[scenario][str(time_variant)] = {}
                    for i in self.time_variants[time_variant]:
                        if i == 'scenario_' + str(scenario):
                            self.scaleup_data[scenario][str(time_variant)]['scenario'] \
                                = self.time_variants[time_variant][i]
                        elif type(i) == str:
                            if 'scenario_' not in i:
                                self.scaleup_data[scenario][str(time_variant)][i] = self.time_variants[time_variant][i]
                        else:
                            self.scaleup_data[scenario][str(time_variant)][i] = self.time_variants[time_variant][i]

    def find_constant_functions(self):
        """
        Method that can be used to set some variables that might usually be time-variant to be constant instead,
        by creating a function that is just a single constant value (through the static make_constant_function method
        above).
        """

        for scenario in self.scenarios:

            # initialise the scale-up function dictionary for the scenario
            self.scaleup_fns[scenario] = {}

            # set constant functions for proportion smear-positive and negative
            if not self.gui_inputs['is_timevariant_organs']:
                for organ in ['pos', 'neg']:
                    self.scaleup_fns[scenario]['epi_prop_smear' + organ] \
                        = make_constant_function(self.model_constants['epi_prop_smear' + organ])

    def create_comorbidity_scaleups(self):
        """
        Another method that is hard-coded and not elegantly embedded with the GUI, but aiming towards creating better
        appearing outputs when we want to look at what varying levels of comorbidities do over time.
        """

        for scenario in self.comorbidity_prevalences:
            self.scenarios.append(scenario)
            for attribute in ['scaleup_data', 'interventions_to_cost', 'relevant_interventions']:
                getattr(self, attribute)[scenario] = copy.deepcopy(getattr(self, attribute)[0])
                self.mixing = {}
            self.scaleup_data[scenario]['riskgroup_prop_' + self.comorbidity_to_increment]['scenario'] \
                = self.comorbidity_prevalences[scenario]

    def find_scaleups(self):
        """
        Calculate the scale-up functions from the scale-up data attribute and populate to a dictionary with keys of the
        scenarios to be run.
        Note that the 'demo_life_expectancy' parameter has to be given this name and base.py will then calculate
        population death rates automatically.
        """

        for scenario in self.scenarios:
            scenario_name = tool_kit.find_scenario_string_from_number(scenario)

            # define scale-up functions from these datasets
            for param in self.scaleup_data[scenario]:
                if param not in self.scaleup_fns[scenario]:  # if not already set as constant previously

                    # extract and remove the smoothness parameter from the dictionary
                    smoothness = self.gui_inputs['default_smoothness']
                    if 'smoothness' in self.scaleup_data[scenario][param]:
                        smoothness = self.scaleup_data[scenario][param].pop('smoothness')

                    # if the parameter is being modified for the scenario being run
                    scenario_for_function = None
                    if 'scenario' in self.scaleup_data[scenario][param]:
                        scenario_for_function = [self.model_constants['scenario_full_time'],
                                                 self.scaleup_data[scenario][param].pop('scenario')]

                    # upper bound depends on whether the parameter is a proportion
                    upper_bound = None
                    if 'prop_' in param: upper_bound = 1.

                    # calculate the scaling function
                    self.scaleup_fns[scenario][param] \
                        = scale_up_function(self.scaleup_data[scenario][param].keys(),
                                            self.scaleup_data[scenario][param].values(),
                                            self.gui_inputs['fitting_method'], smoothness,
                                            bound_low=0., bound_up=upper_bound,
                                            intervention_end=scenario_for_function,
                                            intervention_start_date=self.model_constants['scenario_start_time'])

                    # freeze at point in time if necessary
                    if scenario_name in self.freeze_times \
                            and self.freeze_times[scenario_name] < self.model_constants['recent_time']:
                        self.scaleup_fns[scenario][param] \
                            = freeze_curve(self.scaleup_fns[scenario][param],
                                           self.freeze_times[scenario_name])

    def set_fixed_infectious_proportion(self):
        """
        Find a multiplier for the proportion of all cases infectious for models unstructured by organ status.
        """

        self.model_constants['tb_multiplier_force'] \
            = self.model_constants['epi_prop_smearpos'] \
              + self.model_constants['epi_prop_smearneg'] * self.model_constants['tb_multiplier_force_smearneg']

    def add_missing_economics(self):
        """
        To avoid errors because no economic values are available for age-stratified IPT, use the unstratified values
        for each age group for which no value is provided.
        Also need to reproduce economics parameters for relative and absolute treatment support, so that only single set
        of parameters need to be entered.
        """

        for param in ['_saturation', '_inflectioncost', '_unitcost', '_startupduration', '_startupcost']:

            # ipt
            for agegroup in self.agegroups:
                if 'econ' + param + '_ipt' + agegroup not in self.model_constants:
                    self.model_constants['econ' + param + '_ipt' + agegroup] \
                        = self.model_constants['econ' + param + '_ipt']
                    self.add_comment_to_gui_window('"' + param[1:] + '" parameter unavailable for "' + agegroup +
                                                   '" age-group, so default value used.\n')

            # treatment support
            for treatment_support_type in ['_relative', '_absolute']:
                self.model_constants['econ' + param + '_treatment_support' + treatment_support_type] \
                    = self.model_constants['econ' + param + '_treatment_support']

    ''' uncertainty-related methods '''

    def process_uncertainty_parameters(self):
        """
        Master method to uncertainty processing, calling other relevant methods.
        """

        # specify the parameters to be used for uncertainty
        if self.gui_inputs['output_uncertainty'] or self.intervention_uncertainty:
            self.find_uncertainty_distributions()
            self.get_data_to_fit()

    def find_uncertainty_distributions(self):
        """
        Populate a dictionary of uncertainty parameters from the inputs dictionary in a format that matches code for
        uncertainty.
        """

        for param in self.model_constants:
            if ('tb_' in param or 'start_time' in param) \
                    and '_uncertainty' in param and type(self.model_constants[param]) == dict:
                self.param_ranges_unc += [{'key': param[:-12],
                                           'bounds': [self.model_constants[param]['lower'],
                                                      self.model_constants[param]['upper']],
                                           'distribution': 'uniform'}]
            elif 'int_' in param and '_uncertainty' in param and type(self.model_constants[param]) == dict:
                self.int_ranges_unc += [{'key': param[:-12],
                                         'bounds': [self.model_constants[param]['lower'],
                                                    self.model_constants[param]['upper']],
                                         'distribution': 'uniform'}]

        # change distributions for parameters hard-coded to alternative distributions in instantiation above
        for n_param in range(len(self.param_ranges_unc)):
            if self.param_ranges_unc[n_param]['key'] in self.alternative_distribution_dict:
                self.param_ranges_unc[n_param]['distribution'] \
                    = self.alternative_distribution_dict[self.param_ranges_unc[n_param]['key']][0]
                if len(self.alternative_distribution_dict[self.param_ranges_unc[n_param]['key']]) > 1:
                    self.param_ranges_unc[n_param]['additional_params'] \
                        = self.alternative_distribution_dict[self.param_ranges_unc[n_param]['key']][1:]

    def get_data_to_fit(self):
        """
        Extract data for model fitting. Choices currently hard-coded above.
        """

        # decide whether calibration or uncertainty analysis is being run
        if self.mode == 'calibration':
            var_to_iterate = self.calib_outputs
        elif self.mode == 'epi_uncertainty':
            var_to_iterate = self.outputs_unc

        inc_conversion_dict = {'incidence': 'e_inc_100k',
                               'incidence_low': 'e_inc_100k_lo',
                               'incidence_high': 'e_inc_100k_hi'}
        mort_conversion_dict = {'mortality': 'e_mort_exc_tbhiv_100k',
                                'mortality_low': 'e_mort_exc_tbhiv_100k_lo',
                                'mortality_high': 'e_mort_exc_tbhiv_100k_hi'}

        # work through vars to be used and populate into the data fitting dictionary
        for output in var_to_iterate:
            if output['key'] == 'incidence':
                for key in inc_conversion_dict:
                    self.data_to_fit[key] = self.original_data['tb'][inc_conversion_dict[key]]
            elif output['key'] == 'mortality':
                for key in mort_conversion_dict:
                    self.data_to_fit[key] = self.original_data['tb'][mort_conversion_dict[key]]
            else:
                self.add_comment_to_gui_window(
                    'Warning: Calibrated output %s is not directly available from the data' % output['key'])

    ''' miscellaneous methods '''

    def reconcile_user_inputs(self):
        """
        Method to ensure that user inputs make sense within the model, including that elaborations that are specific to
        particular ways of structuring the model are turned off with a warning if the model doesn't have the structure
        to allow for those elaborations.
        """

        if self.gui_inputs['is_misassignment'] and self.gui_inputs['n_strains'] <= 1:
            self.add_comment_to_gui_window('Misassignment requested, but not implemented as single strain model only')
            self.gui_inputs['is_misassignment'] = False
        if self.gui_inputs['is_amplification'] and self.gui_inputs['n_strains'] <= 1:
            self.add_comment_to_gui_window(
                'Resistance amplification requested, but not implemented as single strain model only')
            self.gui_inputs['is_amplification'] = False
        # if len(self.riskgroups) == 0 and self.vary_force_infection_by_riskgroup:
        #     self.add_comment_to_gui_window(
        #         'Heterogeneous mixing requested, but not implemented as no risk groups are present')
        #     self.vary_force_infection_by_riskgroup = False
        if self.gui_inputs['n_organs'] <= 1 and self.gui_inputs['is_timevariant_organs']:
            self.add_comment_to_gui_window(
                'Time-variant organ status requested, but not implemented as no stratification by organ status')
            self.gui_inputs['is_timevariant_organs'] = False

    def find_keys_of_sheets_to_read(self):
        """
        Find keys of spreadsheets to read. Pretty simplistic at this stage, but expected to get more complicated as
        other sheets (like diabetes) are added as optional.
        """

        keys_of_sheets_to_read = ['bcg', 'rate_birth', 'life_expectancy', 'default_parameters', 'tb', 'notifications',
                                  'outcomes', 'country_constants', 'default_constants', 'country_programs',
                                  'default_programs']

        # add any optional sheets required for specific model being run (currently just diabetes)
        if 'riskgroup_diabetes' in self.gui_inputs: keys_of_sheets_to_read += ['diabetes']

        return keys_of_sheets_to_read

    def add_comment_to_gui_window(self, comment):
        """
        Output message to either JavaScript or Tkinter GUI.
        """

        if self.js_gui:
            self.js_gui('console', {"message":comment})
        else:
            self.runtime_outputs.insert(END, comment + '\n')
            self.runtime_outputs.see(END)

    def checks(self):
        """
        Not much in here as yet. However, this function is intended to contain all the data consistency checks for
        data entry.
        """

        # check that all entered times occur after the model start time
        for time in self.model_constants:
            if time[-5:] == '_time' and '_step_time' not in time:
                assert self.model_constants[time] >= self.model_constants['start_time'], \
                    '% is before model start time' % self.model_constants[time]
