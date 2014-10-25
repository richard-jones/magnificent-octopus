import esprit
from portality.lib import plugin

def initialise(app):
    # if we are not to initialise the index, stop here
    if not app.config.get("INITIALISE_INDEX", False):
        return

    # create the index itself if it needs creating
    conn = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_INDEX'])
    if not esprit.raw.index_exists(conn):
        print "Creating Index; host:" + str(conn.host) + " port:" + str(conn.port) + " db:" + str(conn.index)
        esprit.raw.create_index(conn)

    # get the list of classes which carry the mappings to be loaded
    mapping_daos = app.config.get("ELASTIC_SEARCH_MAPPINGS", [])

    # load each class and execute the "mappings" function to get the mappings
    # that need to be imported
    for cname in mapping_daos:
        klazz = plugin.load_class_raw(cname)
        mappings = klazz.mappings()

        # for each mapping (a class may supply multiple), create them in the index
        for key, mapping in mappings.iteritems():
            if not esprit.raw.has_mapping(conn, key):
                r = esprit.raw.put_mapping(conn, key, mapping)
                print key, r.status_code