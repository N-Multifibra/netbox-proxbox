from typing import Annotated

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from netbox_proxbox.backend.exception import ProxboxException

# Netbox Routes
from .backend.routes.netbox import router as netbox_router
from .backend.routes.netbox.dcim import router as nb_dcim_router
from .backend.routes.netbox.virtualization import router as nb_virtualization_router

# Proxbox Routes
from .backend.routes.proxbox import router as proxbox_router

# Proxmox Routes
from .backend.routes.proxmox import router as proxmox_router
from .backend.routes.proxmox.cluster import router as px_cluster_router
from .backend.routes.proxmox.nodes import router as px_nodes_router


from .backend.schemas import *

PROXBOX_PLUGIN_NAME = "netbox_proxbox"

# Init FastAPI
app = FastAPI()

@app.exception_handler(ProxboxException)
async def proxmoxer_exception_handler(request: Request, exc: ProxboxException):
    return JSONResponse(
        status_code=400,
        content={
            "message": exc.message,
            "detail": exc.detail,
            "python_exception": exc.python_exception,
        }
    )


#
# Routes (Endpoints)
#
app.include_router(netbox_router, prefix="/netbox", tags=["netbox"])
app.include_router(nb_dcim_router, prefix="/netbox/dcim", tags=["netbox / dcim"])
app.include_router(nb_virtualization_router, prefix="/netbox/virtualization", tags=["netbox / virtualization"])

app.include_router(proxbox_router, prefix="/proxbox", tags=["proxbox"])
app.include_router(px_nodes_router, prefix="/proxmox/nodes", tags=["proxmox / nodes"])
app.include_router(px_cluster_router, prefix="/proxmox/cluster", tags=["proxmox / cluster"])
app.include_router(proxmox_router, prefix="/proxmox", tags=["proxmox"])




@app.get("/")
async def standalone_info():
    return {
        "message": "Proxbox Backend made in FastAPI framework",
        "proxbox": {
            "github": "https://github.com/netdevopsbr/netbox-proxbox",
            "docs": "https://docs.netbox.dev.br",
        },
        "fastapi": {
            "github": "https://github.com/tiangolo/fastapi",
            "website": "https://fastapi.tiangolo.com/",
            "reason": "FastAPI was chosen because of performance and reliabilty."
        }
    }

