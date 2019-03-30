# stocker
An easy to use Monte Carlo savings and retirement planner.

## Why

I built this tool while trying to understand the "risk" of an investment portfolio. Asset classes and individual investments have volatility (often quantified by standard deviation) which measures the up and down variation of the investment over time. However, the impact of this volatility is difficult to understand for a buy-and-hold investor with very long timelines, typical of retirement or college savings. To determine risk posture, investors are often asked to answer a short survey, the answers of which reflect the likelihood of an investor to sell off an asset class should it drop in value. While this is certainly a factor that should not be overlooked, for a disciplined buy-and-hold investor, true risk should be quantified as the risk that their savings plan may not meet their savings goal. 

Stocker can be used to quantify investment risk in a more tangible way. By simulating many, many possible outcomes for a given portfolio, stocker calculates the probability that the allocation and savings plan will meet the goals of the investor. Stocker takes in portfolio information about the average return and standard deviation of a portfolio's underlying assets and provides a distribution of possible outcomes that may result.

## How It Works

Stocker allows you to define a portfolio of different positions (stocks, bonds, etc.), and then simulate the performance of that portfolio forward in time. Stocker understands each position in your portfolio as a combination of two numbers, the average annual return over time, and the annual standard deviation. The historical performance of many common assets such as the aggregate US and international stocks and bonds is provided by stocker for easy use, however, you can define a portfolio position with whatever annual return and standard deviation you project as the most accurate of future performance. Stocker uses these numbers for each portfolio position to project a possible future outcome for each year of the simulation.

By running many simulations of the same scenario, a well formed distribution of final portfolio values can be projected, allowing stocker to calculate a probability that your portfolio will meet your savings goal. Stocker provides many different scenario inputs such as annual contributions/distributions, annual rebalancing, inflation correction, and age-based portfolio transitions. See the usage section, below, or the [examples directory](examples/) for more details.

## Usage

Let's plan for retirement. Below we define a $250,000 portfolio made up of 60% US stocks and 40% US Bonds:

```
stocks_and_bonds_portfolio = Portfolio(
    name="Retirement Savings", \
    value=250000, \
    positions=[US_Stocks, US_Bonds], \
    weights=[6, 4]
)
print(str(stocks_and_bonds_portfolio))
```

which produces the following output:

```
-----------------------------------------------------------
Position                      | Allocation |          Value
-----------------------------------------------------------
Domestic Equities             |       60.0%|    $150,000.00
Domestic Fixed Income         |       40.0%|    $100,000.00
-----------------------------------------------------------
Total                         |     100.0% |    $250,000.00
-----------------------------------------------------------
```
 
In addition to `US_Stocks` and `US_Bonds`, stocker provides a few other positions based on the performance of historical asset classes. Feel free to mix these into your portfolio, or define your own `Position` with its own average return and standard deviation:

```
US_Stocks = Position("Domestic Equities", ave_return=10.2, std_dev=19.8)
International_Stocks = Position("International Equities", ave_return=9.2, std_dev=22.1)
US_Bonds = Position("Domestic Fixed Income", ave_return=5.3, std_dev=5.8)
International_Bonds = Position("International Fixed Income", ave_return=5.5, std_dev=9.1)
Alternatives = Position("Alternatives", ave_return=6.1, std_dev=16.1)
Cash = Position("Cash", ave_return=3.4, std_dev=3.1)
```

Next, we can define a savings scenario that uses the portfolio we defined earlier. The following scenario defines the accumulation phase of a retirement plan that compounds for a period of 30 years. We are planning to contribute an additional $20,000 to the portfolio annually, increasing this contribution amount by 2% every year.

```
retirement_scenario = stocker.Scenario(
    name="Retirement Accumulation", \
    portfolio=stocks_and_bonds_portfolio, \
    num_years=30, \
    annual_contribution=20000, \
    annual_contribution_increase_perc=2.0
)
```

Now that the scenario has been defined, we can run it to see what kind of return it produces:

```
retirement_scenario.run()
print(retirement_scenario.results())
```

The code above produces the following output:

```
'Retirement Accumulation' Scenario:
Portfolio: Retirement Savings Portfolio
Duration: 30 years
Inflation Rate: 3.5%
Annual Rebalancing: Yes

Retirement Savings Portfolio Start:
-----------------------------------------------------------
Position                      | Allocation |          Value
-----------------------------------------------------------
Domestic Equities             |       60.0%|    $150,000.00
Domestic Fixed Income         |       40.0%|    $100,000.00
-----------------------------------------------------------
Total                         |     100.0% |    $250,000.00
-----------------------------------------------------------

Retirement Savings Portfolio End (Inflation Corrected at 3.5%):
-----------------------------------------------------------
Position                      | Allocation |          Value
-----------------------------------------------------------
Domestic Equities             |       60.0%|  $1,063,515.22
Domestic Fixed Income         |       40.0%|    $709,010.14
-----------------------------------------------------------
Total                         |     100.0% |  $1,772,525.36
-----------------------------------------------------------

Raw Metrics:
Ave Return: 7.9%
Best Return: 46.2% (year 4)
Worst Return: -23.1% (year 6)

Inflation Corrected Metrics at 3.5%:
Ave Return: 4.2%
Best Return: 41.3% (year 4)
Worst Return: -25.7% (year 6)
```

Great! This was a profitable simulation. The final value of our portfolio was above 1.7 million in today's dollars. We can produce a plot of this run too:

```
retirement_scenario.plot(smooth=True) # Enable smoothing to hide some volatility
```

![Alt text](relative/path/to/img.jpg?raw=true "Title")

This single result is promising, but it only represents one possible outcome. The volatility of these underlying investments may perform much differently on subsequent runs. To get an idea of how this portfolio performs on average, we need to run this scenario many more times. The following code uses the Monte Carlo class to run 400 simulations of the scenario and compare the results to our savings goal of 1 million dollars:

```
mc = stocker.Monte_Carlo(retirement_scenario)
mc.run(n=400)
print(mc.results(goal=1000000))
```

The code above produces the following output:

```
Monte Carlo Results for the 'Retirement Accumulation' Scenario:

Number of Runs: 400
High-end Outliers Removed: 15

Inflation Corrected Portfolio Final Values:
  Average:   $1,937,428.17
  Std Dev:   $860,675.75

  Median:    $1,778,466.98
  MAD:       $580,846.20

  Minimum:   $460,648.34
  10th Perc: $921,443.29
  Median:    $1,778,466.98
  90th Perc: $3,203,398.54
  Maximum:   $4,283,117.80

Savings Goal: $1,000,000.00
Likelihood of Meeting Goal: 88.8%
```

Note that the median value is around 1.8 million dollars with a mean absolute deviation (MAD) of 580 thousand dollars. This is well above our goal of 1 million dollars. By analyzing the results from all 400 scenarios, stocker reports that the likelihood of meeting our 1 million dollar goal is 88.8% using our portfolio and savings plan.

To get a better feel for the results we can produce a few useful plots. The first is a historgram which shows the distribution of the final portfolio values for each of the 400 runs.

```
mc.histogram()
stocker.show_plots()
```

![Alt text](relative/path/to/img.jpg?raw=true "Title")

We can also easily plot two important simulations, the median scenario, which represents the most likely performance of our portfolio, and the 10th percentile scenario, which represents the probable worst case scenario for our portfolio.

```
mc.plot(smooth=True)
stocker.show_plots()
```

![Alt text](relative/path/to/img.jpg?raw=true "Title")

## Examples

For more examples on what stocker can do see [this directory](examples/).

## Installation

Stocker's dependencies can be installed via `pip`:

```
pip install -r requirements.txt
```

Then, simply clone this repository, add it to you path, and `import` it in your code.

## Want to contribute?

Please submit a *pull request* or *issue* with any questions you might have.
