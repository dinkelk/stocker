import numpy.random
import copy
import statistics
import astropy.stats
import numpy as np

def format_currency(value):
  return "${:,.2f}".format(value)

def format_percentage(decimal):
  return ("%0.1f%% " % (decimal*100.0))

class Position(object):
  # ave return and std are in percentage per time unit:
  def __init__(self, name, ave_return, std_dev, value=0.0):
    self.name = name
    self.value = value
    self.ave_return = ave_return/100.0
    self.std_dev = std_dev/100.0

  def trade(self, amount):
    self.value += amount
    if self.value < 0.0:
      self.value = 0.0

  # Simulate 1 time unit:
  def simulate(self):
    # Calculate return as ave return + normal distribution of std deviation:
    this_return = 0.0
    if self.value > 0.0:
      this_return = self.ave_return*self.value + np.random.normal(0, self.value*self.std_dev)
    self.value = self.value + this_return
    if self.value < 0.0:
      self.value = 0.0

  def __repr__(self):
    return format_currency(self.value)

class Portfolio(object):
  def __init__(self, name, value, positions=[], weights=[]):
    self.name = name
    self.total_weight = float(sum(weights))
    self.weights = [float(w)/self.total_weight for w in weights]
    self.positions = positions

    assert len(weights)==len(positions), "The number of weights must equal the number of positions"
    assert value >= 0.0, "Initial value must be positive or zero."

    self.trade(value)

  # Simulate 1 time unit:
  def simulate(self):
    for position in self.positions:
      position.simulate()

  def value(self):
    return sum([p.value for p in self.positions])

  def trade(self, amount):
    for w, p in zip(self.weights, self.positions):
      p.trade(amount*w)

  def rebalance(self):
    value = self.value()

    for w, p in zip(self.weights, self.positions):
      current_weight = p.value/value
      new_value = p.value*w/current_weight
      correction = new_value-p.value
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
      strn += template.format(p.name, format_percentage(p.value/value), str(p)) + "\n"
    strn += "-----------------------------------------------------------\n"
    strn += template.format("Total", "100.0% ", format_currency(value)) + "\n"
    strn += "-----------------------------------------------------------\n"
    return strn

  def __str__(self):
    return self.__repr__()

class Assumptions(object):
  def __init__(self):
    pass

class Scenario(object):
  def __init__(self, name, portfolio, num_years, addition_per_year=0.0, addition_increase_perc=0.0, inflation_rate_perc=3.5, rebalance=True):
    self.name = name
    self.portfolio = portfolio
    self.num_years = num_years
    self.addition = addition_per_year
    self.addition_increase = addition_increase_perc/100.0
    self.inflation_rate = inflation_rate_perc/100.0
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

  def _simulate(self, year, addition=0.0):
    # Buy more of the portfolio, after simulation, worst case:
    self.portfolio.trade(addition)

    # Simulate a year of growth:
    self.portfolio.simulate()

    # Rebalance portfolio to match original allocation weights:
    if self.rebalance:
      self.portfolio.rebalance()

    # Correct the values in the portfolio for inflation to report
    # numbers in today's dollars:
    # Using the present value function to calculate what our money is actually worth with
    # inflation: http://financeformulas.net/present_value.html
    uncorrected_value = self.portfolio.value()
    corrected_value = uncorrected_value*(1/(1 + self.inflation_rate)**year)
    correction = corrected_value - uncorrected_value
    p = copy.deepcopy(self.portfolio)
    p.trade(correction)

    # Save the corrected portfolio history:
    self.history.append(p)
    return_perc = (self.history[-1].value() - self.history[-2].value())/self.history[-2].value()
    self.returns.append(return_perc)

    # Save the uncorrected porfolio in the history:
    self.uncorrected_history.append(copy.deepcopy(self.portfolio))
    return_perc = (self.uncorrected_history[-1].value() - self.uncorrected_history[-2].value())/self.uncorrected_history[-2].value()
    self.uncorrected_returns.append(return_perc)

  def simulate(self):
    to_add = self.addition
    for x in range(self.num_years):
      self._simulate(x+1, to_add)
      to_add += to_add*self.addition_increase

  def __repr__(self):
    strn = self.name + " Scenario:\n"
    strn += "Portfolio: " + self.portfolio.name + " Portfolio\n"
    strn += "Duration: " + str(len(self.history)-1) + " years\n"
    strn += "Annual Addition: " + format_currency(self.addition) + "\n"
    strn += "Annual Addition Increase: " + format_percentage(self.addition_increase) + "\n"
    strn += "Inflation Rate: " + format_percentage(self.inflation_rate) + "\n" 
    strn += "Annual Rebalancing: " + ("Yes" if self.rebalance else "No") + "\n" 
    strn += "\n"
    strn += self.portfolio.name + " Portfolio Start:\n"
    strn += str(self.history[0])
    strn += "\n"
    strn += self.portfolio.name + " Portfolio End:\n"
    strn += str(self.uncorrected_history[-1])
    strn += "\n"
    strn += self.portfolio.name + " Portfolio End (Inflation Corrected at " + format_percentage(self.inflation_rate) + "):\n" 
    strn += str(self.history[-1])
    strn += "\n"
    strn += "Raw Metrics:\n"
    strn += "Total Return: " + format_percentage((self.uncorrected_history[-1].value() - self.uncorrected_history[0].value())/self.uncorrected_history[0].value()) + "\n"
    strn += "Ave Return: " + format_percentage(sum(self.uncorrected_returns)/len(self.uncorrected_returns)) + "\n"
    strn += "Best Return: " + format_percentage(max(self.uncorrected_returns)) + " (year " + str(self.returns.index(max(self.returns))) + ")\n"
    strn += "Worst Return: " + format_percentage(min(self.uncorrected_returns)) + " (year " + str(self.returns.index(min(self.returns))) + ")\n"
    strn += "\n"
    strn += "Inflation Corrected Metrics at " + format_percentage(self.inflation_rate) + ":\n" 
    strn += "Total Return: " + format_percentage((self.history[-1].value() - self.history[0].value())/self.history[0].value()) + "\n"
    strn += "Ave Return: " + format_percentage(sum(self.returns)/len(self.returns)) + "\n"
    strn += "Best Return: " + format_percentage(max(self.returns)) + " (year " + str(self.returns.index(max(self.returns))) + ")\n"
    strn += "Worst Return: " + format_percentage(min(self.returns)) + " (year " + str(self.returns.index(min(self.returns))) + ")\n"
    return strn

  def __str__(self):
    return self.__repr__()

class Monte_Carlo(object):
  def __init__(self, scenario):
    self.scenario = copy.deepcopy(scenario)
    self.scenario.reset()
    self.runs = []
    self.values = []
    
  def run(self, n):
    for x in range(n):
      new_scenario = copy.deepcopy(self.scenario)
      new_scenario.simulate()
      self.values.append(new_scenario.history[-1].value())
      self.runs.append(new_scenario)

  def __repr__(self):
    strn = "Monte Carlo Results for " + str(len(self.runs)) + " Scenarios:\n"
    strn += "Portfolio: " + self.scenario.portfolio.name + " Portfolio\n"
    strn += "\n"
    strn += "Inflation Corrected Portfolio Final Values:\n"
    strn += "  Average:   " + format_currency(statistics.mean(self.values)) + "\n"
    strn += "  Std Dev:   " + format_currency(statistics.stdev(self.values)) + "\n"
    strn += "\n"
    strn += "  Median:    " + format_currency(statistics.median_low(self.values)) + "\n"
    strn += "  MAD:       " + format_currency(astropy.stats.median_absolute_deviation(self.values)) + "\n"
    strn += "\n"
    strn += "  Minimum:   " + format_currency(min(self.values)) + "\n"
    strn += "  10th Perc: " + format_currency(np.percentile(self.values, 10, interpolation='nearest')) + "\n"
    strn += "  Median:    " + format_currency(statistics.median_low(self.values)) + "\n"
    strn += "  90th Perc: " + format_currency(np.percentile(self.values, 90, interpolation='nearest')) + "\n"
    strn += "  Maximum:   " + format_currency(max(self.values)) + "\n"
    return strn

  def __str__(self):
    return self.__repr__()

  def histogram(self):
    import matplotlib.pyplot as plt
    values = [v/1000000.0 for v in self.values]
    weights = np.ones_like(values)/float(len(values))*100.0
    plt.figure()
    n, bins, patches = plt.hist(values, 30, weights=weights, facecolor='0.5', alpha=0.75)
    plt.axvline(x=statistics.median_low(values), color='g')
    plt.axvline(x=np.percentile(values, 10, interpolation='nearest'), color='r')
    plt.axvline(x=statistics.median_low(values) - 2*astropy.stats.median_absolute_deviation(values), color='m')
    plt.legend([ \
      'Median (' + format_currency(statistics.median_low(self.values)) + ')', \
      '10th Perc (' + format_currency(np.percentile(self.values, 10, interpolation='nearest')) + ')', \
      r'-2*MAD (' + format_currency(statistics.median_low(self.values) - 2*astropy.stats.median_absolute_deviation(self.values)) + ')', \
    ])
    plt.xlabel('Portfolio Value ($M)')
    plt.ylabel('Probability %')
    plt.title('Final Portfolio Value Probability Distribution (n=' + str(len(self.runs)) + ")")
    plt.grid(True)
    plt.show()

  def plot(self, smooth=True):
    import matplotlib.pyplot as plt
    from scipy.signal import savgol_filter

    # Find the median and 10th percentile data sets:
    med_scenario = self.runs[statistics.median_low((val, idx) for (idx, val) in enumerate(self.values))[1]]
    tenth_scenario = self.runs[self.values.index(np.percentile(self.values, 10, interpolation='nearest'))]
    med_data = [p.value()/1000000 for p in med_scenario.history]
    tenth_data = [p.value()/1000000 for p in tenth_scenario.history]
    # Plot data:
    plt.figure()
    if smooth:
      med_data = savgol_filter(med_data, 11, 3)
      tenth_data = savgol_filter(tenth_data, 11, 3)
    plt.plot(med_data, lw=1, color='lightblue')
    plt.fill_between(list(range(len(med_data))), med_data, interpolate=False, facecolor='lightblue', alpha=0.5)
    plt.plot(tenth_data, lw=1, color='steelblue')
    plt.fill_between(list(range(len(tenth_data))), tenth_data, interpolate=False, facecolor='steelblue', alpha=0.5)
    plt.ylim(bottom=0.0) 
    plt.xlim(0, len(med_data) - 1)
    plt.xlabel('Year')
    plt.ylabel('Portfolio Value ($M)')
    plt.title('Portfolio Value Over Time')
    plt.legend([ \
      'Median (' + format_currency(statistics.median_low(self.values)) + ')', \
      '10th Perc (' + format_currency(np.percentile(self.values, 10)) + ')', \
    ])
    plt.grid(True)
    plt.show()


if __name__== "__main__":
  us_stocks = Position("Domestic Equities", ave_return=10.2, std_dev=19.8)
  int_stocks = Position("International Equities", ave_return=9.2, std_dev=22.1)
  us_bonds = Position("Domestic Fixed Income", ave_return=5.3, std_dev=5.8)
  int_bonds = Position("International Fixed Income", ave_return=5.5, std_dev=9.1)
  alternatives = Position("Alternatives", ave_return=6.1, std_dev=16.1)
  cash = Position("Cash", ave_return=3.4, std_dev=3.1)

  sample_portfolio = Portfolio(name="Sample", value=100000.0, positions=[us_stocks, int_stocks, us_bonds, int_bonds, alternatives, cash], weights=[35, 15, 20, 10, 5, 1])

  sample_scenario = Scenario("Sample", sample_portfolio, 30, 15000.0, 2.0)
  sample_scenario.simulate()
  print(str(sample_scenario))

  mc = Monte_Carlo(sample_scenario)
  mc.run(250)
  print(str(mc))
  mc.histogram()
  mc.plot()

