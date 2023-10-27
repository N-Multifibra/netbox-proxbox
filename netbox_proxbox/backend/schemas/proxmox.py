from pydantic import BaseModel, RootModel

from typing import List, Dict

from netbox_proxbox.backend.enum.proxmox import ResourceType

class ProxmoxTokenSchema(BaseModel):
    name: str
    value: str
    
class ProxmoxSessionSchema(BaseModel):
    domain: str
    http_port: int
    user: str
    password: str
    token: ProxmoxTokenSchema
    ssl: bool

ProxmoxMultiClusterConfig = RootModel[List[ProxmoxSessionSchema]]
  
class Resources(BaseModel):
    cgroup_mode: int = None
    content: str = None
    cpu: float = None
    disk: int = None
    hastate: str = None
    id: str
    level: str = None
    maxcpu: float = None
    maxdisk: int = None
    maxmem: int = None
    mem: int = None
    name: str = None
    node: str = None
    plugintype: str = None
    pool: str = None
    status: str = None
    storage: str = None
    type: ResourceType
    uptime: int = None
    vmid: int = None

ResourcesList = RootModel[List[Resources]]
ClusterResourcesList = RootModel[List[Dict[str, ResourcesList]]]
