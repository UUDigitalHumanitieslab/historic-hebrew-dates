[![Build Status](https://travis-ci.com/UUDigitalHumanitieslab/historic-hebrew-dates.svg?token=gbE1yWiPSuz64uDZEWzs&branch=develop)](https://travis-ci.com/UUDigitalHumanitieslab/historic-hebrew-dates)

# Historic Hebrew Dates

Python library and console application for extracting Hebrew and Aramaic dates from historic texts.

## Running from the Console

```bash
$ python -m historic_hebrew_dates שבע מאות וחמישים וארבע
> 7*100+5*10+4
> 754
```

## From Code

```python
from historic_hebrew_dates import create_parsers
hebrew = create_parsers('hebrew')

result = hebrew['numerals'].parse('שבע מאות וחמישים וארבע')
print(result) # ((7*100+5*10)+4)

result = hebrew['numerals'].parse('שבע מאות וחמישים וארבע', True)
print(result) # 754
```

# Getting it to Work

* Install [Python 3.6](https://www.python.org) or newer and make sure to include pip.
* Install [node](https://nodejs.org).
* Install [yarn](https://yarnpkg.com).

(If you want you could setup a [virtual environment](https://virtualenv.pypa.io) first).

```
yarn
yarn start
```

Go to `http://localhost:4200`.
