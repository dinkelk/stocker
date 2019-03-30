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
  all_stocks_accumulation_phase = stocker.Scenario(
    name="Initial Accumulation", \
    portfolio=all_stocks_portfolio, \
    num_years=15, \
    annual_contribution=16000, \
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
  stocks_and_bonds_accumulation_phase = stocker.Scenario(
    name="Secondary Accumulation", \
    portfolio=stocks_and_bonds_portfolio, \
    num_years=15, \
    annual_contribution=20000, \
    annual_contribution_increase_perc=2.0, \
    end_weights=end_weights
  )

  # We have accumulated a large portfolio invested in 50/50 stocks
  # and bonds. We will use this portfolio throughout retirement
  retirement_portfolio = stocker.Portfolio(
    name="Stocks and Bonds", \
    value=1500000, \
    positions=[stocker.US_Stocks, stocker.International_Stocks, stocker.US_Bonds, stocker.International_Bonds], \
    weights=[7, 3, 7, 3] \
  )

  # We are going to live on annual distributions of 80K, increasing by 2% annually
  # to curb some inflation. We want to make this portfolio last for at lleast 30 years
  # during retirement.
  retirement_distribution_phase = stocker.Scenario(
    name="Retirement Distribution", \
    portfolio=retirement_portfolio, \
    num_years=30, \
    annual_contribution=-80000, \
    annual_contribution_increase_perc=2.0, \
  )

  # Combine these two accumulation phases together with the distribution phase using a piecewise scenario:
  retirement_plan = stocker.Piecewise_Scenario("Retirement Plan", [all_stocks_accumulation_phase, stocks_and_bonds_accumulation_phase, retirement_distribution_phase])

  # Run the savings scenario once and print and plot the results:
  retirement_plan.run()
  print(retirement_plan.results())
  retirement_plan.plot(smooth=False)

  # Run a monte carlo simulation of this scenario with 400 iterations:
  mc = stocker.Monte_Carlo(retirement_plan)
  mc.run(n=400)

  # Print the results of the monte carlo simulation, showing the probablility
  # of not running out of funds before the end of our retirement.
  print(mc.results(goal=0.0))

  # Create the monte carlo plots:
  mc.histogram()
  mc.plot(smooth=True)

  # Show all the stocker plots:
  stocker.show_plots()
