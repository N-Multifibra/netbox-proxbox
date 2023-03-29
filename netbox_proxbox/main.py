import uvicorn
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from netbox_proxbox import proxbox_api

# Import config
from .deploy_uvicorn import (
    fastapi_host,
    fastapi_port,
)

# PLUGIN_CONFIG variables
from .proxbox_api.plugins_config import (
    NETBOX_SESSION as nb,
    PROXMOX_SESSION as proxmox,
)

print(f"fastapi_host: {fastapi_host}")
print(f"fastapi_port: {fastapi_port}")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

from pathlib import Path
BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))


@app.get("/jinja", response_class=HTMLResponse)
async def jinja(request: Request):
    return templates.TemplateResponse("fastapi.html", {"request": request})


@app.get("/full_update")
async def full_update():
    json_result = await proxbox_api.update.all()
    return json_result

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("websocket.html",
        {
            "request": request,
            "fastapi_host": fastapi_host,
            "fastapi_port": fastapi_port,
        },
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    from .proxbox_api.plugins_config import (
        PROXMOX,
        PROXMOX_PORT,
        PROXMOX_USER,
        PROXMOX_PASSWORD,
        PROXMOX_SSL,
        NETBOX,
        NETBOX_TOKEN,
        PROXMOX_SESSION as proxmox,
        NETBOX_SESSION as nb,
    )

    from .proxbox_api import (
        updates,
        create,
        remove,
    )

    from .proxbox_api.update import (
        nodes,
        virtual_machine,
    )
    from .proxbox_api.create import extras 

    import logging

    await websocket.accept()
    while True:
        #data = await websocket.receive_text()

        #await websocket.send_text(f"Message text was: {data}")

        # Makes everything needed so that VIRTUAL MACHINES / CONTAINERS, NODES and CLUSTER exists on Netbox
        await websocket.send_text("teste websocket")
        print("[Proxbox - Netbox plugin | Update All]")
        cluster_all = proxmox.cluster.status.get()
        print(f"cluster_all: {cluster_all}")

        #
        # CLUSTER
        #
        print("pre-cluster")
        cluster = await create.virtualization.cluster()
        print('\n\n\nCLUSTER...')
        print(f"cluster: {cluster}")

        try:
            logging.info(f'[OK] CLUSTER created. -> {cluster.name}')
        except:
            logging.info(f"[OK] Cluster created. -> {cluster}")

        proxmox_cluster = cluster_all[0]
        #
        # NODES
        #
        await websocket.send_text("NODES...")
        print('\n\n\nNODES...')
        nodes_list = []
        proxmox_nodes = cluster_all[1:]

        # Get all NODES from Proxmox
        for px_node_each in proxmox_nodes:
            node_updated = await nodes(proxmox_json = px_node_each, proxmox_cluster = proxmox_cluster)
            await websocket.send_json(node_updated)
            nodes_list.append(node_updated)


        #
        # VIRTUAL MACHINES / CONTAINERS
        #
        await websocket.send_text("VIRTUAL MACHINES...")
        print('\n\n\nVIRTUAL MACHINES...')
        virtualmachines_list = []

        await websocket.send_text("UPDATE ALL...")
        print('\nUPDATE ALL...')
        # Get all VM/CTs from Proxmox
        for px_vm_each in proxmox.cluster.resources.get(type='vm'):     
            vm_updated = await virtual_machine(proxmox_json = px_vm_each)
            await websocket.send_json(vm_updated)
            virtualmachines_list.append(vm_updated)

        remove_unused = False
        #
        # 
        # Get "remove_unused" passed on function call
        # remove_unused = kwargs.get("remove_unused", False)
        #
        #

        # Remove Netbox's old data
        if remove_unused == True:
            await websocket.send_text("REMOVE UNUSED DATA...")
            print('\nREMOVE UNUSED DATA...')
            remove_info = await remove.all()
        else:
            remove_info = False
        #
        # BUILD JSON RESULT
        #
        result = {}
        result["virtualmachines"] = virtualmachines_list
        result["nodes"] = nodes_list
        result["remove_unused"] = remove_info

        websocket.close()