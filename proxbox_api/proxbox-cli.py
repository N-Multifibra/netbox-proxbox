import typer

from proxbox_api.database import NetBoxEndpoint, engine
from sqlmodel import select, Session
import requests

app = typer.Typer()

def get_netbox() -> NetBoxEndpoint:
    with Session(engine) as session:
        statement = select(NetBoxEndpoint).offset(0).limit(100)
        netbox_endpoints = session.exec(statement=statement).all()
        
        return netbox_endpoints[0]
    
@app.command()
def netbox(json: bool = False):
    nb = get_netbox()
    
    if json:
        print(nb.model_dump())
    else:
        print(f'[NetBox Endpoint]\nID: {nb.id}\nName: {nb.name}\nIP Address: {nb.ip_address}\nPort: {nb.port}\nToken: {nb.token}\nVerify SSL: {nb.verify_ssl}')

                

@app.command()
def proxmox(json: bool = False):
    nb = get_netbox()
    try:
        url: str = f'http://{nb.ip_address}:{nb.port}/api/plugins/proxbox/endpoints/proxmox'
        proxmox = requests.get(url, headers={'Authorization': f'Token {nb.token}'})
        proxmox.raise_for_status()
        proxmox = proxmox.json()
        
        if json:
            print(proxmox)
        
        else:
            endpoints: list = proxmox.get('results')
            print(f'[Proxmox Endpoints]')
            for endpoint in endpoints:
                name = endpoint.get('name')
                ip_address = endpoint['ip_address']['address']
                port = endpoint['port']
                print(f'{name} ({ip_address}:{port})')
                
    except requests.exceptions.HTTPError as err:
        print(proxmox, err)
    

if __name__ == '__main__':
    app()