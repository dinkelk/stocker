# Include the directory up in the path:
import sys
sys.path.insert(0,'..')

# Import stocker:
import stocker

# Main:
if __name__== "__main__":
  #sample_portfolio = Portfolio(name="Sample", value=100000.0, positions=[US_Stocks, International_Stocks, US_Bonds, International_Bonds, Alternatives, Cash], weights=[30, 15, 20, 10, 5, 1])
  start_weights=[1, 0]
  end_weights=[0, 1]
  sample_portfolio = stocker.Portfolio(name="Sample", value=100000.0, positions=[stocker.US_Stocks, stocker.US_Bonds], weights=start_weights)
  #sample_portfolio = Portfolio(name="Sample", value=100000.0, positions=[US_Stocks, International_Stocks], weights=[70, 0])
  #sample_portfolio = Portfolio(name="Stocks", value=100000.0, positions=[US_Stocks, US_Bonds, Alternatives, Cash], weights=[50, 40, 5, 5])
  #sample_portfolio2 = Portfolio(name="Bonds", value=100000.0, positions=[US_Stocks, US_Bonds, Alternatives, Cash], weights=[0, 40, 5, 5])
  accumulation = stocker.Scenario("Accumulation", sample_portfolio, num_years=35, addition_per_year=15000.0, addition_increase_perc=2.0, end_weights=end_weights)
  retirement = accumulation
  #distribution = Scenario("Distribution", sample_portfolio, num_years=30, addition_per_year=80000.0, addition_increase_perc=-3.5)
  #retirement = Piecewise_Scenario("Retirement", [accumulation, distribution])
  retirement.run()
  print(retirement.results())
  retirement.plot(smooth=False)

  mc = stocker.Monte_Carlo(retirement)
  mc.run(250)
  print(mc.results(goal = 1000000))
  mc.histogram()
  mc.plot(smooth=True)
  stocker.show_plots()
