# generate-gedcom

Python program to create a genealogical GEDCOM for testing other tools.

## Usage

One input parameter is the number of people to generate. Output file is sent to standard out.

```
generate-gedcom.py 200 >test.ged 2>run.err
```

## Notes

There are some random decisions:
- how many children in a family
- choice of given name
- if a spouse will have a sibling or two
- if a spouse will have grandparents

Inital test generated one million individuals in about 32 seconds.

## Limitations

- Requires Python 3.6+
