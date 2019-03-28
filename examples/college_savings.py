#!/usr/bin/env python3

# Include the directory up in the path:
import sys
sys.path.insert(0,'..')

# Import stocker:
import stocker

# Main:
if __name__== "__main__":

  # Let's save in a combination of US stocks and US bonds for college. Weight the
  # initial portfolio towards 100% stocks, but gradually transition to 100% bonds
  # over the coarse of the savings period. We can seed the portfolio with $5000.
  positions = [stocker.US_Stocks, stocker.US_Bonds]
  start_weights = [1, 0]
  end_weights = [0, 1]
  college_529_portfolio = stocker.Portfolio(name="529", value=5000.0, positions=positions, weights=start_weights)

  # Create the college savings scenario where we compound the interest on this portfolio 
  # for 18 years, adding $2500 annually. Assume an inflation rate of 2.5%
  college_savings = stocker.Scenario(name="College", portfolio=college_529_portfolio, num_years=18, annual_contribution=2500, inflation_rate_perc=2.5, end_weights=end_weights)

  # Run the savings scenario once and print and plot the results:
  college_savings.run()
  print(college_savings.results())
  college_savings.plot(smooth=False)

  # Run a monte carlo simulation of this scenario with 400 iterations:
  mc = stocker.Monte_Carlo(college_savings)
  mc.run(n=400)

  # Print the results of the monte carlo simulation, showing the probablility
  # of hitting a 15k accumulation goal:
  print(mc.results(goal=60000))

  # Create the monte carlo plots:
  mc.histogram()
  mc.plot(smooth=True)

  # Show all the stocker plots:
  stocker.show_plots()
