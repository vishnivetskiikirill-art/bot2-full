from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from .models import Property, PropertyImage
from .settings import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if username == settings.ADMIN_USER and password == settings.ADMIN_PASS:
            request.session.update({"user": username})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("user"))


class PropertyAdmin(ModelView, model=Property):
    name = "Property"
    name_plural = "Properties"

    column_list = [
        Property.id,
        Property.price,
        Property.area_m2,
        Property.rooms,
        Property.lat,
        Property.lng,
        Property.is_active,
        Property.created_at,
    ]
    column_sortable_list = [
        Property.id,
        Property.price,
        Property.area_m2,
        Property.rooms,
        Property.created_at,
    ]
    column_searchable_list = [Property.description]

    form_columns = [
        "price",
        "area_m2",
        "rooms",
        "lat",
        "lng",
        "description",
        "is_active",
    ]


class PropertyImageAdmin(ModelView, model=PropertyImage):
    name = "Property Image"
    name_plural = "Property Images"

    column_list = [
        PropertyImage.id,
        PropertyImage.property_id,
        PropertyImage.url,
        PropertyImage.sort_order,
        PropertyImage.is_cover,
    ]
    column_sortable_list = [
        PropertyImage.id,
        PropertyImage.property_id,
        PropertyImage.sort_order,
    ]
    form_columns = [
        "property_id",
        "url",
        "sort_order",
        "is_cover",
    ]


def setup_admin(app, engine):
    auth = AdminAuth(secret_key=settings.SESSION_SECRET)
    admin = Admin(app, engine, authentication_backend=auth)

    admin.add_view(PropertyAdmin)
    admin.add_view(PropertyImageAdmin)

    return admin
