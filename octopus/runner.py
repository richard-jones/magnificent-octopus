def start_from_main(app):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="start in debug for pycharm mode if defined")
    args = parser.parse_args()

    host = app.config.get("HOST", "0.0.0.0")
    debug = app.config.get("DEBUG", False)
    port = app.config.get("PORT", 5000)
    threaded = app.config.get("THREADED", False)

    if args.debug:
        print "STARTING WITH DEBUG SERVER SUPPORT"
        import octopus.lib.pycharm
        debug = False
        threaded = False

    app.run(host=host, debug=debug, port=port, threaded=threaded)