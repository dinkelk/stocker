#!/usr/bin/env python3

# Include the directory up in the path:
import sys
sys.path.insert(0,'..')

# Import stocker:
import stocker

# Main:
if __name__== "__main__":

  # Define a retirement portfolio with a 60/40 split between US stocks and US 
  # bonds. 
  stocks_and_bonds_portfolio = stocker.Portfolio(
    name="Retirement Savings", \
    value=250000, \
    positions=[stocker.US_Stocks, stocker.US_Bonds], \
    weights=[6, 4]
  )
  print(str(stocks_and_bonds_portfolio))

  # Define a retirement savings scenario that lasts for 30 years. We will
  # contribute 10K annually, increasing our svings amount by 2% every year.
  retirement_scenario = stocker.Scenario(
    name="Retirement Accumulation", \
    portfolio=stocks_and_bonds_portfolio, \
    num_years=30, \
    annual_contribution=20000, \
    annual_contribution_increase_perc=2.0, \
  )

  # Run the savings scenario once and print and plot the results:
  retirement_scenario.run()
  print(retirement_scenario.results())
  retirement_scenario.plot(smooth=True)

  # Run a monte carlo simulation of this scenario with 400 iterations:
  mc = stocker.Monte_Carlo(retirement_scenario)
  mc.run(n=400)

  # Print the results of the monte carlo simulation, showing the probablility
  # of hitting a 1M dollar accumulation goal:
  print(mc.results(goal=1000000))

  # Create the monte carlo plots:
  mc.histogram()
  mc.plot(smooth=True)

  # Show all the stocker plots:
  stocker.show_plots()
