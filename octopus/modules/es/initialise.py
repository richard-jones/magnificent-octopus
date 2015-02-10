import esprit
from octopus.lib import plugin
from octopus.core import app

def initialise():
    # if we are not to initialise the index, stop here
    if not app.config.get("INITIALISE_INDEX", False):
        return

    # create the index itself if it needs creating
    conn = esprit.raw.Connection(app.config['ELASTIC_SEARCH_HOST'], app.config['ELASTIC_SEARCH_INDEX'])
    if not esprit.raw.index_exists(conn):
        print "Creating ES Index; host:" + str(conn.host) + " port:" + str(conn.port) + " db:" + str(conn.index)
        esprit.raw.create_index(conn)
    else:
        print "ES Index Already Exists; host:" + str(conn.host) + " port:" + str(conn.port) + " db:" + str(conn.index)

    # get the list of classes which carry the mappings to be loaded
    mapping_daos = app.config.get("ELASTIC_SEARCH_MAPPINGS", [])

    # get the ES version that we're working with
    es_version = app.config.get("ELASTIC_SEARCH_VERSION", "0.90.13")

    # load each class and execute the "mappings" function to get the mappings
    # that need to be imported
    for cname in mapping_daos:
        klazz = plugin.load_class_raw(cname)
        mappings = klazz.mappings()

        # for each mapping (a class may supply multiple), create them in the index
        for key, mapping in mappings.iteritems():
            if not esprit.raw.type_exists(conn, key):   # FIXME: check this behaves the same in ES 0.x and 1.x
                r = esprit.raw.put_mapping(conn, key, mapping, es_version=es_version)
                print "Creating ES Type+Mapping for", key, "; status:", r.status_code
            else:
                print "ES Type+Mapping already exists for ", key