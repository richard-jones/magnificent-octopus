# Define the CRUD mappings from URL routes to the model objects they represent
CRUD = {}

"""
e.g.
CRUD = {
    "payment" : {
        "model" : "service.models.CRUDPayment",
        "create" : {
            "enable" : True,
            "auth" : True,
            "roles" : []
        },
        "retrieve" : {
            "enable" : True,
            "auth" : True,
            "roles" : []
        },
        "update" : {
            "enable" : True,
            "auth" : True,
            "roles" : []
        },
        "delete" : {
            "enable" : True,
            "auth" : True,
            "roles" : []
        }
    }
}
"""

CLIENTJS_CRUD_ENDPOINT = "/api"