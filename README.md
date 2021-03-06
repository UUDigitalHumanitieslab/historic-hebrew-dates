[![Build Status](https://travis-ci.com/UUDigitalHumanitieslab/historic-hebrew-dates.svg?token=gbE1yWiPSuz64uDZEWzs&branch=develop)](https://travis-ci.com/UUDigitalHumanitieslab/historic-hebrew-dates)

WARNING: this library is very rough around the edges

# Historic Hebrew Dates

Python library and console application for extracting Hebrew and Aramaic dates from historic texts. It includes a graphical editor to specify, modify and test the search patterns.

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
print(result[0][0].value) # ((7*100+5*10)+4)
print(result[0][0].evaluated) # 754
```

# Getting the Editor to Work

## Using Vagrant

On a machine without developer tools it's probably most convenient to use [Vagrant](https://www.vagrantup.com/docs/installation/) for running the editor.

Once this has been setup run the following from a terminal at the root directory of this project:

```bash
vagrant up
```

Wait for everything to be ready (can take a few minutes), then it should be possible to go
to http://localhost:4200. Changes made to the patterns can be send back
to this repository using [Git](https://git-scm.com/).

## Locally

* Install [Python 3.6](https://www.python.org) or newer and make sure to include pip.
* Install [node](https://nodejs.org).
* Install [yarn](https://yarnpkg.com).

(If you want you could setup a [virtual environment](https://virtualenv.pypa.io) first).

```
yarn
yarn start
```

Go to `http://localhost:4200`.

# How Does it Work?

Dates consist of different formats and constituent parts, e.g.:

* <u>thirteenth</u> of **September**, _2019_
* **September** <u>13</u>, _twenty-nineteen_

These different formats can be matched using a list of patterns:

* `{day:ordinal} of {month}, {year:number}`
* `{month} {day:number}, {year:number}`

Patterns can also be derived automatically using an annotated corpus (see `annotated_corpus.py`).

The patterns are text strings with optional placeholder references for other patterns. Those references consist of a name (e.g. `month`, `day`, `year`) and a type (`number`, `ordinal`, `month`...). It is also possible to reference to preceding patterns by their type name or all preceding patterns using a numbered reference (e.g. `{1}`).

The matched values are then available for the expression, which can be evaluated using the evaluation function which has been specified for the pattern type.

For example for numbers:

| type | pattern | value |
| ---- | ------- | ----- |
| A | one | `1` |
| A | two | `2` |
| A | ... | ...|
| A | nine | `9` |
| B | twenty | `20` |
| B | thirty | `30` |
| B | ... | ... |
| B | ninety | `90` |
| C | `{big:B}-{small:A}` | `({big}+{small})` |

This could match and evaluate forty-two.

The text is tokenized using all the tokens found in the patterns. If a word is of an unknown token, the system will try to split it up in multiple tokens. This way it can work with words which are written together.

It is also possible to specify in the search text that parts are missing by using a question mark. Those will be filled with all the possible known tokens.

Search is then done using a chart parser. The parser goes through all the patterns, matches them against all the possible (sub) token interpretations and finally returns all the possible matches.

The patterns are specified in `historic_hebrew_dates/patterns` and can be edited using a graphical web interface.

# Supporting Another Language

Copying, renaming and editing the `.json` file of another language is enough to get started. Once this has been done you can specify the patterns using the editor.
