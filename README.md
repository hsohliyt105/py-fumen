# py-fumen
Python implementation of knewjade's fumen

# Installation 
Enter `pip install py-fumen` in terminal / cmd if you have python3 already.

# Uses
The usage of this package is very similar to the original fumen package.

## Decode
```
from py_fumen import decode

decode_pages = decode("v115@vhHJEJWPJyKJz/I1QJUNJvIJAgH")

for page in decode_pages:
    print(page.get_field().string())
```

## Encode
```
from py_fumen import Field, Page, encode, create_inner_field

pages = []
pages.append(
    Page(field=create_inner_field(Field.create(
        'LLL_____SS' +
        'LOO____SST' +
        'JOO___ZZTT' +
        'JJJ____ZZT',
        '__________',
    )),
    comment='Perfect Clear Opener'))

print(encode(pages))
```

# Difference between the knewjade's fumen
Some of functions and variables are non-private because of the disparity between python and typescript (e.g. quiz variable in the Quiz class).

Function and varibale names are changed with python naming convention.

create_inner_field function and create_new_inner_field are moved to field.py because of cross importing issue.

page.py is created for better OOP.

js_escape.py is added to imitate javascript's escape/unescape.

buffer.ts is renamed to fumen_buffer.py and Buffer object to FumenBuffer.

getters and setters are changed into methods (e.g. Page.get_field()). 
