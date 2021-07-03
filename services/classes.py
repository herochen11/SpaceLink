from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom, RelatedObjects


class User(GraphObject):
    __primarylabel__ = "user"
    __primarykey__ = "email"
    UID = Property()
    username = Property()
    name = Property()
    email = Property()
    password = Property()
    affiliation = Property()
    title = Property()
    country = Property()
    hashed_password = Property()
    created_on = Property()
    last_logon = Property()
    project_priority = Property() # 0331
    UhaveE = RelatedTo("Equipments","OWNER")
    Manage = RelatedTo("Projects","OWN")   

class Equipments(GraphObject):
    __primarylabel__ = "equipments"
    __primarykey__ = "EID"
    EID = Property()
    aperture = Property()
    Fov = Property()
    pixel_scale = Property()
    tracking_accurcay = Property()
    lim_magnitude = Property()
    elevation_lim = Property()
    mount_type = Property()
    camera_type1 = Property()
    camera_type2 = Property()
    JohnsonB = Property()
    JohnsonV = Property()
    JohnsonR = Property()
    SDSSu = Property()
    SDSSg = Property()
    SDSSr = Property()
    SDSSi = Property()
    SDSSz =Property()
    owner = RelatedFrom(User,"UHAVEE")

class Target(GraphObject):
    __primarylabel__ ="target"
    __primarykey__ ="TID"
    TID = Property()
    name = Property()
    longitude = Property()
    latitude = Property()

class Project(GraphObject):
    __primarylabel__ = "project"
    __primarykey__ = "PID"
    PID = Property()
    title = Property()
    project_type = Property()
    PI = Property()
    description = Property()
    aperture_upper_limit = Property()
    aperture_lower_limit = Property()
    FoV_upper_limit = Property()
    FoV_lower_limit = Property()
    pixel_scale_upper_limit = Property()
    pixel_scale_lower_limit = Property()
    mount_type = Property()
    camera_type1 = Property()
    camera_type2 = Property()
    JohnsonB = Property()
    JohnsonV = Property()
    JohnsonR = Property()
    SDSSu = Property()
    SDSSg = Property()
    SDSSr = Property()
    SDSSi = Property()
    SDSSz =Property()
    own = RelatedFrom(User,"MANAGE")

class Schedule(GraphObject):
    __primarylabel__ = "schedule"
    __primarykey__ = "SID"
    SID = Property()
    last_update = Property()
    observe_section = Property()
