#!/usr/bin/env python3

# Include the directory up in the path:
import sys
sys.path.insert(0,'..')

# Import stocker:
import stocker

# Main:
if __name__== "__main__":

  # Define a portfolio that contains a mixed variety of stocks, bonds, alternatives, and cash with a value of 10k:
  sample_portfolio = stocker.Portfolio(
    name="Sample", \
    value=10000.0, \
    positions=[stocker.US_Stocks, stocker.International_Stocks, stocker.US_Bonds, stocker.International_Bonds, stocker.Alternatives, stocker.Cash], \
    weights=[30, 15, 20, 10, 5, 1] \
  )

  # Create a savings scenario where we compound the interest on this portfolio for 15 years, with no annual additions:
  savings = stocker.Scenario(name="Savings", portfolio=sample_portfolio, num_years=15)

  # Run the savings scenario once and print and plot the results:
  savings.run()
  print(savings.results())
  savings.plot(smooth=False)

  # Run a monte carlo simulation of this scenario with 400 iterations:
  mc = stocker.Monte_Carlo(savings)
  mc.run(n=400)

  # Print the results of the monte carlo simulation, showing the probablility
  # of hitting a 15k accumulation goal:
  print(mc.results(goal=15000))

  # Create the monte carlo plots:
  mc.histogram()
  mc.plot(smooth=True)

  # Show all the stocker plots:
  stocker.show_plots()
