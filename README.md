# generate-gedcom

Python program to create a genealogical GEDCOM for testing other tools.

## Usage

One input parameter: the number of people to generate. Output file is sent to standard out. Some stats are printed to stderr.

```
generate-gedcom.py 200 >test.ged 2>run.err
```

There is an optional second parameter which can override the include-dates setting within the program code. It can be "nodates" or "yesdates". Date creating is enabled by default because it helps with identifying individuals.

```
generate-gedcom.py 400 nodates >tet.ged 2>run.err
```


## Notes

This is only for biological relationship testing. There dates (if enabled) for birth, death and marriate but no other events created.

There are some random decisions (adjustable by variables inside the program):
- how many children in a family
- choice of given name
- if a spouse will have a sibling or two
- if a spouse will have grandparents

## Timing on a modest pc

Without dates:
- 10 thousand individuals in about 1 second.
- one million individuals in about 32 seconds.

## Limitations

- Requires Python 3.6+
