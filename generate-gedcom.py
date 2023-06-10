''' Create a gedcom family tree to stdout
Input parameter is the number of people, default 10, min 10
Second optional parameter of "nodates" or "yesdates" overrides the setting inside the program.

This is for biological relationship testing only.
There are no places.
There are no events or facts except some birth, death and marriage dates.

For simplicity to ensure the tree doesn't expire before creating
the selected number of people: every child will take a spouse
and every family will have children.

This code is released under the MIT License: https://opensource.org/licenses/MIT
Copyright (c) 2023 John A. Andrea
v2.1

No support provided.
'''

import sys
import random


# every family will have this many children
MIN_CHILDREN = 2
MAX_CHILDREN = 6

# a person will take a second spouse if the probability exceeds
#SECOND_SPOUSE_PROB = 0.92 #not yet used

# more inlaws
ADD_SPOUSE_SIBLING = 0.60
SECOND_SPOUSE_SIBLING = 0.85
SPOUSE_GRANDPARENTS = 0.75

# all the date controls
INCLUDE_DATES = True
ADD_DEATH_PROB = 0.8
ADD_MARRIAGE_DATE_PROB = 0.4
START_YEAR = 1800
AGE_DIFFER_FROM_SPOUSE = 4 # +/-
YEARS_MARRIED_BEFORE_CHILD = 3  # zero minimum
MIN_AGE_FIRST_CHILDBIRTH = 18 # for the mother
MAX_AGE_FIRST_CHILDBIRTH = 29
MIN_YEARS_BETWEEN_SIBLINGS = 1
MAX_YEARS_BETWEEN_SIBLINGS = 4
MIN_YEARS_ALIVE_AFTER_CHILDREN = 5
MAX_YEARS_ALIVE_AFTER_CHILDREN = 35

# some gender names to be picked out randomly

MALE_NAMES = ['Adam','Allan','Andy','Arthur','Billy','Brian','Barry','Bob','Bruce',
              'Calvin','Colin','Daryl','Drew','Edward','Ernest','Ethan','Fred','Frank',
              'Gaston','Gus','Harry','Hank','Ivan','Igor','Jack','Joe','Justin',
              'Kevin','Keith','Larry','Lionel','Louis','Leon','Mario','Melvin','Mark',
              'Norman','Neil','Oscar','Oliver','Paul','Perry','Quinn',
              'Randy','Robert','Ralph','Raju','Samuel','Scott','Shawn','Tom','Trevor','Todd',
              'Umberto','Vern','Victor','Walt','Winston','Wolfgang','Xavier','Yosif','Yuri',
              'Zeke','Zack']

FEMALE_NAMES = ['Alice','Alwyne','Amelia','Amy','Betty,','Beth','Bridget',
                'Carol','Connie','Cathy','Daisy','Darlene','Diana','Dora',
                'Elsie','Eliza','Emily','Eve','Fiona','Flora','Flo','Grace','Gloria','Gemma',
                'Helen','Heidi','Hope','Irene','Ivy','Iris','Jane','Judy','Jill','Jade','Joi',
                'Kate','Kathryn','Krista','Lauren','Louisa','Lily','Lucy','Lucia',
                'Mary','Martha','Marcy','Molly','Morgan','Nina','Nora','Olive','Octavia',
                'Patricia','Penelope','Rachel','Rose','Ruby','Ruth','Sarah','Sophia','Samantha',
                'Tiffany','Tilly','Ursula','Violet','Veronica','Winifred','Yvette','Yolonda',
                'Zoey','Zelda']

PARTNER_TYPES = ['wife', 'husb']


def header():
    print( '''0 HEAD
1 SOUR programrandomly
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
1 SUBM @SUB1@
0 @SUB1@ SUBM
1 NAME John Andrea''' )

def trailer():
    print( '0 TRLR' )


def make_gender():
    result = 'M'
    if random.random() > 0.5:
       result = 'F'
    return result


def gender_from_partner_type( t ):
    result = 'M'
    if t.lower() == 'wife':
       result = 'F'
    return result


def other_gender( g ):
    result = 'M'
    if g == 'M':
       result = 'F'
    return result


def make_surname( i ):
    return 'Surname' + '_' + str(i)


def random_name( names ):
    n = len( names )
    r = random.randint( 0, n-1 )
    n = names[r].strip()
    # protect against a name mistake in the constants
    if n:
      return n
    return 'Name'


def pick_a_name( g ):
    if g == 'M':
       return random_name( MALE_NAMES )
    return random_name( FEMALE_NAMES )


def make_person( surname, gender, birth, parent_fam, fam ):
    results = dict()
    results['givn'] = pick_a_name( gender )
    results['surn'] = surname
    results['gender'] = gender
    # existance of these tags becomes a flag because they are only created as needed
    if fam:
       results['fams'] = fam
    if parent_fam:
       results['famc'] = parent_fam
    if birth:
       results['birt'] = birth

    return results


def add_children( max_indi, n_indi, n_fam, n_surnames, parent_fam ):
   global indi_data
   global fam_data

   def add_parents_to_spouse( the_spouses, max_indi, n_indi, n_fam, n_surnames ):
       # always occurs

       birth_year = None

       for spouse in the_spouses:
           # collect them by type as added
           spouse_parents_by_type = dict()
           for partner_type in PARTNER_TYPES:
               n_indi += 1
               if n_indi <= max_indi:
                  spouse_parents_by_type[partner_type] = n_indi
                  gender = gender_from_partner_type( partner_type )

                  # husb gets surname from child
                  surname = indi_data[spouse]['surn']
                  if gender == 'F':
                    # wife gets a new one
                    n_surnames += 1
                    surname = make_surname( n_surnames )
                  indi_data[n_indi] = make_person( surname, gender, birth_year, None, None )
           # were any created
           if spouse_parents_by_type:
              n_fam += 1
              fam_data[n_fam] = dict()
              for spouse_parent_type in spouse_parents_by_type:
                  parent_id = spouse_parents_by_type[spouse_parent_type]
                  fam_data[n_fam][spouse_parent_type] = parent_id
                  indi_data[parent_id]['fams'] = n_fam
              # add the child to that family
              fam_data[n_fam]['chil'] = [spouse]
              # and vise versa
              indi_data[spouse]['famc'] = n_fam
       return [ n_indi, n_fam, n_surnames ]

   def add_siblings_to_spouse( the_spouses, max_indi, n_indi, n_fam, n_surnames ):
       birth_year = None

       for spouse in the_spouses:

           if INCLUDE_DATES:
              birth_year = indi_data[spouse]['birt']

           n_more = 0
           if random.random() >= ADD_SPOUSE_SIBLING:
              n_more += 1
           if random.random() >= SECOND_SPOUSE_SIBLING:
              n_more += 1

           for _ in range(n_more):
               n_indi += 1
               if n_indi <= max_indi:
                  surname = indi_data[spouse]['surn']
                  same_fam = indi_data[spouse]['famc']
                  gender = make_gender()

                  if INCLUDE_DATES:
                     birth_year += random.randint( MIN_YEARS_BETWEEN_SIBLINGS, MAX_YEARS_BETWEEN_SIBLINGS )

                  indi_data[n_indi] = make_person( surname, gender, birth_year, None, same_fam )
                  fam_data[same_fam]['chil'].append( n_indi )
       return [ n_indi, n_fam, n_surnames ]

   def add_grandparents_to_spouse( the_spouses, max_indi, n_indi, n_fam, n_surnames ):
       # don't bother adding dates for these grandparents
       birth_year = None

       # there is some code duplication here vs the spouse parent addition
       for spouse in the_spouses:
           # also check that parents exist, because max_indi might have been reached
           if random.random() >= SPOUSE_GRANDPARENTS and 'famc' in indi_data[spouse]:
              spouse_fam = indi_data[spouse]['famc']
              # collect parents by type
              spouse_parents = dict()
              for partner_type in PARTNER_TYPES:
                  if partner_type in fam_data[spouse_fam]:
                     spouse_parents[partner_type] = fam_data[spouse_fam][partner_type]
              # add the grandparent generaton to each parent
              for spouse_parent in spouse_parents:
                  # collect by type as they are added
                  spouse_grand = dict()
                  parent_id = spouse_parents[spouse_parent]
                  for partner_type in PARTNER_TYPES:
                      n_indi += 1
                      if n_indi <= max_indi:
                         spouse_grand[partner_type] = n_indi
                         gender = gender_from_partner_type( partner_type )
                         # husb gets surname from child
                         surname = indi_data[parent_id]['surn']
                         if gender == 'F':
                            # wife gets a new one
                            n_surnames += 1
                            surname = make_surname( n_surnames )
                         indi_data[n_indi] = make_person( surname, gender, birth_year, None, None )
                  # where any added
                  if spouse_grand:
                     n_fam += 1
                     fam_data[n_fam] = dict()
                     for grand in spouse_grand:
                         grand_id = spouse_grand[grand]
                         fam_data[n_fam][grand] = grand_id
                         # they are a partner in this family
                         indi_data[grand_id]['fams'] = n_fam
                     # child has this family of parents
                     indi_data[parent_id]['famc'] = n_fam
                     # and vise versa
                     fam_data[n_fam]['chil'] = [parent_id]
       return [ n_indi, n_fam, n_surnames ]

   def add_parent_dates( fam, date_child_1, date_child_n ):
       # to be called within an include-dates test
       # marriage and deaths depends on child births
       if random.random() >= ADD_MARRIAGE_DATE_PROB:
          # count backwards
          marr_date = date_child_1 - random.randint( 0, YEARS_MARRIED_BEFORE_CHILD )
          fam_data[fam]['marr'] = marr_date
          for partner_type in PARTNER_TYPES:
              if partner_type in fam_data[fam]:
                 if random.random() >= ADD_DEATH_PROB:
                    partner = fam_data[fam][partner_type]
                    death = date_child_n + random.randint( MIN_YEARS_ALIVE_AFTER_CHILDREN, MAX_YEARS_ALIVE_AFTER_CHILDREN )
                    indi_data[partner]['deat'] = death

   def add_spouse_parent_dates( the_spouses ):
       # to be called within an include-dates test
       for spouse in the_spouses:
           if 'famc' in indi_data[spouse]:
              fam = indi_data[spouse]['famc']
              first_sib_birth = None
              last_sib_birth = None
              if 'chil' in fam_data[fam]:
                 for child in fam_data[fam]['chil']:
                     birth = indi_data[child]['birt']
                     if first_sib_birth:
                        first_sib_birth = min( first_sib_birth, birth )
                        last_sib_birth = max( last_sib_birth, birth )
                     else:
                        first_sib_birth = birth
                        last_sib_birth = birth
                 # birth of mother first
                 partner_birth = None
                 if 'wife' in fam_data[fam]:
                    partner = fam_data[fam]['wife']
                    # count backwards
                    partner_birth = first_sib_birth - random.randint( MIN_AGE_FIRST_CHILDBIRTH, MAX_AGE_FIRST_CHILDBIRTH )
                    indi_data[partner]['birt'] = partner_birth
                 if 'husb' in fam_data[fam]:
                    partner = fam_data[fam]['husb']
                    indi_data[partner]['birt'] = partner_birth + random.randint( -AGE_DIFFER_FROM_SPOUSE, +AGE_DIFFER_FROM_SPOUSE )

                 # then marriage, etc.
                 add_parent_dates( fam, first_sib_birth, last_sib_birth )

   # stats
   gen_counts = [0]

   # set to nothing in case never used
   child_birth = None
   spouse_birth = None
   first_child_birth = None
   last_child_birth = None

   add_children_to_families = [parent_fam]

   while n_indi <= max_indi:
       next_gen_families = []

       # count created children
       n_created = 0

       for add_child_to_fam in add_children_to_families:
           # add some absolute limits on the number of children
           n_child = random.randint( max(1,MIN_CHILDREN), min(16,MAX_CHILDREN) )

           # surname from the father
           father = fam_data[add_child_to_fam]['husb']
           parent_surname = indi_data[father]['surn']

           if INCLUDE_DATES:
              # birth from mother, which might be None
              mother = fam_data[add_child_to_fam]['wife']
              mother_birth = indi_data[mother]['birt']
              # set the first child
              child_birth = mother_birth + random.randint( MIN_AGE_FIRST_CHILDBIRTH, MAX_AGE_FIRST_CHILDBIRTH )
              first_child_birth = child_birth

           fam_data[add_child_to_fam]['chil'] = []

           for _ in range(n_child):
               n_indi += 1
               if n_indi <= max_indi:
                  n_created += 1
                  gender = make_gender()
                  indi_data[n_indi] = make_person( parent_surname, gender, child_birth, add_child_to_fam, None )
                  # add child to parents
                  fam_data[add_child_to_fam]['chil'].append( n_indi )

               # next child
               if INCLUDE_DATES:
                  last_child_birth = child_birth
                  child_birth += random.randint( MIN_YEARS_BETWEEN_SIBLINGS, MAX_YEARS_BETWEEN_SIBLINGS )

           spouses = []

           # add a spouse to each new child
           for child in fam_data[add_child_to_fam]['chil']:
               n_indi += 1
               if n_indi <= max_indi:
                  spouses.append( n_indi )
                  n_fam += 1
                  fam_data[n_fam] = dict()

                  # handle this family in the next generation
                  next_gen_families.append( n_fam )

                  # add this family to the new child
                  indi_data[child]['fams'] = n_fam

                  # spouse gets a new surname
                  n_surnames += 1
                  surname = make_surname( n_surnames )

                  spouse_gender = other_gender( indi_data[child]['gender'] )

                  if INCLUDE_DATES:
                     child_birth = indi_data[child]['birt']
                     spouse_birth = child_birth + random.randint( -AGE_DIFFER_FROM_SPOUSE, +AGE_DIFFER_FROM_SPOUSE )

                  husb = n_indi
                  wife = child
                  if spouse_gender == 'F':
                     husb = child
                     wife = n_indi

                  indi_data[n_indi] = make_person( surname, spouse_gender, spouse_birth, None, n_fam )

                  fam_data[n_fam]['husb'] = husb
                  fam_data[n_fam]['wife'] = wife

           new_counts = add_parents_to_spouse( spouses, max_indi, n_indi, n_fam, n_surnames )
           n_indi = new_counts[0]
           n_fam = new_counts[1]
           n_surnames = new_counts[2]

           new_counts = add_siblings_to_spouse( spouses, max_indi, n_indi, n_fam, n_surnames )
           n_indi = new_counts[0]
           n_fam = new_counts[1]
           n_surnames = new_counts[2]

           new_counts = add_grandparents_to_spouse( spouses, max_indi, n_indi, n_fam, n_surnames )
           n_indi = new_counts[0]
           n_fam = new_counts[1]
           n_surnames = new_counts[2]

           if INCLUDE_DATES:
              add_parent_dates( add_child_to_fam, first_child_birth, last_child_birth )
              add_spouse_parent_dates( spouses )

       gen_counts.append( n_created )

       # run across the next generation, breath wise
       # deep copy (not pythonic)
       add_children_to_families = []
       for new_fam in next_gen_families:
           add_children_to_families.append( new_fam )

   return gen_counts


def make_xref( s, i ):
    return '@' + s.upper() + str(i) + '@'


def print_indi( d, stats ):
    print( '1 NAME', d['givn'], '/' + d['surn'] + '/' )
    print( '2 GIVN', d['givn'] )
    print( '2 SURN', d['surn'] )
    print( '1 SEX', d['gender'] )
    stats[d['gender']] += 1
    for item in ['fams','famc']:
        if item in d:
           print( '1', item.upper(), make_xref( 'f', d[item] ) )
    for item in ['birt','deat']:
        if item in d:
           value = d[item]
           stats['oldest'] = min( stats['oldest'], value )
           stats['newest'] = max( stats['newest'], value )
           print( '1', item.upper() )
           print( '2 DATE', value )

def print_fam( d ):
    for partner_type in PARTNER_TYPES:
        if partner_type in d:
           print( '1', partner_type.upper(), make_xref( 'i', d[partner_type] ) )
    if 'chil' in d:
       for child in d['chil']:
           print( '1 CHIL', make_xref( 'i', child ) )
    for item in ['marr']:
        if item in d:
           print( '1', item.upper() )
           print( '2 DATE', d[item] )


n = 10 #default minimum number of individuals

if len( sys.argv ) > 1:
   x = int(sys.argv[1])
   if x > n:
      n = x

# second option overrides date setting
if len( sys.argv ) > 2:
   option = sys.argv[2].lower().replace('-','').replace('_','').replace(' ','')
   if option in ['nodates','notdates']:
      INCLUDE_DATES = False
   if option == 'yesdates':
      INCLUDE_DATES = True


# build a generic data structure
indi_data = dict()
fam_data = dict()

# the top of the tree
# indi_xref will be the total person counter

indi_xref = 1
fam_xref = 1
surname_count = 1

birth = None
spouse_birth = None
if INCLUDE_DATES:
   birth = START_YEAR
   spouse_birth = birth + random.randint( -AGE_DIFFER_FROM_SPOUSE, +AGE_DIFFER_FROM_SPOUSE )

surname = make_surname( surname_count)
indi_data[indi_xref] = make_person( surname, 'M', birth, None, fam_xref )
parent1 = indi_xref

indi_xref += 1
surname_count += 1
surname = make_surname( surname_count )
indi_data[indi_xref] = make_person( surname, 'F', spouse_birth, None, fam_xref )

fam_data[fam_xref] = dict()
fam_data[fam_xref]['husb'] = parent1
fam_data[fam_xref]['wife'] = indi_xref
# marriage date added after children added

generation_stats = add_children( n, indi_xref, fam_xref, surname_count, fam_xref )

# all done with the ceation, output to gedcom format
header()

more_stats = dict()
more_stats['oldest'] = START_YEAR
more_stats['newest'] = START_YEAR
more_stats['F'] = 0
more_stats['M'] = 0

for indi in indi_data:
    print( '0', make_xref( 'i', indi ), 'INDI' )
    print_indi( indi_data[indi], more_stats )

for fam in fam_data:
    print( '0', make_xref( 'f', fam ), 'FAM' )
    print_fam( fam_data[fam] )

# stats to stderr
if INCLUDE_DATES:
   print( 'Date range:', more_stats['oldest'], more_stats['newest'], file=sys.stderr )
print( 'Genders:', 'F', more_stats['F'], 'M', more_stats['M'], file=sys.stderr )
print( 'Generation: Children; excluding spouses and spouse birth families.', file=sys.stderr )
for i,count in enumerate( generation_stats ):
    print( i, count, file=sys.stderr )

trailer()
