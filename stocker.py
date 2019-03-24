import numpy.random
import copy

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
      this_return = self.ave_return*self.value + numpy.random.normal(0, self.value*self.std_dev)
    self.value = self.value + this_return
    if self.value < 0.0:
      self.value = 0.0

  def __repr__(self):
    #return "$%0.2f" % self.value
    return "${:,.2f}".format(self.value)

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
    #strn += "\tPosition:\tAllocation:\tValue:\n"
    strn = "-----------------------------------------------------------\n"
    strn += template.format("Position", "Allocation ", "Value") + "\n"
    strn += "-----------------------------------------------------------\n"
    for w, p in zip(self.weights, self.positions):
      #strn += "\t" + p.name + "\t" + ("%0.2f" % (w*100.0)) + "%\t" + str(p) + "\n"
      strn += template.format(p.name, ("%0.1f%% " % (p.value/value*100.0)), str(p)) + "\n"
    strn += "-----------------------------------------------------------\n"
    strn += template.format("Total", "100.0% ", "${:,.2f}".format(value)) + "\n"
    strn += "-----------------------------------------------------------\n"
    return strn

  def __str__(self):
    return self.__repr__()

class Assumptions(object):
  def __init__(self):
    pass

class Scenario(object):
  def __init__(self, name, portfolio):
    self.name = name
    self.portfolio = portfolio
    self.history = [copy.deepcopy(portfolio)]
    self.returns = []
    self.inflation = []

  def simulate(self, addition=0.0, rebalance=True):
    # Buy more of the portfolio, after simulation, worst case:
    self.portfolio.trade(addition)

    # Simulate a year of growth:
    self.portfolio.simulate()

    # Rebalance portfolio to match original allocation weights:
    if rebalance:
      self.portfolio.rebalance()

    # Save the porfolio in the history:
    self.history.append(copy.deepcopy(self.portfolio))
    return_perc = (self.history[-1].value() - self.history[-2].value())/self.history[-2].value()
    self.returns.append(return_perc)

  def simulate_for(self, num_years, addition=0.0, addition_increase_perc=0.0, rebalance=True):
    for x in range(num_years):
      to_add = addition + addition_increase_perc*addition_increase_perc*x
      self.simulate(to_add, rebalance)

  # Calculate portfolio history in terms of today's dollars.
  #def adjust_for_inflation(self):
  #  # Calculate inflation rate:
  #  inflation = inflation_rate/100 + numpy.random.normal(0, inflation_std_dev/100)
  #  self.inflation.append(inflation)

  #  # Correct for inflation:
  #  # Using the present value function to calculate what our money is actually worth with
  #  # inflation: http://financeformulas.net/present_value.html
  #  value = self.portfolio.value()
  #  corrected_value = value/(1 + inflation)
  #  difference = corrected_value - value
  #  self.portfolio.trade(difference)

  def __repr__(self):
    strn = self.name + " Scenario:\n"
    strn += "Portfolio: " + self.portfolio.name + " Portfolio\n"
    strn += "Duration: " + str(len(self.history)-1) + " years\n"
    strn += "\n"
    strn += self.portfolio.name + " Portfolio Start:\n"
    strn += str(self.history[0])
    strn += "\n"
    strn += self.portfolio.name + " Portfolio End:\n"
    strn += str(self.history[-1])
    strn += "\n"
    strn += "Total Return: " + ("%0.1f%%" % (((self.history[-1].value() - self.history[0].value())/self.history[0].value())*100)) + "\n"
    strn += "Ave Return: " + ("%0.1f%%" % (sum(self.returns)/len(self.returns)*100)) + "\n"
    strn += "Best Return: " + ("%0.1f%%" % (max(self.returns)*100)) + " (year " + str(self.returns.index(max(self.returns))) + ")\n"
    strn += "Worst Return: " + ("%0.1f%%" % (min(self.returns)*100)) + " (year " + str(self.returns.index(min(self.returns))) + ")\n"
    return strn

  def __str__(self):
    return self.__repr__()

if __name__== "__main__":
  us_stocks = Position("Domestic Equities", ave_return=10.2, std_dev=19.8)
  int_stocks = Position("International Equities", ave_return=9.2, std_dev=22.1)
  us_bonds = Position("Domestic Fixed Income", ave_return=5.3, std_dev=5.8)
  int_bonds = Position("International Fixed Income", ave_return=5.5, std_dev=9.1)
  alternatives = Position("Alternatives", ave_return=6.1, std_dev=16.1)
  cash = Position("Cash", ave_return=3.4, std_dev=3.1)

  sample_portfolio = Portfolio(name="Sample", value=100000.0, positions=[us_stocks, int_stocks, us_bonds, int_bonds, alternatives, cash], weights=[35, 15, 20, 10, 5, 1])

  sample_scenario = Scenario("Sample", sample_portfolio)
  sample_scenario.simulate_for(30)

  print(str(sample_scenario))

