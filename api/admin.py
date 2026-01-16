from sqladmin import Admin

from models import Property, PropertyImage


def setup_admin(app, engine):
    admin = Admin(app, engine)

    # минимальные ModelView (sqladmin можно расширять позже)
    from sqladmin import ModelView

    class PropertyAdmin(ModelView, model=Property):
        column_list = [
            Property.id,
            Property.city,
            Property.district,
            Property.type,
            Property.price,
            Property.area_m2,
            Property.rooms,
            Property.is_active,
            Property.created_at,
        ]
        name = "Property"
        name_plural = "Properties"

    class PropertyImageAdmin(ModelView, model=PropertyImage):
        column_list = [PropertyImage.id, PropertyImage.property_id, PropertyImage.url, PropertyImage.sort_order, PropertyImage.is_cover]
        name = "Image"
        name_plural = "Images"

    admin.add_view(PropertyAdmin)
    admin.add_view(PropertyImageAdmin)
