import requests

from typing import Annotated, Any
from fastapi import Depends

from netbox_proxbox.backend.routes.proxbox import netbox_settings
from netbox_proxbox.backend.schemas.netbox import NetboxSessionSchema
from netbox_proxbox.backend.exception import ProxboxException

# Netbox
import pynetbox

try:
    from netbox.settings import BASE_PATH
    DEFAULT_BASE_PATH = '/' + BASE_PATH
except ImportError:
    DEFAULT_BASE_PATH = ''
    
#
# NETBOX SESSION 
#
# TODO: CREATES SSL VERIFICATION - Issue #32
class NetboxSession:
    def __init__(self, netbox_settings):
        self.domain = netbox_settings.domain
        self.http_port = netbox_settings.http_port
        self.token = netbox_settings.token
        self.ssl = netbox_settings.ssl
        self.settings = netbox_settings.settings
        self.session = self.pynetbox_session()
        self.tag = self.proxbox_tag()
        
        
    def pynetbox_session(self):
        print("Establish Netbox connection...")
        try:
            # CHANGE SSL VERIFICATION TO FALSE
            session = requests.Session()
            session.verify = False
            
            netbox_session = pynetbox.api(
                    f'http://{self.domain}:{self.http_port}{DEFAULT_BASE_PATH}',
                    token=self.token,
                    threading=True,
            )
            # DISABLES SSL VERIFICATION
            netbox_session.http_session = session
            
            return netbox_session
        
        except Exception as error:
            raise RuntimeError(f"Error trying to initialize Netbox Session using TOKEN {self.token} provided.\nPython Error: {error}")
        
    def proxbox_tag(self):
            proxbox_tag_name = 'Proxbox'
            proxbox_tag_slug = 'proxbox'

            # Check if Proxbox tag already exists.
            proxbox_tag = self.session.extras.tags.get(
                name = proxbox_tag_name,
                slug = proxbox_tag_slug
            )

            if proxbox_tag is None:
                try:
                    # If Proxbox tag does not exist, create one.
                    tag = self.session.extras.tags.create(
                        name = proxbox_tag_name,
                        slug = proxbox_tag_slug,
                        color = 'ff5722',
                        description = "Proxbox Identifier (used to identify the items the plugin created)"
                    )
                except Exception as error:
                    raise ProxboxException(
                        message = f"Error creating the '{proxbox_tag_name}' tag. Possible errors: the name '{proxbox_tag_name}' or slug '{proxbox_tag_slug}' is already used.",
                        python_exception=f"{error}"
                    ) 
            else:
                tag = proxbox_tag

            return tag
        

async def netbox_session(
    netbox_settings: Annotated[NetboxSessionSchema, Depends(netbox_settings)],
):
    """Instantiate 'NetboxSession' class with user parameters and return Netbox  HTTP connection to make API calls"""
    return NetboxSession(netbox_settings)

# Make Session reusable
NetboxSessionDep = Annotated[Any, Depends(netbox_session)]