from pydantic import BaseModel

from netbox_proxbox.backend.schemas.netbox.extras import TagSchema
from netbox_proxbox.backend.enum.netbox.virtualization import ClusterStatusOptions


class ClusterTypeSchema(BaseModel):
    name: str
    slug: str
    description: str | None = None
    tags: list[TagSchema] | None = None
    custom_fields: dict | None = None

class ClusterSchema(BaseModel):
    name: str
    type: int
    group: int | None = None
    site: int | None = None
    status: ClusterStatusOptions
    tenant: int | None = None
    description: str | None = None
    comments: str | None = None
    tags: list[TagSchema] | None = None
    custom_fields: dict | None = None
    