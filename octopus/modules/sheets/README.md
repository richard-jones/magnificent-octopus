# Sheets Module

This module aids in the reading/writing of tabular/spreadsheet data.

## Readers and Writers

These are classes which allow data to be read and written to underlying storage, through the appropriate format.

### CSVs

The following 2 classes can be used for reading/writing CSVs

    octopus.modules.sheets.commasep.CsvReader
    octopus.modules.sheets.commasep.CsvWriter
    
Either of them can be constructed around a file path or a file-like object (something which supports "read" or "write")

    reader = CsvReader("path/to/file.csv")
    
    with codecs.open("path/to/file.csv", "wb") as file_handle:
        writer = CsvWriter(file_handle)

Note that as part of the point of the CSV reader is to handle file encodings, overall you're better giving it a file
and letting it work out the correct encoding.


## Structural Sheets

These are classes which allow tabular data, as read by a Reader, to be interpreted with a particular structure.

### Object By Row

This class can be used to read a sheet such that each row is an object with the first row defining the keys

    octopus.modules.sheets.sheets.ObjectByRow

In order for this class to function, it needs to be told the shape of the sheet to read, with a sheet spec.  This is of the following form:

    {
        "from_row" : 0,
        "to_row" : -1,
        "from_col" : 0,
        "to_col" : -1,
        "ignore_empty_rows" : true,
        "columns" : [
            {
                "col_name" : "DOI",
                "trim" : true,
                "normalised_name" : "doi",
                "default" : null,
                "coerce" : ["unicode"],
                "ignore_values" : [],
                "to_unicode" : "unicode"
            },
            ... etc ...
        ]
    }

For each column the following properties may be set:

* col_name - this is the name of the column as it appears in the incoming sheet, or should appear in a sheet being written
* trim - should whitespace be trimmed from around values found in this column
* normalised_name - this is the name of the column as it will be used in code.  Incoming sheets will have their matching col_names converted to this value, and vice-versa when being written
* default - the default value for fields in this column, if the content is considered empty
* coerce - a list of named functions from the coerce library which should be run on the data in the column sequentially during read
* ignore_values - a list of values which, if found in this field, will be considered equal to the empty string.  They may in turn be overwritten by the default value
* to_unicode - a named function from the coerce library which will convert the value in the data to a unicode string for writing to an output sheet


## CLI

### CSV

To run a conversion of data from the command line, use the "csv" run command on the octopus runner:

    python magnificent-octopus/octopus/bin/run.py csv
    
This can be used as follows:

    usage: run.py [-h] [-r] [-w] [-f FILE] [-d DATA] [-o OUT] [-s SPEC] [-j JSPEC]
    
    optional arguments:
      -h, --help            show this help message and exit
      -r, --read            sheet read mode
      -w, --write           sheet write mode
      -f FILE, --file FILE  file path to read (source csv in read mode, or source
                            json in write mode)
      -d DATA, --data DATA  input data string to read (source csv in read mode, or
                            source json in write mode)
      -o OUT, --out OUT     file to output parsed json (read mode) or created csv
                            (write mode)
      -s SPEC, --spec SPEC  file path to sheet spec description
      -j JSPEC, --jspec JSPEC
                            json string for sheet spec description
                            
So to read a sheet, use:
                            
    python magnificent-octopus/octopus/bin/run.py csv -r -f /path/to/file.csv -o out.json -s /path/to/spec.json
    
Similarly, to convert some json back to a sheet

    python magnificent-octopus/octopus/bin/run.py csv -w -f /path/to/file.json -o out.csv -s /path/to/spec.json
