import typer

from proxbox_api.database import NetBoxEndpoint, engine
from sqlmodel import select, Session

app = typer.Typer()

@app.command()
def netbox(json: bool = False):
    with Session(engine) as session:
        statement = select(NetBoxEndpoint).offset(0).limit(100)
        netbox_endpoints = session.exec(statement=statement).all()
        
        for nb in netbox_endpoints:
            if json:
                print(nb.model_dump())
            else:
                print(f'[NetBox Endpoint]\nID: {nb.id}\nName: {nb.name}\nIP Address: {nb.ip_address}\nPort: {nb.port}\nToken: {nb.token}\nVerify SSL: {nb.verify_ssl}')

if __name__ == '__main__':
    app()