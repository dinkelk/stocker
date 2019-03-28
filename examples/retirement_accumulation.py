#!/usr/bin/env python3

# Include the directory up in the path:
import sys
sys.path.insert(0,'..')

# Import stocker:
import stocker

# Main:
if __name__== "__main__":

  # Let's save in a combination of stocks and bonds for retirement. Weight the
  # initial portfolio towards 100% stocks for 15 years, weighted 70% US and 
  # 30% international. We will contribute 15000 annually with a 2% increase
  # in that contribution annually. Assume the default inflation rate of 3.5%.
  all_stocks_portfolio = stocker.Portfolio(
    name="Stocks", \
    value=0.0, \
    positions=[stocker.US_Stocks, stocker.International_Stocks], \
    weights=[7, 3]
  )
  all_stocks_phase = stocker.Scenario(
    name="Initial Accumulation", \
    portfolio=all_stocks_portfolio, \
    num_years=15, \
    annual_contribution=15000, \
    annual_contribution_increase_perc=2.0
  )

  # The next phase of our retirement accumulation will start at 100% stocks
  # but gradually transition to a 50/50 stocks/bonds portfolio by retirement.
  # This phase consists of 20 years more accumulation, with an annual contribution
  # of 20k, increasing 2% each year.
  end_weights = [7, 3, 7, 3]
  stocks_and_bonds_portfolio = stocker.Portfolio(
    name="Stocks and Bonds", \
    positions=[stocker.US_Stocks, stocker.International_Stocks, stocker.US_Bonds, stocker.International_Bonds], \
    weights=[7, 3, 0, 0]
  )
  stocks_and_bonds_phase = stocker.Scenario(
    name="Secondary Accumulation", \
    portfolio=stocks_and_bonds_portfolio, \
    num_years=15, \
    annual_contribution=20000, \
    annual_contribution_increase_perc=2.0, \
    end_weights=end_weights
  )

  # Combine these two accumulation phases together using a piecewise scenario:
  retirement_accumulation = stocker.Piecewise_Scenario("Retirement Accumulation", [all_stocks_phase, stocks_and_bonds_phase])

  # Run the savings scenario once and print and plot the results:
  retirement_accumulation.run()
  print(retirement_accumulation.results())
  retirement_accumulation.plot(smooth=False)

  # Run a monte carlo simulation of this scenario with 400 iterations:
  mc = stocker.Monte_Carlo(retirement_accumulation)
  mc.run(n=400)

  # Print the results of the monte carlo simulation, showing the probablility
  # of hitting a 1M dollar accumulation goal:
  print(mc.results(goal=1000000))

  # Create the monte carlo plots:
  mc.histogram()
  mc.plot(smooth=True)

  # Show all the stocker plots:
  stocker.show_plots()
