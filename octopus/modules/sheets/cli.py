from octopus.lib import cli
from octopus.modules.sheets import commasep, sheets

from StringIO import StringIO
import argparse, json, codecs


class Csv(cli.Script):
    def run(self, argv):
        parser = argparse.ArgumentParser()

        parser.add_argument("-r", "--read", help="sheet read mode", action="store_true", default=False)
        parser.add_argument("-w", "--write", help="sheet write mode", action="store_true", default=False)
        parser.add_argument("-f", "--file", help="file path to read (source csv in read mode, or source json in write mode)")
        parser.add_argument("-d", "--data", help="input data string to read (source csv in read mode, or source json in write mode)")
        parser.add_argument("-o", "--out", help="file to output parsed json (read mode) or created csv (write mode)")
        parser.add_argument("-s", "--spec", help="file path to sheet spec description")
        parser.add_argument("-j", "--jspec", help="json string for sheet spec description")

        args = parser.parse_args(argv)

        if args.read and args.write:
            print "You can only specify one of --read or --write"
            parser.print_help()
            exit(0)

        if not args.read and not args.write:
            print "You must specify one of --read or --write"
            parser.print_help()
            exit(0)

        if args.file is not None and args.data is not None:
            print "You can only specify one of --file or --data"
            parser.print_help()
            exit(0)

        if args.file is None and args.data is None:
            print "You must specify one of --file or --data"
            parser.print_help()
            exit(0)

        if args.spec is not None and args.jspec is not None:
            print "You can only specify one of --spec or --jspec"
            parser.print_help()
            exit(0)

        if args.spec is None and args.jspec is None:
            print "You must specify one of --spec or --jspec"
            parser.print_help()
            exit(0)

        raw_spec = args.jspec
        if args.spec:
            with codecs.open(args.spec) as f:
                raw_spec = f.read()
        spec = json.loads(raw_spec)

        if args.read:
            path_or_handle = args.file
            if args.data is not None:
                path_or_handle = StringIO(args.data)

            reader = commasep.CsvReader(path_or_handle)
            s = sheets.ObjectByRow(reader=reader, spec=spec)

            output = json.dumps(s.dicts())

            if args.out is not None:
                with codecs.open(args.out, "wb") as f:
                    f.write(output)
            else:
                print output

        elif args.write:
            writer = None
            output = None
            if args.out is not None:
                writer = commasep.CsvWriter(args.out)
            else:
                output = StringIO()
                writer = commasep.CsvWriter(output)

            raw_json = args.data
            if args.file is not None:
                with codecs.open(args.file) as f:
                    raw_json = f.read()
            data = json.loads(raw_json)

            s = sheets.ObjectByRow(writer=writer, spec=spec)
            s.set_dicts(data)
            s.write(close=False)

            if args.out is None:
                print output.getvalue()