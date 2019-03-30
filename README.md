# stocker
An easy to use Monte Carlo savings and retirement planner.

## Why

I built this tool while trying to understand the "risk" of an investment portfolio. Asset classes and individual investments have volatility (often quantified by standard deviation) which measures the up and down variation of the investment over time. However, the impact of this volatility is difficult to understand for a buy-and-hold investor with very long timelines, typical of retirement or college savings. To determine risk posture, investors are often asked to answer a short survey, the answers of which reflect the likelihood of an investor to sell off an asset class should it drop in value. While this is certainly a factor that should not be overlooked, for a disciplined buy-and-hold investor, true risk should be quantified as the risk that their savings plan may not meet their savings goal. 

Stocker can be used to quantify investment risk in a more tangible way. By simulating many, many possible outcomes for a given portfolio, stocker calculates the probability that the allocation and savings plan will meet the goals of the investor. Stocker takes in portfolio information about the average return and standard deviation of a portfolio's underlying assets and provides a distribution of possible outcomes that may result.

## How It Works

Stocker allows you to define a portfolio of different positions (stocks, bonds, etc.), and then simulate the performance of that portfolio forward in time. Stocker understands each position in your portfolio as a combination of two numbers, the average annual return over time, and the annual standard deviation. The historical performance of many common assets such as the aggregate US and international stocks and bonds is provided by stocker for easy use, however, you can define a portfolio position with whatever annual return and standard deviation you project as the most accurate of future performance. Stocker uses these numbers for each portfolio position to project a possible future outcome for each year of the simulation.

By running many simulations of the same scenario, a well formed distribution of final portfolio values can be projected, allowing stocker to calculate a probability that your portfolio will meet your savings goal. Stocker provides many different scenario inputs such as annual contributions/distributions, annual rebalancing, inflation correction, and age-based portfolio transitions. See the usage section, below, or the [examples directory](examples/) for more details.

## Usage

TODO

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
