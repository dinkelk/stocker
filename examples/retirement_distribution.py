#!/usr/bin/env python3

# Include the directory up in the path:
import sys
sys.path.insert(0,'..')

# Import stocker:
import stocker

# Main:
if __name__== "__main__":

  # We have accumulated a portfolio of 1.5M dollars invested in 50/50 stocks
  # and bonds.
  stocks_and_bonds_portfolio = stocker.Portfolio(
    name="Stocks and Bonds", \
    value=1500000, \
    positions=[stocker.US_Stocks(), stocker.International_Stocks(), stocker.US_Bonds(), stocker.International_Bonds()], \
    weights=[7, 3, 7, 3] \
  )

  # We are going to live on annual distributions of 75K, increasing by 2% annually
  # to curb some inflation. We want to make this portfolio last for at lleast 30 years
  # during retirement.
  retirement_distribution = stocker.Scenario(
    name="Retirement Distribution", \
    portfolio=stocks_and_bonds_portfolio, \
    num_years=30, \
    annual_contribution=-75000, \
    annual_contribution_increase_perc=2.0, \
  )

  # Run the retirement scenario once and print and plot the results:
  retirement_distribution.run()
  print(retirement_distribution.results())
  retirement_distribution.plot(smooth=False)

  # Run a monte carlo simulation of this scenario with 400 iterations:
  mc = stocker.Monte_Carlo(retirement_distribution)
  mc.run(n=400)

  # Print the results of the monte carlo simulation, showing the probablility
  # of not running out of funds before the end of 30 years.
  print(mc.results(goal=0.0))

  # Create the monte carlo plots:
  mc.histogram()
  mc.plot(smooth=True)

  # Show all the stocker plots:
  stocker.show_plots()
