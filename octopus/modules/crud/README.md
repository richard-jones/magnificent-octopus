# CRUD

This module allows you to expose any existing objects (via a thin facade) in your system via a RESTful CRUD (Create, Retrieve, Update, Delete) API.

## Creating a compliant model object:

Create a model object which conforms to the **octopus.modules.crud.models.CRUDObject** interface:

```python
    class CRUDObject(object):
    
        @classmethod
        def pull(cls, id)           # retrieve an instance of the object by id
        
        @property
        def id(self)                # retrieve the id of this instance of the object
    
        def save(self)              # save this object
        def json(self)              # get a JSON representation of this object
        def update(self, data)      # update the current data of this object with this new data
        def delete(self)            # delete this object from the system
 ```
 
This, can, for example, be a proxy or decorator for your actual model object.

If you are using the ESDAO model objects from **octopus.modules.es.dao**, then this is very simple.  You can instead use
**octopus.modules.crud.models.ES_CRUD_Wrapper**, as follows

```python
    class MyCRUDObject(ES_CRUD_Wrapper):
        INNER_TYPE = MyObject
```

MyObject is your actual model which extends the ESDAO, and an instance of it will be created and stored in self.inner on the instantiated crud object.  

The only enhancements you may wish to make are to the \__init__() and update() methods, if there are values which may come 
in via the REST API which you want to protect.  For example, if you don't want the REST API being able to overwrite the "id", 
"created_date" or "last_updated" fields, use something like:

```python
    class MyCRUDObject(ES_CRUD_Wrapper):
        INNER_TYPE = MyObject
    
        def __init__(self, raw=None):
            if raw is not None:
                # remove any disallowed fields
                if "id" in raw:
                    del raw["id"]
                if "created_date" in raw:
                    del raw["created_date"]
                if "last_updated" in raw:
                    del raw["last_updated"]
    
            super(MyCRUDObject, self).__init__(raw)
    
        def update(self, data):
            # carry over the data from the old object
            data["id"] = self.inner.id
            data["created_date"] = self.inner.created_date
    
            # remove any disallowed fields
            if "last_updated" in data:
                del data["last_updated"]
    
            super(MyCRUDObject, self).update(data)
```

## Configuring the CRUD interface
 
The CRUD interface for an object has to be explicitly enabled, which can be done with the following setting:

```python
    CRUD = {
        "myobject" : {
            "model" : "service.models.MyCRUDObject",
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
```

Note that you can enable/disable each of the CRUD operations independently according to your needs.  Methods are
disabled by default, so you must explicitly enable them if you want to use them.


## Mounting the blueprint

Finally, to enable the CRUD endpoint, mount the blueprint in your service/web.py:

```python
    from octopus.modules.crud.api import blueprint as crud
    app.register_blueprint(crud, url_prefix="/api")
```

You can now access and send data to urls like

    GET /api/myobject/123456
    POST /api/myobject [data]
