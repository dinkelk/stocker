import copy
import statistics
import astropy.stats
import numpy as np
import abc

#
# Value formatting functions:
#
def _format_currency(value):
  return "${:,.2f}".format(value)

def _format_percentage(decimal):
  return ("%0.1f%%" % (decimal*100.0))

#
# Inflation helper functions:
#
def present_value(value, year, rate=0.035):
  assert year >= 0, "Year cannot be negative."
  return value*(1/(1 + rate)**year)

def future_value(value, year, rate=0.035):
  assert year >= 0, "Year cannot be negative."
  return value*(1 + rate)**year

#
# Define a positition
#
# A position consists of an named allocation to a specific 
# investment. The investment is assigned a projected average
# return and standard deviation, such that its future performance
# can be simulated:
class Position(object):
  # ave return and std are in percentage per time unit:
  def __init__(self, name, ave_return, std_dev, value=0.0):
    self.name = name
    self.value = float(value)
    self.ave_return = float(ave_return)/100.0
    self.std_dev = float(std_dev)/100.0

  def trade(self, amount):
    self.value += float(amount)
    if self.value < 0.0:
      self.value = 0.0

  # Simulate 1 time unit:
  def simulate(self):
    # Calculate return as ave return + normal distribution of std deviation:
    this_return = 0.0
    if self.value > 0.0:
      this_return += self.ave_return*self.value
      if self.std_dev > 0.0:
        this_return += np.random.normal(0, self.value*self.std_dev)
    self.value += this_return
    if self.value < 0.0:
      self.value = 0.0

  def __repr__(self):
    return _format_currency(self.value)

  def __str__(self):
    return self.__repr__()

#
# Define the historical asset class return and risk:
#
# Data sources: Ibbotson Associates, MSCI, Standard & Poor’s, World Gold Council, BP.com,
# US Energy Information Administration, Robert Shiller Online, MIT Center For Real Estate, Yahoo Finance.
# Calculations are based on the long-term historical performance of asset classes using a combination of
# indexes and ETFs as proxies: S&P 500, MSCI EAFE and MSCI ACWI ex-US, 10 Year U.S. Treasuries, S&P/
# Citigroup International Treasury Bond Ex-US, 30 Day T-Bills, as well as IEF, IGOV, VNQ, IAU, and DBC. Prior
# to 2007, the Alternative asset class is represented by a hypothetical index of 50% real estate and a 50%
# gold/oil combination. Each year thereafter it is comprised of 50% real estate and a 50% blend of diversified
# commodities and gold ETFs. Portfolio standard deviation, correlation, and expected returns are based on
# average annual performance included in source data: domestic equities since 1926, international equities since
# 1970, domestic fixed since 1926, international fixed since 2002, alternatives since 1970 and cash since 1926.
#
def _predefined_position(name, ave_return, std_dev):
  def inner(value=0.0):
    return Position(name, ave_return, std_dev, value)
  return inner

US_Stocks = _predefined_position("Domestic Equities", ave_return=10.2, std_dev=19.8)
International_Stocks = _predefined_position("International Equities", ave_return=9.2, std_dev=22.1)
US_Bonds = _predefined_position("Domestic Fixed Income", ave_return=5.3, std_dev=5.8)
International_Bonds = _predefined_position("International Fixed Income", ave_return=5.5, std_dev=9.1)
Alternatives = _predefined_position("Alternatives", ave_return=6.1, std_dev=16.1)
Cash = _predefined_position("Cash", ave_return=3.4, std_dev=3.1)

#
# More historical returns from https://www.bogleheads.org/wiki/Historical_and_expected_returns:
#
# Series	               Geometric Mean	Arithmetic Mean	Standard Deviation
# Large Company Stocks	                10.4%	          12.3%	             20.2%
# Small Company Stocks	                12.6%	          17.4%	             32.9%
# Long-term Corporate Bonds	         5.9%	           6.2%	              8.5%
# Long-term Government Bonds	         5.3%	           5.5%	              5.7%
# U.S. Treasury Bills	                 3.7%	           3.8%	              3.1%
#
Large_Cap_Stocks = _predefined_position("Large Company Stocks", ave_return=10.4, std_dev=20.2)
Small_Cap_Stocks = _predefined_position("Small Company Stocks", ave_return=12.6, std_dev=32.9)
Long_Term_Corp_Bonds = _predefined_position("Long-term Corporate Bonds", ave_return=5.9, std_dev=8.5)
Long_Term_Gov_Bonds = _predefined_position("Long-term Government Bonds", ave_return=5.3, std_dev=5.7)
US_Treasury_Bills = _predefined_position("U.S. Treasury Bills", ave_return=3.8, std_dev=3.1)

#
# Define a portfolio:
#
# A portfollio is a collection of positions (see above) given
# a specific weighting to each. A portfolio can be rebalanced
# at any time to readjust the amount of value stored in each
# position.
class Portfolio(object):
  def __init__(self, name, positions, weights, value=0.0):
    self.name = name
    self.positions = positions
    self.set_weights(weights)

    assert value >= 0.0, "Initial value must be positive or zero."

    self.trade(value)

  def set_weights(self, weights):
    assert len(weights) == len(self.positions), "The number of weights must equal the number of positions"
    assert all([w >= 0.0 for w in weights]), "All weights must be positive: " + str(weights)
    self.total_weight = float(sum(weights))
    self.weights = [float(w)/self.total_weight for w in weights]

  # Simulate 1 time unit:
  def simulate(self):
    for position in self.positions:
      position.simulate()

  def value(self):
    return sum([p.value for p in self.positions])

  def trade(self, amount):
    for w, p in zip(self.weights, self.positions):
      p.trade(amount*w)

  def rebalance(self, new_weights=None):
    value = self.value()

    # If new weights were provided, apply those prior to
    # rebalancing:
    if new_weights:
      self.set_weights(new_weights)

    # Rebalance:
    if value > 0.0:
      for w, p in zip(self.weights, self.positions):
        correction = w * value - p.value
        p.trade(correction)

    new_value = self.value()

    # Make sure rebalancing didn't change total balance:
    assert new_value < value + 1.0, str(new_value) + " < " + str(value) + " + 1.0"
    assert new_value > value - 1.0, str(new_value) + " > " + str(value) + " - 1.0"

  def __repr__(self):
    value = self.value()
    template = "{0:<30}|{1:>12}|{2:>15}"
    strn = "-----------------------------------------------------------\n"
    strn += template.format("Position", "Allocation ", "Value") + "\n"
    strn += "-----------------------------------------------------------\n"
    for w, p in zip(self.weights, self.positions):
      if value > 0.0:
        strn += template.format(p.name, _format_percentage(p.value/value), str(p)) + "\n"
      else:
        strn += template.format(p.name, _format_percentage(w), str(p)) + "\n"
    strn += "-----------------------------------------------------------\n"
    strn += template.format("Total", "100.0% ", _format_currency(value)) + "\n"
    strn += "-----------------------------------------------------------\n"
    return strn

  def __str__(self):
    return self.__repr__()

# 
# Define some common potfolios:
#
def _predefined_portfolio(name, positions, weights):
  def inner(value=0.0):
    return Portfolio(name, positions, weights, value)
  return inner
# All Stocks portfolio 70% US, 30% International
All_Stocks = _predefined_portfolio(name="All Stocks", positions=[US_Stocks(), International_Stocks()], weights=[7, 3])
# All Bonds portfolio 70% US, 30% International
All_Bonds = _predefined_portfolio(name="All Bonds", positions=[US_Bonds(), International_Bonds()], weights=[7, 3])
# All Stocks portfolio 100% US
All_US_Stocks = _predefined_portfolio(name="All Stocks", positions=[US_Stocks()], weights=[1])
# All Bonds portfolio 100% US
All_US_Bonds = _predefined_portfolio(name="All Bonds", positions=[US_Bonds()], weights=[1])
# 50/50 Stocks and bonds with 70% US and 30% International
Fifty_Fifty = _predefined_portfolio(name="All Bonds", positions=[US_Stocks(), International_Stocks(), US_Bonds(), International_Bonds()], weights=[7, 3, 7, 3])
# 60/40 Stocks and bonds with 70% US and 30% International
Sixty_Forty = _predefined_portfolio(name="All Bonds", positions=[US_Stocks(), International_Stocks(), US_Bonds(), International_Bonds()], weights=[7*6, 3*6, 7*4, 3*4])

#
# Define Scenarios:
#
# Each scenario class defines a savings scenario which has specific
# parameters and behavior associated with a specific saving strategy.

# Scenario base class:
# This provides common functionality for all scenarios:
class _Scenario_Base(metaclass=abc.ABCMeta):
  def __init__(self, name, num_years, portfolio, inflation_rate_perc=3.5, rebalance=True):
    self.name = name
    self.portfolio = copy.deepcopy(portfolio)
    self.num_years = int(num_years)
    self.inflation_rate = float(inflation_rate_perc)/100.0
    self.rebalance = rebalance
    self.history = [copy.deepcopy(portfolio)]
    self.uncorrected_history = [copy.deepcopy(portfolio)]
    self.returns = []
    self.uncorrected_returns = []

  def reset(self):
    self.portfolio = copy.deepcopy(self.history[0])
    self.history = [copy.deepcopy(self.portfolio)]
    self.uncorrected_history = [copy.deepcopy(self.portfolio)]
    self.returns = []
    self.uncorrected_returns = []

  # Run the entire scenario:
  @abc.abstractmethod
  def run(self): pass

  # Helper method to simulate a single time step:
  def _run(self, start_year=0):
    # Get current value:
    uncorrected_prev_value = self.portfolio.value()

    # Simulate a year of growth:
    self.portfolio.simulate()

    # Get the new value:
    uncorrected_value = self.portfolio.value()

    # Rebalance portfolio to match original allocation weights:
    if self.rebalance:
      self.portfolio.rebalance()

    # Correct the values in the portfolio for inflation to report
    # numbers in today's dollars:
    # Using the present value function to calculate what our money is actually worth with
    # inflation: http://financeformulas.net/present_value.html
    year = len(self.history) + start_year
    assert year >= 0, "Year cannot be negative."
    corrected_value = present_value(uncorrected_value, year, self.inflation_rate)
    correction = corrected_value - uncorrected_value
    p = copy.deepcopy(self.portfolio)
    p.trade(correction)

    # Save the corrected portfolio history:
    self.history.append(p)
    corrected_prev_value = uncorrected_prev_value
    if year > 0:
      corrected_prev_value = uncorrected_prev_value*(1/(1 + self.inflation_rate)**(year-1))
    if corrected_prev_value > 0.0:
      return_perc = (corrected_value - corrected_prev_value)/corrected_prev_value
      self.returns.append(return_perc)
    else:
      self.returns.append(0.0)

    # Save the uncorrected porfolio in the history:
    self.uncorrected_history.append(copy.deepcopy(self.portfolio))
    if uncorrected_prev_value > 0.0:
      return_perc = (uncorrected_value - uncorrected_prev_value)/uncorrected_prev_value
      self.uncorrected_returns.append(return_perc)
    else:
      self.uncorrected_returns.append(0.0)

  def plot(self, figure=None, color='steelblue', label="Value", smooth=False):
    import matplotlib.pyplot as plt
    from scipy.signal import savgol_filter

    # Find the median and 10th percentile data sets:
    data = [p.value()/1000000.0 for p in self.history]
    # Plot data:
    if figure:
      plt.figure(figure.number)
    else:
      plt.figure()
    if smooth:
      amount = min(9, int(len(data)/5))
      amount = int(amount/2) * 2 + 1
      order = 3
      if order >= amount:
        order = amount - 1
      data = savgol_filter(data, amount, order)
    plt.plot(data, lw=1, color=color, label=label + ' (' + _format_currency(self.history[-1].value()) + ')')
    plt.fill_between(list(range(len(data))), data, interpolate=False, facecolor=color, alpha=0.5)
    plt.ylim(bottom=0.0) 
    plt.xlim(0, len(data) - 1)
    plt.xlabel('Year')
    plt.ylabel('Portfolio Value ($M)')
    plt.title('Portfolio Value Over Time')
    plt.legend()
    plt.grid(True)

  def results(self):
    strn = "'" + self.name + "' Scenario:\n"
    strn += "Portfolio: " + self.portfolio.name + " Portfolio\n"
    strn += "Duration: " + str(len(self.history)-1) + " years\n"
    strn += "Inflation Rate: " + _format_percentage(self.inflation_rate) + "\n" 
    strn += "Annual Rebalancing: " + ("Yes" if self.rebalance else "No") + "\n" 
    strn += "\n"
    strn += self.portfolio.name + " Portfolio Start:\n"
    strn += str(self.history[0])
    strn += "\n"
    # strn += self.portfolio.name + " Portfolio End:\n"
    # strn += str(self.uncorrected_history[-1])
    # strn += "\n"
    strn += self.portfolio.name + " Portfolio End (Inflation Corrected at " + _format_percentage(self.inflation_rate) + "):\n" 
    strn += str(self.history[-1])
    strn += "\n"
    strn += "Raw Metrics:\n"
    strn += "Ave Return: " + _format_percentage(sum(self.uncorrected_returns)/len(self.uncorrected_returns)) + "\n"
    strn += "Best Return: " + _format_percentage(max(self.uncorrected_returns)) + " (year " + str(self.returns.index(max(self.returns))) + ")\n"
    strn += "Worst Return: " + _format_percentage(min(self.uncorrected_returns)) + " (year " + str(self.returns.index(min(self.returns))) + ")\n"
    strn += "\n"
    strn += "Inflation Corrected Metrics at " + _format_percentage(self.inflation_rate) + ":\n" 
    strn += "Ave Return: " + _format_percentage(sum(self.returns)/len(self.returns)) + "\n"
    strn += "Best Return: " + _format_percentage(max(self.returns)) + " (year " + str(self.returns.index(max(self.returns))) + ")\n"
    strn += "Worst Return: " + _format_percentage(min(self.returns)) + " (year " + str(self.returns.index(min(self.returns))) + ")\n"
    return strn

# Standard scenario:
# This scenario allows a single portfolio to build for a configurable
# number of years. Parameters are provided to account for inflation,
# rebalnce the portfolio yearly, add/subtract a static value yearly,
# and to adjust the addition/subtraction by some percentage over time.
# An "end_weights" field also exists to provide a linear transition 
# from the portfolio's weightings to the weighting of the "end_weights"
# field over the duration of the scenario. This field can be used to
# simulate an age-based portfolio, transferring assets from stocks to
# bonds as the investment ages.
# This simple strategy should work for many real life savings projections.
class Scenario(_Scenario_Base):
  def __init__(self, name, portfolio, num_years, inflation_rate_perc=3.5, rebalance=True, annual_contribution=0.0, annual_contribution_increase_perc=0.0, end_weights=None):
    self.addition = annual_contribution
    self.addition_increase = annual_contribution_increase_perc/100.0
    self.end_weights = end_weights
    self.slopes = None
    self.start_weights = None
    if self.end_weights:
      assert len(end_weights) == len(portfolio.weights), "Length of end weight vector and length of start weights in portfolio must be equal."
      self.slopes = [float(w_end - w_start) / float(num_years - 1) for w_end, w_start in zip(self.end_weights, portfolio.weights)]
      self.start_weights = copy.deepcopy(portfolio.weights)

    # Call the base class init:
    super(Scenario, self).__init__(name, num_years, portfolio, inflation_rate_perc, rebalance)

  def _run(self, start_year=0):
    to_add = self.addition
    for x in range(self.num_years):
      # Calculate new weights and rebalance portfolio:
      if self.slopes:
        new_weights = [s*x + w for w, s in zip(self.start_weights, self.slopes)] 
        self.portfolio.rebalance(new_weights)

      # Calculate amount to add to portfolio:
      to_add += to_add*self.addition_increase
      if to_add != 0.0:
        self.portfolio.trade(to_add)

      # Run the base class simulation:
      super(Scenario, self)._run(start_year)

  def run(self):
    self._run()

# Piecewise scenario:
# This scenario allows the combinations of other scenarios in a piecewise
# fashion. A list of scenarios is provided and each is executed in turn.
# Note: The monitary values of all portfolios except in the first scenario are ignored.
# After the first scenario is run, the value from that portfolio is transfered
# to the second portfolio, and so on.
class Piecewise_Scenario(_Scenario_Base):
  def __init__(self, name, scenarios):
    self.scenarios = scenarios
    first_scenario = self.scenarios[0]
    super(Piecewise_Scenario, self).__init__(name, first_scenario.num_years, first_scenario.portfolio)

  def reset(self):
    for scenario in self.scenarios:
      scenario.reset()
    super(Piecewise_Scenario, self).reset()

  def run(self):
    value = self.scenarios[0].portfolio.value()
    year = 0
    for scenario in self.scenarios:
      # First zero the scenario portfolio value:
      scenario.portfolio.trade(-1*scenario.portfolio.value())

      # Set scenario portfolio value with the value of the
      # previous scenario:
      scenario.portfolio.trade(value)

      # Run scenario:
      scenario._run(year)
      year += len(scenario.history) - 1

      # Save the final portfolio value:
      value = scenario.portfolio.value()

      # Save data:
      self.history.extend(copy.deepcopy(scenario.history[1:]))
      self.uncorrected_history.extend(copy.deepcopy(scenario.uncorrected_history[1:]))
      self.returns.extend(copy.deepcopy(scenario.returns))
      self.uncorrected_returns.extend(copy.deepcopy(scenario.uncorrected_returns))


def _remove_outliers(values):
  # Remove high outliers:
  med = statistics.median_low(values)
  MAD = astropy.stats.median_absolute_deviation(values)
  if MAD > 0.0:
    values = [v for v in values if v < (med + 4*MAD)]
    med = statistics.median_low(values)
    MAD = astropy.stats.median_absolute_deviation(values)
    if MAD > 0.0:
      values = [v for v in values if v < (med + 4*MAD)]
      med = statistics.median_low(values)
      MAD = astropy.stats.median_absolute_deviation(values)
      if MAD > 0.0:
        values = [v for v in values if v < (med + 4*MAD)]
  return values

#
# The Monte Carlo class
#
# This class takes in a scenario and runs it a variable number of times,
# storing the result for each run. After running, statistics can be 
# gathered on aggregate outcomes of the executed scenarios.
class Monte_Carlo(object):
  def __init__(self, scenario):
    self.scenario = copy.deepcopy(scenario)
    self.scenario.reset()
    self.runs = []
    self.values = []
    self.raw_values = []
    
  def run(self, n):
    for x in range(n):
      new_scenario = copy.deepcopy(self.scenario)
      new_scenario.run()
      self.raw_values.append(new_scenario.history[-1].value())
      self.runs.append(new_scenario)

  def results(self, goal=None, remove_outliers=False):
    if remove_outliers:
      self.values = _remove_outliers(self.raw_values)
    else:
      self.values = self.raw_values
    strn = "Monte Carlo Results for the '" + self.scenario.name + "' Scenario:\n"
    strn += "\n"
    strn += "Number of Runs: " + str(len(self.runs)) + "\n"
    strn += "High-end Outliers Removed: " + str(len(self.raw_values) - len(self.values)) + "\n"
    strn += "\n"
    strn += "Inflation Corrected Portfolio Final Values:\n"
    strn += "  Average:   " + _format_currency(statistics.mean(self.values)) + "\n"
    strn += "  Std Dev:   " + _format_currency(statistics.stdev(self.values)) + "\n"
    strn += "\n"
    strn += "  Median:    " + _format_currency(statistics.median_low(self.values)) + "\n"
    strn += "  MAD:       " + _format_currency(astropy.stats.median_absolute_deviation(self.values)) + "\n"
    strn += "\n"
    strn += "  Minimum:   " + _format_currency(min(self.values)) + "\n"
    strn += "  10th Perc: " + _format_currency(np.percentile(self.values, 10, interpolation='nearest')) + "\n"
    strn += "  Median:    " + _format_currency(statistics.median_low(self.values)) + "\n"
    strn += "  90th Perc: " + _format_currency(np.percentile(self.values, 90, interpolation='nearest')) + "\n"
    strn += "  Maximum:   " + _format_currency(max(self.values)) + "\n"
    strn += "\n"
    if goal != None:
      good_runs = len([v for v in self.raw_values if v > goal])
      strn += "Savings Goal: " + _format_currency(goal) + "\n"
      strn += "Likelihood of Meeting Goal: " + _format_percentage(good_runs/len(self.raw_values)) + "\n"
    return strn

  def histogram(self, remove_outliers=True):
    if remove_outliers:
      self.values = _remove_outliers(self.raw_values)
    else:
      self.values = self.raw_values
    import matplotlib.pyplot as plt
    values = [v/1000000.0 for v in self.values]
    weights = np.ones_like(values)/float(len(values))*100.0
    plt.figure()
    n, bins, patches = plt.hist(values, 30, weights=weights, facecolor='0.5', alpha=0.75)
    plt.axvline(x=statistics.median_low(values), color='g')
    plt.axvline(x=np.percentile(values, 10, interpolation='nearest'), color='r')
    two_MAD = statistics.median_low(values) - 2*astropy.stats.median_absolute_deviation(values)
    if two_MAD < 0.0:
      two_MAD = 0.0
    plt.axvline(x=two_MAD, color='m')
    two_MAD = statistics.median_low(self.values) - 2*astropy.stats.median_absolute_deviation(self.values)
    if two_MAD < 0.0:
      two_MAD = 0.0
    plt.legend([ \
      'Median (' + _format_currency(statistics.median_low(self.values)) + ')', \
      '10th Perc (' + _format_currency(np.percentile(self.values, 10, interpolation='nearest')) + ')', \
      r'-2*MAD (' + _format_currency(two_MAD) + ')', \
    ])
    plt.xlabel('Portfolio Value ($M)')
    plt.ylabel('Probability %')
    plt.title('Final Portfolio Value Probability Distribution (n=' + str(len(self.runs)) + ")")
    plt.grid(True)

  def plot(self, smooth=False):
    import matplotlib.pyplot as plt

    # Find the median and 10th percentile data sets:
    med = statistics.median_low(self.values)
    ten = np.percentile(self.values, 10, interpolation='nearest')
    med_scenario = self.runs[self.raw_values.index(med)]
    tenth_scenario = self.runs[self.raw_values.index(ten)]

    # Plot the median and 10th percentile scenario:
    f = plt.figure()
    med_scenario.plot(figure=f, color='lightblue', label='Median', smooth=smooth)
    tenth_scenario.plot(figure=f, color='steelblue', label='10th Perc', smooth=smooth)

def show_plots():
  import matplotlib.pyplot as plt
  plt.show()
