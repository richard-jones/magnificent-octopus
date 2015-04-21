def print_config():
    from octopus.core import app
    keys = app.config.keys()
    keys.sort()
    for k in keys:
        v = app.config.get(k)
        print k, "=", v

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", action="store_true", help="print the system configuration")
    args = parser.parse_args()

    if args.config:
        print_config()
    else:
        parser.print_help()
