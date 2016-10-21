from numpy import isfinite
import tool_kit
import model
import os
import data_processing
import numpy
import datetime
from scipy.stats import norm, beta
from Tkinter import *
from scipy.optimize import minimize
from random import uniform
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import outputs
import autumn.economics
import itertools

def is_positive_definite(v):

    return isfinite(v) and v > 0.


def generate_candidates(n_candidates, param_ranges_unc):

    """
    Function for generating candidate parameters

    """

    # Dictionary for storing candidates
    param_candidates = {}
    for param_dict in param_ranges_unc:

        # Find bounds of parameter
        bound_low, bound_high = param_dict['bounds'][0], param_dict['bounds'][1]

        # Draw from distribution
        if param_dict['distribution'] == 'beta':
            x = numpy.random.beta(2., 2., n_candidates)
            x = bound_low + x * (bound_high - bound_low)
        elif param_dict['distribution'] == 'uniform':
            x = numpy.random.uniform(bound_low, bound_high, n_candidates)

            # Return values
        param_candidates[param_dict['key']] = x
    return param_candidates


def increment_list(increment, list_to_increment):

    return [sum(x) for x in zip(list_to_increment, increment)]


def elementwise_list_division(numerator, denominator):

    return [n / d for n, d in zip(numerator, denominator)]


def find_integer_dict_from_float_dict(float_dict):

    integer_dict = {}
    times = float_dict.keys()
    times.sort()
    start = numpy.floor(times[0])
    finish = numpy.floor(times[-1])
    float_years = numpy.linspace(start, finish, finish - start + 1.)
    for year in float_years:
        key = [t for t in times if t >= year][0]
        integer_dict[int(key)] = float_dict[key]

    return integer_dict


def extract_integer_dicts(models_to_analyse={}, dict_to_extract_from={}):

    integer_dict = {}
    for scenario in models_to_analyse:
        integer_dict[scenario] = {}
        for output in dict_to_extract_from[scenario]:
            integer_dict[scenario][output] \
                = find_integer_dict_from_float_dict(dict_to_extract_from[scenario][output])
    return integer_dict


def get_output_dicts_from_lists(models_to_analyse={}, output_dict_of_lists={}):

    """
    Convert output lists to dictionaries. This may actually not be that necessary - but the code is pretty short
    and elegant, so easy enough to include/remove as needed.

    """

    output_dictionary = {}
    for scenario in models_to_analyse:
        output_dictionary[scenario] = {}
        for output in output_dict_of_lists[scenario]:
            if output != 'times':
                output_dictionary[scenario][output] = dict(zip(output_dict_of_lists[scenario]['times'],
                                                               output_dict_of_lists[scenario][output]))
    return output_dictionary


class ModelRunner:

    def __init__(self, gui_inputs, runtime_outputs, figure_frame):

        self.gui_inputs = gui_inputs
        self.runtime_outputs = runtime_outputs
        self.figure_frame = figure_frame
        self.inputs = data_processing.Inputs(gui_inputs, runtime_outputs, from_test=True)
        self.inputs.read_and_load_data()
        self.model_dict = {}
        self.is_last_run_success = False
        self.interventions_to_cost = self.inputs.interventions_to_cost
        self.loglikelihoods = []
        self.outputs_unc = [{'key': 'incidence',
                             'posterior_width': None,
                             'width_multiplier': 2.  # for incidence for ex. Width of Normal posterior relative to CI width in data
                             }]
        self.results = {}
        self.all_parameters_tried = {}
        self.whether_accepted_list = []
        self.accepted_indices = []
        self.rejected_indices = []
        self.results['scenarios'] = {}
        self.solns_for_extraction = ['compartment_soln', 'fraction_soln']
        self.arrays_for_extraction = ['flow_array', 'fraction_array', 'soln_array', 'var_array', 'costs']
        self.optimisation = False
        self.total_funding = 6.6e6  # Total funding for the entire period
        self.acceptable_combinations = []
        self.acceptance_dict = {}
        self.rejection_dict = {}
        self.optimized_combinations = []
        self.optimal_allocation = {}
        self.epi_outputs_to_analyse = ['population', 'incidence', 'prevalence', 'mortality', 'notifications']
        self.epi_outputs = {}
        self.epi_outputs_dict = {}
        self.epi_outputs_integer_dict = {}
        self.epi_outputs_uncertainty = {}
        self.epi_outputs_uncertainty_centiles = {}
        self.cost_outputs = {}
        self.cost_outputs_dict = {}
        self.cost_outputs_integer_dict = {}
        self.cost_outputs_uncertainty = {}
        self.cost_outputs_uncertainty_centiles = {}
        self.uncertainty_percentiles = {}
        self.percentiles = [2.5, 50, 97.5]
        self.accepted_no_burn_in_indices = []
        self.uncertainty_attributes = ['epi_outputs_uncertainty',
                                       'cost_outputs_uncertainty',
                                       'accepted_indices',
                                       'all_parameters_tried',
                                       'whether_accepted_list',
                                       'acceptance_dict',
                                       'accepted_no_burn_in_indices',
                                       'rejection_dict',
                                       'loglikelihoods']

    ##############################################
    ### Master method to run all other methods ###
    ##############################################

    def master_runner(self):

        for scenario in self.gui_inputs['scenarios_to_run']:

            # Name and initialise model
            scenario_name = tool_kit.find_scenario_string_from_number(scenario)
            self.model_dict[scenario_name] = model.ConsolidatedModel(scenario, self.inputs, self.gui_inputs)

            # Sort out times for scenario runs
            if scenario is None:
                self.model_dict[scenario_name].start_time = self.inputs.model_constants['start_time']
            else:
                scenario_start_time_index = \
                    self.model_dict['baseline'].find_time_index(self.inputs.model_constants['recent_time'])
                self.model_dict[scenario_name].start_time = \
                    self.model_dict['baseline'].times[scenario_start_time_index]
                self.model_dict[scenario_name].loaded_compartments = \
                    self.model_dict['baseline'].load_state(scenario_start_time_index)

            # Describe model
            self.add_comment_to_gui_window('Running ' + scenario_name + ' conditions for ' + self.gui_inputs['country']
                                           + ' using point estimates for parameters.')

            # Integrate and add result to outputs object
            self.model_dict[scenario_name].integrate()

        # Model interpretation code - should be flexible and is now used by uncertainty and optimisation
        self.epi_outputs \
            = self.find_epi_outputs(models_to_analyse=self.model_dict,
                                    outputs_to_analyse=self.epi_outputs_to_analyse,
                                    stratifications=[self.model_dict['baseline'].agegroups,
                                                     self.model_dict['baseline'].comorbidities])
        self.find_population_fractions(stratifications=[self.model_dict['baseline'].agegroups,
                                                        self.model_dict['baseline'].comorbidities])
        self.cost_outputs \
            = self.find_cost_outputs(interventions_to_cost=self.model_dict['baseline'].interventions_to_cost)
        adjusted_costs = self.find_adjusted_costs(raw_costs=self.cost_outputs, cost_types=['inflated',
                                                                                           'discounted',
                                                                                           'discounted_inflated'])
        for scenario in self.model_dict:
            self.cost_outputs[scenario].update(adjusted_costs[scenario])

        # If you want some dictionaries based on the lists created above (may not be necessary)
        self.epi_outputs_dict.update(get_output_dicts_from_lists(models_to_analyse=self.model_dict,
                                                                 output_dict_of_lists=self.epi_outputs))
        self.cost_outputs_dict.update(get_output_dicts_from_lists(models_to_analyse=self.model_dict,
                                                                  output_dict_of_lists=self.cost_outputs))

        # If you want some integer-based dictionaries
        self.epi_outputs_integer_dict.update(extract_integer_dicts(self.model_dict, self.epi_outputs_dict))
        self.cost_outputs_integer_dict.update(extract_integer_dicts(self.model_dict, self.cost_outputs_dict))

        if self.gui_inputs['output_uncertainty']:

            # Describe process
            self.add_comment_to_gui_window('Uncertainty analysis commenced')

            # Prepare directory for eventual pickling
            out_dir = 'saved_uncertainty_analyses'
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
            storage_file_names = {}
            for attribute in self.uncertainty_attributes:
                storage_file_names[attribute] = os.path.join(out_dir, attribute + '.pkl')

            # Don't run uncertainty but load a saved simulation
            if self.gui_inputs['pickle_uncertainty'] == 'Load':
                self.add_comment_to_gui_window('Uncertainty results loaded from previous simulation')
                for attribute in self.uncertainty_attributes:
                    setattr(self, attribute,
                            tool_kit.pickle_load(storage_file_names[attribute]))

            # Run uncertainty
            else:
                self.run_uncertainty()

            # Save uncertainty if requested
            if self.gui_inputs['pickle_uncertainty'] == 'Save':
                for attribute in self.uncertainty_attributes:
                    tool_kit.pickle_save(getattr(self, attribute),
                                         storage_file_names[attribute])
                self.add_comment_to_gui_window('Uncertainty results saved to disc')

        # Processing methods that are only required for outputs
        if self.gui_inputs['output_uncertainty']:
            self.epi_outputs_uncertainty_centiles.update(self.find_uncertainty_centiles(self.epi_outputs_uncertainty))
            self.cost_outputs_uncertainty_centiles.update(self.find_uncertainty_centiles(self.cost_outputs_uncertainty))

        if self.optimisation:
            if self.total_funding is None:
                start_cost_index \
                    = tool_kit.find_first_list_element_at_least_value(
                    self.model_dict['baseline'].cost_times,
                    self.model_dict['baseline'].inputs.model_constants['scenario_start_time'])
                self.total_funding = numpy.sum(self.model_dict['baseline'].costs[start_cost_index:, :]) \
                                     / (self.model_dict['baseline'].inputs.model_constants['report_end_time'] -
                                        self.model_dict['baseline'].inputs.model_constants['scenario_start_time'])
            self.run_optimisation()
            self.model_dict['optimised'] = model.ConsolidatedModel(None, self.inputs, self.gui_inputs)
            start_time_index = \
                self.model_dict['baseline'].find_time_index(self.inputs.model_constants['recent_time'])
            self.model_dict['optimised'].start_time = \
                self.model_dict['baseline'].times[start_time_index]
            self.model_dict['optimised'].loaded_compartments = \
                self.model_dict['baseline'].load_state(start_time_index)
            self.model_dict['optimised'].eco_drives_epi = True
            for intervention in self.model_dict['baseline'].interventions_to_cost:
                self.model_dict['optimised'].available_funding[intervention] = self.optimal_allocation[intervention] \
                                                                               * self.total_funding
            self.model_dict['optimised'].distribute_funding_across_years()
            self.model_dict['optimised'].integrate()

    ####################################
    ### Model interpretation methods ###
    ####################################

    def find_epi_outputs(self, models_to_analyse={}, outputs_to_analyse=[], stratifications=[]):

        """
        Method to extract all requested epidemiological outputs from the models. Intended ultimately to be flexible\
        enough for use for analysis of scenarios, uncertainty and optimisation.

        """

        epi_outputs = {}
        for scenario in models_to_analyse:
            epi_outputs[scenario] = {}
            epi_outputs[scenario]['times'] = self.model_dict[scenario].times

            # Unstratified outputs______________________________________________________________________________________
            # Initialise lists
            for output in outputs_to_analyse:
                epi_outputs[scenario][output] = [0.] * len(epi_outputs[scenario]['times'])

            # Population
            if 'population' in outputs_to_analyse:
                for compartment in self.model_dict[scenario].compartments:
                    epi_outputs[scenario]['population'] \
                        = increment_list(self.model_dict[scenario].get_compartment_soln(compartment),
                                         epi_outputs[scenario]['population'])

            # Incidence
            if 'incidence' in outputs_to_analyse:
                for from_label, to_label, rate in self.model_dict[scenario].var_transfer_rate_flows:
                    if 'latent' in from_label and 'active' in to_label:
                        epi_outputs[scenario]['incidence'] \
                            = increment_list(self.model_dict[scenario].get_compartment_soln(from_label) \
                                             * self.model_dict[scenario].get_var_soln(rate) \
                                             / epi_outputs[scenario]['population'] \
                                             * 1e5,
                                             epi_outputs[scenario]['incidence'])
                for from_label, to_label, rate in self.model_dict[scenario].fixed_transfer_rate_flows:
                    if 'latent' in from_label and 'active' in to_label:
                        epi_outputs[scenario]['incidence'] \
                            = increment_list(self.model_dict[scenario].get_compartment_soln(from_label) \
                                             * rate \
                                             / epi_outputs[scenario]['population'] \
                                             * 1e5,
                                             epi_outputs[scenario]['incidence'])

            # Notifications
            if 'notifications' in outputs_to_analyse:
                for from_label, to_label, rate in self.model_dict[scenario].var_transfer_rate_flows:
                    if 'active' in from_label and 'detect' in to_label:
                        epi_outputs[scenario]['notifications'] \
                            = increment_list(self.model_dict[scenario].get_compartment_soln(from_label) \
                                             * self.model_dict[scenario].get_var_soln(rate),
                                             epi_outputs[scenario]['notifications'])

            # Mortality
            if 'mortality' in outputs_to_analyse:
                for from_label, rate in self.model_dict[scenario].fixed_infection_death_rate_flows:
                    # Under-reporting factor included for those deaths not occurring on treatment
                    epi_outputs[scenario]['mortality'] \
                        = increment_list(self.model_dict[scenario].get_compartment_soln(from_label) \
                                         * rate \
                                         * self.model_dict[scenario].params['program_prop_death_reporting'] \
                                         / epi_outputs[scenario]['population'] \
                                         * 1e5, epi_outputs[scenario]['mortality'])
                for from_label, rate in self.model_dict[scenario].var_infection_death_rate_flows:
                    epi_outputs[scenario]['mortality'] \
                        = increment_list(self.model_dict[scenario].get_compartment_soln(from_label) \
                                         * self.model_dict[scenario].get_var_soln(rate) \
                                         / epi_outputs[scenario]['population'] \
                                         * 1e5, epi_outputs[scenario]['mortality'])

            # Prevalence
            if 'prevalence' in outputs_to_analyse:
                for label in self.model_dict[scenario].labels:
                    if 'susceptible' not in label and 'latent' not in label:
                        epi_outputs[scenario]['prevalence'] \
                            = increment_list(self.model_dict[scenario].get_compartment_soln(label) \
                                             / epi_outputs[scenario]['population'] \
                                             * 1e5, epi_outputs[scenario]['prevalence'])

            # Stratified outputs________________________________________________________________________________________
            for stratification in stratifications:
                if len(stratification) > 1:
                    for stratum in stratification:

                        # Initialise lists
                        for output in outputs_to_analyse:
                            epi_outputs[scenario][output + stratum] = [0.] * len(epi_outputs[scenario]['times'])

                        # Population
                        if 'population' in outputs_to_analyse:
                            for compartment in self.model_dict[scenario].compartments:
                                if stratum in compartment:
                                    epi_outputs[scenario]['population' + stratum] \
                                        = increment_list(self.model_dict[scenario].get_compartment_soln(compartment),
                                                         epi_outputs[scenario]['population' + stratum])

                        # Incidence
                        if 'incidence' in outputs_to_analyse:
                            for from_label, to_label, rate in self.model_dict[scenario].var_transfer_rate_flows:
                                if 'latent' in from_label and 'active' in to_label and stratum in label:
                                    epi_outputs[scenario]['incidence' + stratum] \
                                        = increment_list(self.model_dict[scenario].get_compartment_soln(from_label) \
                                                         * self.model_dict[scenario].get_var_soln(rate) \
                                                         / epi_outputs[scenario]['population' + stratum] \
                                                         * 1e5,
                                                         epi_outputs[scenario]['incidence' + stratum])
                            for from_label, to_label, rate in self.model_dict[scenario].fixed_transfer_rate_flows:
                                if 'latent' in from_label and 'active' in to_label and stratum in label:
                                    epi_outputs[scenario]['incidence' + stratum] \
                                        = increment_list(self.model_dict[scenario].get_compartment_soln(from_label) \
                                                         * rate \
                                                         / epi_outputs[scenario]['population' + stratum] \
                                                         * 1e5,
                                                         epi_outputs[scenario]['incidence' + stratum])

                        # Mortality
                        if 'mortality' in outputs_to_analyse:
                            for from_label, rate in self.model_dict[scenario].fixed_infection_death_rate_flows:
                                if stratum in from_label:
                                    # Under-reporting factor included for those deaths not occurring on treatment
                                    epi_outputs[scenario]['mortality' + stratum] \
                                        = increment_list(self.model_dict[scenario].get_compartment_soln(from_label) \
                                                         * rate \
                                                         * self.model_dict[scenario].params['program_prop_death_reporting'] \
                                                         * epi_outputs[scenario]['population' + stratum] \
                                                         * 1e5,
                                                         epi_outputs[scenario]['mortality' + stratum])
                            for from_label, rate in self.model_dict[scenario].var_infection_death_rate_flows:
                                if stratum in from_label:
                                    epi_outputs[scenario]['mortality' + stratum] \
                                        = increment_list(self.model_dict[scenario].get_compartment_soln(from_label) \
                                                         * self.model_dict[scenario].get_var_soln(rate) \
                                                         / epi_outputs[scenario]['population' + stratum] \
                                                         * 1e5,
                                                         epi_outputs[scenario]['mortality' + stratum])

                        # Prevalence
                        if 'prevalence' in outputs_to_analyse:
                            for label in self.model_dict[scenario].labels:
                                if 'susceptible' not in label and 'latent' not in label and stratum in label:
                                    epi_outputs[scenario]['prevalence' + stratum] \
                                        = increment_list(self.model_dict[scenario].get_compartment_soln(label) \
                                                         / epi_outputs[scenario]['population' + stratum] \
                                                         * 1e5, epi_outputs[scenario]['prevalence' + stratum])
        return epi_outputs

    def find_population_fractions(self, stratifications=[]):

        """
        Find the proportion of the population in various stratifications.
        The stratifications must apply to the entire population, so not to be used for strains, etc.

        """

        for scenario in self.model_dict:
            for stratification in stratifications:
                if len(stratification) > 1:
                    for stratum in stratification:
                        self.epi_outputs[scenario]['fraction' + stratum] \
                            = elementwise_list_division(self.epi_outputs[scenario]['population' + stratum],
                                                        self.epi_outputs[scenario]['population'])

    def find_cost_outputs(self, interventions_to_cost=[]):

        """
        Add cost dictionaries to cost_outputs attribute.

        """

        cost_outputs = {}
        for scenario in self.model_dict:
            cost_outputs[scenario] = {}
            cost_outputs[scenario]['times'] = self.model_dict[scenario].cost_times
            for i, intervention in enumerate(interventions_to_cost):
                cost_outputs[scenario]['raw_cost_' + intervention] = self.model_dict[scenario].costs[:, i]
        return cost_outputs

    def find_adjusted_costs(self, raw_costs, cost_types=[]):

        cost_outputs = {}

        # Get some preliminary parameters
        year_current = self.model_dict['baseline'].inputs.model_constants['current_time']
        current_cpi = self.model_dict['baseline'].scaleup_fns['econ_cpi'](year_current)
        discount_rate = self.model_dict['baseline'].params['econ_discount_rate']

        for scenario in self.model_dict:
            cost_outputs[scenario] = {}

            # Work through adjusted costs
            for cost_type in cost_types:
                cost_outputs[scenario][cost_type + '_cost_all_programs'] = []

                # Maybe not ideal that the outer loop is time and the inner interventions here
                # - may reverse at some point.
                for t, time in enumerate(self.cost_outputs[scenario]['times']):
                    cost_all_programs = 0.
                    cpi_time_variant = self.model_dict[scenario].scaleup_fns['econ_cpi'](time)
                    t_into_future = max(0., (time - year_current))
                    for int, intervention in enumerate(self.model_dict[scenario].interventions_to_cost):
                        if t == 0: cost_outputs[scenario][cost_type + '_cost_' + intervention] = []
                        cost_outputs[scenario][cost_type + '_cost_' + intervention].append(
                            autumn.economics.get_adjusted_cost(raw_costs[scenario]['raw_cost_' + intervention][t],
                                                               cost_type, current_cpi, cpi_time_variant, discount_rate,
                                                               t_into_future))
                        cost_all_programs += cost_outputs[scenario][cost_type + '_cost_' + intervention][-1]
                    cost_outputs[scenario][cost_type + '_cost_all_programs'].append(cost_all_programs)
        return cost_outputs

    def find_uncertainty_centiles(self, full_uncertainty_outputs):

        """
        Find percentiles from uncertainty dictionaries.

        Modifies:
            self.percentiles: Adds all the required percentiles to this dictionary.

        """

        # Loop through scenarios and outputs
        uncertainty_percentiles = {}
        self.accepted_no_burn_in_indices \
            = [i for i in self.accepted_indices if i >= self.gui_inputs['burn_in_runs']]

        for scenario in full_uncertainty_outputs:
            uncertainty_percentiles[scenario] = {}
            for output in full_uncertainty_outputs[scenario]:
                if output != 'times':
                    # Code to deal with the fact that we are currently saving all baseline runs but only accepted
                    # scenario runs:
                    if scenario == 'baseline':
                        matrix_to_analyse = full_uncertainty_outputs[scenario][output][
                                            self.accepted_no_burn_in_indices, :]
                    else:
                        matrix_to_analyse = full_uncertainty_outputs[scenario][output]

                    # Find the actual centiles
                    uncertainty_percentiles[scenario][output] \
                        = numpy.percentile(matrix_to_analyse,
                                           self.percentiles,
                                           axis=0)

        # Return result to make usable in other situations
        return uncertainty_percentiles

    ###########################
    ### Uncertainty methods ###
    ###########################

    def run_uncertainty(self):

        """
        Main method to run all the uncertainty processes.

        """

        # If not doing an adaptive search, only need to start with a single parameter set
        if self.gui_inputs['adaptive_uncertainty']:
            n_candidates = 1
        else:
            n_candidates = self.gui_inputs['uncertainty_runs'] * 10

        # Define an initial set of parameter candidates only
        param_candidates = generate_candidates(n_candidates, self.inputs.param_ranges_unc)
        normal_char = self.get_normal_char()

        # Prepare for uncertainty loop
        for param_dict in self.inputs.param_ranges_unc:
            self.all_parameters_tried[param_dict['key']] = []
        n_accepted = 0
        i_candidates = 0
        run = 0
        prev_log_likelihood = -1e10
        params = []
        self.results['uncertainty'] = {}

        for param_dict in self.inputs.param_ranges_unc:
            self.acceptance_dict[param_dict['key']] = {}

        for param_dict in self.inputs.param_ranges_unc:
            self.rejection_dict[param_dict['key']] = {}
            self.rejection_dict[param_dict['key']][n_accepted] = []

        # Until a sufficient number of parameters are accepted
        while n_accepted < self.gui_inputs['uncertainty_runs']:

            # Set timer
            start_timer_run = datetime.datetime.now()

            # Update parameters
            new_params = []
            if self.gui_inputs['adaptive_uncertainty']:
                if i_candidates == 0:
                    new_params = []
                    for param_dict in self.inputs.param_ranges_unc:
                        new_params.append(param_candidates[param_dict['key']][run])
                        params.append(param_candidates[param_dict['key']][run])
                else:
                    new_params = self.update_params(params)
            else:
                for param_dict in self.inputs.param_ranges_unc:
                    new_params.append(param_candidates[param_dict['key']][run])

            # Run the baseline integration
            # (includes checking parameters, setting parameters and recording success/failure of run)
            self.run_with_params(new_params, model_object='baseline')

            # Now storing regardless of acceptance
            if self.is_last_run_success:

                # Storage
                epi_outputs = self.find_epi_outputs(['baseline'],
                                                    outputs_to_analyse=self.epi_outputs_to_analyse)
                cost_outputs \
                    = self.find_cost_outputs(interventions_to_cost=self.model_dict['baseline'].interventions_to_cost)
                adjusted_costs = self.find_adjusted_costs(raw_costs=cost_outputs, cost_types=['inflated',
                                                                                              'discounted',
                                                                                              'discounted_inflated'])
                cost_outputs['baseline'].update(adjusted_costs['baseline'])
                self.store_uncertainty('baseline',
                                       epi_outputs,
                                       cost_outputs,
                                       epi_outputs_to_analyse=self.epi_outputs_to_analyse)
                integer_dictionary \
                    = extract_integer_dicts(['baseline'],
                                            get_output_dicts_from_lists(models_to_analyse=['baseline'],
                                                                        output_dict_of_lists=epi_outputs))

                # Calculate prior
                prior_log_likelihood = 0.
                for p, param_dict in enumerate(self.inputs.param_ranges_unc):
                    param_val = new_params[p]
                    self.all_parameters_tried[param_dict['key']].append(new_params[p])

                    # Calculate the density of param_val
                    bound_low, bound_high = param_dict['bounds'][0], param_dict['bounds'][1]

                    # Normalise value and find log of PDF from beta distribution
                    if param_dict['distribution'] == 'beta':
                        prior_log_likelihood \
                            += beta.logpdf((param_val - bound_low) / (bound_high - bound_low),
                                           2., 2.)

                    # Find log of PDF from uniform distribution
                    elif param_dict['distribution'] == 'uniform':
                        prior_log_likelihood \
                            += numpy.log(1. / (bound_high - bound_low))

                # Calculate posterior
                posterior_log_likelihood = 0.
                for output_dict in self.outputs_unc:

                    # The GTB values for the output of interest
                    working_output_dictionary = normal_char[output_dict['key']]
                    for year in working_output_dictionary.keys():
                        model_result_for_output \
                            = integer_dictionary['baseline']['incidence'][year]
                        mu, sd = working_output_dictionary[year][0], working_output_dictionary[year][1]
                        posterior_log_likelihood += norm.logpdf(model_result_for_output, mu, sd)

                # Sum for overall likelihood of run
                log_likelihood = prior_log_likelihood + posterior_log_likelihood

                # Determine acceptance
                if log_likelihood >= prev_log_likelihood:
                    accepted = 1
                else:
                    accepted = numpy.random.binomial(n=1, p=numpy.exp(log_likelihood - prev_log_likelihood))
                self.loglikelihoods.append(log_likelihood)

                # Record some information for all runs
                if not bool(accepted):
                    self.whether_accepted_list.append(False)
                    for p, param_dict in enumerate(self.inputs.param_ranges_unc):
                        self.rejection_dict[param_dict['key']][n_accepted].append(new_params[p])
                    self.rejected_indices += [run]
                else:
                    self.whether_accepted_list.append(True)
                    self.accepted_indices += [run]
                    n_accepted += 1
                    for p, param_dict in enumerate(self.inputs.param_ranges_unc):
                        self.acceptance_dict[param_dict['key']][n_accepted] = new_params[p]
                        self.rejection_dict[param_dict['key']][n_accepted] = []

                    # Update likelihood and parameter set for next run
                    prev_log_likelihood = log_likelihood
                    params = new_params

                    # Run scenarios other than baseline and store uncertainty - currently only if accepted
                    for scenario in self.gui_inputs['scenarios_to_run']:
                        scenario_name = tool_kit.find_scenario_string_from_number(scenario)
                        if scenario is not None:
                            scenario_start_time_index = \
                                self.model_dict['baseline'].find_time_index(self.inputs.model_constants['recent_time'])
                            self.model_dict[scenario_name].start_time = \
                                self.model_dict['baseline'].times[scenario_start_time_index]
                            self.model_dict[scenario_name].loaded_compartments = \
                                self.model_dict['baseline'].load_state(scenario_start_time_index)
                            self.run_with_params(new_params, model_object=scenario_name)

                            # Storage
                            epi_outputs = self.find_epi_outputs([scenario_name],
                                                                outputs_to_analyse=self.epi_outputs_to_analyse)
                            cost_outputs \
                                = self.find_cost_outputs(
                                interventions_to_cost=self.model_dict[scenario_name].interventions_to_cost)
                            adjusted_costs = self.find_adjusted_costs(raw_costs=cost_outputs,
                                                                      cost_types=['inflated',
                                                                                  'discounted',
                                                                                  'discounted_inflated'])
                            cost_outputs[scenario_name].update(adjusted_costs['baseline'])
                            self.store_uncertainty(scenario_name,
                                                   epi_outputs,
                                                   cost_outputs,
                                                   epi_outputs_to_analyse=self.epi_outputs_to_analyse)

                i_candidates += 1
                run += 1

            self.plot_progressive_parameters(from_runner=True)

            # Generate more candidates if required
            if not self.gui_inputs['adaptive_uncertainty'] and run >= len(param_candidates.keys()):
                param_candidates = generate_candidates(n_candidates, self.inputs.param_ranges_unc)
                run = 0
            self.add_comment_to_gui_window(str(n_accepted) + ' accepted / ' + str(i_candidates) +
                                           ' candidates. Running time: '
                                           + str(datetime.datetime.now() - start_timer_run))

    def set_model_with_params(self, param_dict, model_object='baseline'):

        """
        Populates baseline model with params from uncertainty calculations.

        Args:
            param_dict: Dictionary of the parameters to be set within the model (keys parameter name strings and values
                parameter values).

        """

        n_set = 0
        for key in param_dict:
            if key in self.model_dict[model_object].params:
                n_set += 1
                self.model_dict[model_object].set_parameter(key, param_dict[key])
            else:
                raise ValueError("%s not in model_object params" % key)

    def convert_param_list_to_dict(self, params):

        """
        Extract parameters from list into dictionary that can be used for setting in the model
        through the set_model_with_params method.

        Args:
            params: The parameter names for extraction.

        Returns:
            param_dict: The dictionary returned in appropriate format.

        """

        param_dict = {}

        for names, vals in zip(self.inputs.param_ranges_unc, params):
            param_dict[names['key']] = vals

        return param_dict

    def get_normal_char(self):

        """
        Define the characteristics (mean and standard deviation) of the normal distribution for model outputs
        (incidence, mortality).

        Returns:
            normal_char: Dictionary with keys outputs and values dictionaries. Sub-dictionaries have keys years
                and values lists, with first element of list means and second standard deviations.

        """

        # Dictionary storing the characteristics of the normal distributions
        normal_char = {}
        for output_dict in self.inputs.outputs_unc:
            normal_char[output_dict['key']] = {}

            # Mortality
            if output_dict['key'] == 'mortality':
                sd = output_dict['posterior_width'] / (2.0 * 1.96)
                for year in self.inputs.data_to_fit[output_dict['key']].keys():
                    mu = self.inputs.data_to_fit[output_dict['key']][year]
                    normal_char[output_dict['key']][year] = [mu, sd]

            # Incidence
            elif output_dict['key'] == 'incidence':
                for year in self.inputs.data_to_fit[output_dict['key']].keys():
                    low = self.inputs.data_to_fit['incidence_low'][year]
                    high = self.inputs.data_to_fit['incidence_high'][year]
                    sd = output_dict['width_multiplier'] * (high - low) / (2.0 * 1.96)
                    mu = (high + low) / 2.
                    normal_char[output_dict['key']][year] = [mu, sd]

        return normal_char

    def update_params(self, old_params):

        """
        Update all the parameter values being used in the uncertainty analysis.

        Args:
            old_params:

        Returns:
            new_params: The new parameters to be used in the next model run.

        """

        new_params = []

        # Iterate through the parameters being used
        for p, param_dict in enumerate(self.inputs.param_ranges_unc):
            bounds = param_dict['bounds']
            sd = self.gui_inputs['search_width'] * (bounds[1] - bounds[0]) / (2.0 * 1.96)
            random = -100.

            # Search for new parameters
            while random < bounds[0] or random > bounds[1]:
                random = norm.rvs(loc=old_params[p], scale=sd, size=1)

            # Add them to the dictionary
            new_params.append(random[0])

        return new_params

    def run_with_params(self, params, model_object='baseline'):

        """
        Integrate the model with the proposed parameter set.

        Args:
            params: The parameters to be set in the model.

        """

        # Check whether parameter values are acceptable
        for p, param in enumerate(params):

            # Whether the parameter value is valid
            if not is_positive_definite(param):
                print 'Warning: parameter%d=%f is invalid for model' % (p, param)
                self.is_last_run_success = False
                return
            bounds = self.inputs.param_ranges_unc[p]['bounds']

            # Whether the parameter value is within acceptable ranges
            if (param < bounds[0]) or (param > bounds[1]):
                # print "Warning: parameter%d=%f is outside of the allowed bounds" % (p, param)
                self.is_last_run_success = False
                return

        param_dict = self.convert_param_list_to_dict(params)

        self.set_model_with_params(param_dict, model_object)
        self.is_last_run_success = True
        try:
            self.model_dict[model_object].integrate()
        except:
            print "Warning: parameters=%s failed with model" % params
            self.is_last_run_success = False

    def store_uncertainty(self, scenario, epi_results, cost_outputs,
                          epi_outputs_to_analyse=['population', 'incidence']):

        """
        Add model results from one uncertainty run to the appropriate outputs dictionary.

        Args:
            scenario: The scenario being run.
            epi_results: The results from that model run.
            epi_outputs_to_analyse: The epidemiological outputs of interest.

        Updates:
            self.epi_outputs_uncertainty

        """

        # Create first column of dictionaries
        if scenario not in self.epi_outputs_uncertainty:
            self.epi_outputs_uncertainty[scenario] = {'times': self.epi_outputs[scenario]['times']}
            self.cost_outputs_uncertainty[scenario] = {'times': self.cost_outputs[scenario]['times']}
            for output in epi_outputs_to_analyse:
                self.epi_outputs_uncertainty[scenario][output] = epi_results[scenario][output]
            for output in cost_outputs[scenario]:
                self.cost_outputs_uncertainty[scenario][output] = cost_outputs[scenario][output]

        # Add additional columns to uncertainty output dictionaries
        else:
            for output in epi_outputs_to_analyse:
                self.epi_outputs_uncertainty[scenario][output] \
                    = numpy.vstack([self.epi_outputs_uncertainty[scenario][output],
                                    epi_results[scenario][output]])
            for output in cost_outputs[scenario]:
                self.cost_outputs_uncertainty[scenario][output] \
                    = numpy.vstack([self.cost_outputs_uncertainty[scenario][output],
                                    cost_outputs[scenario][output]])

    ############################
    ### Optimisation methods ###
    ############################

    def get_acceptable_combinations(self):
        """
        determines the acceptable combinations of interventions according to the related starting costs and given a total
        ammount of funding
        populates the attribute 'acceptable_combinations' of model_runner.
        """
        n_interventions = len(self.model_dict['baseline'].interventions_to_cost)
        full_set = range(n_interventions)
        canditate_combinations = list(itertools.chain.from_iterable(itertools.combinations(full_set, n) \
                                                                    for n in range(n_interventions + 1)[1:]))

        for combi in canditate_combinations:
            total_start_cost = 0
            for ind_intervention in combi:
                if self.model_dict['baseline'].intervention_startdates[self.model_dict['baseline'].interventions_to_cost[ind_intervention]] is None: # start-up costs apply
                    total_start_cost += self.model_dict['baseline'].inputs.model_constants['econ_startupcost_' + \
                                                self.model_dict['baseline'].interventions_to_cost[ind_intervention]]
            if total_start_cost <= self.total_funding:
                self.acceptable_combinations.append(combi)

    def run_optimisation(self):

        print 'Start optimisation'

        # Initialise a new model that will be run from 'recent_time' for optimisation
        self.model_dict['optimisation'] = model.ConsolidatedModel(None, self.inputs, self.gui_inputs)
        start_time_index = \
            self.model_dict['baseline'].find_time_index(self.inputs.model_constants['recent_time'])
        self.model_dict['optimisation'].start_time = \
            self.model_dict['baseline'].times[start_time_index]
        self.model_dict['optimisation'].loaded_compartments = \
            self.model_dict['baseline'].load_state(start_time_index)

        self.model_dict['optimisation'].eco_drives_epi = True

        self.get_acceptable_combinations()

        for combi in self.acceptable_combinations: # for each acceptable combination of interventions
            # prepare storage
            dict_optimized_combi = {'interventions': [], 'distribution': [], 'objective': None}

            for i in range(len(combi)):
                intervention = self.model_dict['baseline'].interventions_to_cost[combi[i]]
                dict_optimized_combi['interventions'].append(intervention)

            print "Optimization of the distribution across: "
            print dict_optimized_combi['interventions']

            # function to minimize: incidence in 2035
            def func(x):
                """
                Args:
                    x: defines the resource allocation (as absolute funding over the total period (2015 - 2035))
                Returns:
                    x has same length as combi
                    predicted incidence for 2035
                """
                #initialise funding at 0 for each intervention
                for intervention in self.model_dict['baseline'].interventions_to_cost:
                    self.model_dict['optimisation'].available_funding[intervention] = 0.

                # input values from x
                for i in range(len(x)):
                    intervention = self.model_dict['baseline'].interventions_to_cost[combi[i]]
                    self.model_dict['optimisation'].available_funding[intervention] = x[i] * self.total_funding
                self.model_dict['optimisation'].distribute_funding_across_years()
                self.model_dict['optimisation'].integrate()
                output_list = self.find_epi_outputs(['optimisation'],
                                                    outputs_to_analyse=['population',
                                                                        'incidence'])
                return output_list['optimisation']['incidence'][-1]

            if len(combi) == 1: # the distribution result is obvious
                dict_optimized_combi['distribution'] = [1.]
                dict_optimized_combi['objective'] = func([1.])
            else:
                # initial guess
                x_0 = []
                for i in range(len(combi)):
                    x_0.append(1./len(combi))

                # Equality constraint:  Sum(x)=Total funding
                cons = [{'type': 'ineq',
                         'fun': lambda x: 1 - sum(x),  # if x is proportion
                         'jac': lambda x: -numpy.ones(len(x))}]
                bnds = []
                for i in range(len(combi)):
                    minimal_allocation = 0.
                    if self.model_dict['baseline'].intervention_startdates[
                        self.model_dict['baseline'].interventions_to_cost[
                            combi[i]]] is None:  # start-up costs apply
                        minimal_allocation = self.model_dict['baseline'].inputs.model_constants['econ_startupcost_' + \
                                                self.model_dict['baseline'].interventions_to_cost[combi[i]]] / self.total_funding
                    bnds.append((minimal_allocation, 1.0))
                # Ready to run optimisation
                res = minimize(func, x_0, jac=None, bounds=bnds, constraints=cons, method='SLSQP',
                               options={'disp': True, 'ftol': 0.5})
                dict_optimized_combi['distribution'] = res.x
                dict_optimized_combi['objective'] = res.fun

            self.optimized_combinations.append(dict_optimized_combi)

        # Update self.optimal_allocation
        best_dict = {}
        best_obj = 1e10
        for i, dict_opti in enumerate(self.optimized_combinations):
            if dict_opti['objective'] < best_obj:
                best_dict = dict_opti
                best_obj = dict_opti['objective']

        for intervention in self.model_dict['baseline'].interventions_to_cost:
            self.optimal_allocation[intervention] = 0.

        for i, intervention in enumerate(best_dict['interventions']):
            self.optimal_allocation[intervention] = best_dict['distribution'][i]

    ###########################
    ### GUI-related methods ###
    ###########################

    def add_comment_to_gui_window(self, comment):

        self.runtime_outputs.insert(END, comment + '\n')
        self.runtime_outputs.see(END)

    def plot_progressive_parameters(self, from_runner=True, input_figure=None):

        # Initialise plotting
        if from_runner:
            param_tracking_figure = plt.Figure()
            parameter_plots = FigureCanvasTkAgg(param_tracking_figure, master=self.figure_frame)

        else:
            param_tracking_figure = input_figure

        subplot_grid = outputs.find_subplot_numbers(len(self.all_parameters_tried))

        # Cycle through parameters with one subplot for each parameter
        for p, param in enumerate(self.all_parameters_tried):

            # Extract accepted params from all tried params
            accepted_params = list(p for p, a in zip(self.all_parameters_tried[param], self.whether_accepted_list) if a)

            # Plot
            ax = param_tracking_figure.add_subplot(subplot_grid[0], subplot_grid[1], p + 1)
            ax.plot(range(1, len(accepted_params) + 1), accepted_params, linewidth=2, marker='o', markersize=4,
                    mec='b', mfc='b')
            ax.set_xlim((1., len(self.accepted_indices) + 1))

            # Find the y-limits from the parameter bounds and the parameter values tried
            for param_number in range(len(self.inputs.param_ranges_unc)):
                if self.inputs.param_ranges_unc[param_number]['key'] == param:
                    bounds = self.inputs.param_ranges_unc[param_number]['bounds']
            ylim_margins = .1
            min_ylimit = min(accepted_params + [bounds[0]])
            max_ylimit = max(accepted_params + [bounds[1]])
            ax.set_ylim((min_ylimit * (1 - ylim_margins), max_ylimit * (1 + ylim_margins)))

            # Indicate the prior bounds
            ax.plot([1, len(self.accepted_indices) + 1], [min_ylimit, min_ylimit], color='0.8')
            ax.plot([1, len(self.accepted_indices) + 1], [max_ylimit, max_ylimit], color='0.8')

            # Plot rejected parameters
            for run, rejected_params in self.rejection_dict[param].items():
                if self.rejection_dict[param][run]:
                    ax.plot([run + 1] * len(rejected_params), rejected_params, marker='o', linestyle='None',
                            mec='0.5', mfc='0.5', markersize=3)
                    for r in range(len(rejected_params)):
                        ax.plot([run, run + 1], [self.acceptance_dict[param][run], rejected_params[r]], color='0.5',
                                linestyle='--')

            # Label
            ax.set_title(tool_kit.find_title_from_dictionary(param))
            if p > len(self.all_parameters_tried) - subplot_grid[1] - 1:
                ax.set_xlabel('Accepted runs')

            if from_runner:

                # Output to GUI window
                parameter_plots.show()
                parameter_plots.draw()
                parameter_plots.get_tk_widget().grid(row=1, column=1)

        if not from_runner:
            return param_tracking_figure
