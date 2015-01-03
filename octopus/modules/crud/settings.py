# Define the CRUD mappings from URL routes to the model objects they represent
CRUD = {}

"""
e.g.
CRUD = {
    "payment" : {
        "model" : "service.models.CRUDPayment",
        "create" : {
            "enable" : True
        },
        "retrieve" : {
            "enable" : True
        },
        "update" : {
            "enable" : True
        },
        "delete" : {
            "enable" : True
        }
    }
}
"""