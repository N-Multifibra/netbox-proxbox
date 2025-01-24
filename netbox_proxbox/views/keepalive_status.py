# Django Imports
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.urls import reverse
import requests

# Django-HTMX Imports
from django_htmx.middleware import HtmxDetails
from django_htmx.http import replace_url

class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails

from netbox_proxbox.models import *

@require_GET
def get_service_status(
    request: HtmxHttpRequest,
    service: str,
    pk: int,
) -> HttpResponse:
    """Get the status of a service."""
    def get_request(url: str):
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.SSLError as err:
            print(f'SSL error ocurred: {err}')
            response = get_request(url=url.replace('https://', 'http://'))
            if response:
                return response
        
        except requests.exceptions.HTTPError as err:
            print(f'HTTP error ocrrured: {err}')
            
        except Exception as err:
            print(f'Error ocurred: {err}')
        
        return None
        
    
    
    template_name: str = 'netbox_proxbox/status_badge.html'
    
    # Accept only HTMX requests to render this view.
    if not request.htmx:
        return HttpResponse(status=400)
    
    host: str = ''
    url: str = ''
    status: str = 'unknown'
    
    if service == 'fastapi':
        fastapi_service_obj = FastAPIEndpoint.objects.get(pk=pk)
    else:
        fastapi_service_obj = FastAPIEndpoint.objects.first()
    
    if fastapi_service_obj:
        host = str(fastapi_service_obj.ip_address.address).split('/')[0]
        url: str = f"https://{host}:{fastapi_service_obj.port}"
    
    if service == 'proxmox':
        proxmox_service_obj = ProxmoxEndpoint.objects.get(pk=pk)
            
        if proxmox_service_obj:
            proxmox_host: str = str(proxmox_service_obj.ip_address).split('/')[0]
            url = f'{url}/proxmox/version?ip_address={proxmox_host}&port={proxmox_service_obj.port}'
        
    if service == 'netbox':
        netbox_service_obj = NetBoxEndpoint.objects.get(pk=pk)
        netbox_ip = str(netbox_service_obj.ip_address.address).split('/')[0]
        
        netbox_endpoint_url = f'{url}/netbox/endpoint'
        
        # Check if NetBoxEndpoint exists on FastAPI database
        response = get_request(netbox_endpoint_url)
        if response:
            status = 'success'
            
        netbox = None
        
        if len(response) > 0:
            for nb in response:
                if (nb['id'] == pk) and (nb['ip_address'] == netbox_ip):
                    netbox = nb
                    break
            
            if netbox:
                # Delete all NetBoxEndpoints from FastAPI database, except the one that matches the current NetBoxEndpoint.
                for nb in response:
                    if nb['id'] != pk:
                        requests.delete(f'{netbox_endpoint_url}/{nb["id"]}')
            else:
                # Delete all NetBoxEndpoints from FastAPI database.
                for nb in response:
                    requests.delete(f'{netbox_endpoint_url}/{nb["id"]}')
        
        if netbox:
            # NetBoxEndpoint exists on FastAPI database. Check if it is alive.
            url = f'{url}/netbox/status'
        else:
            # Create NetBoxEndpoint on FastAPI database.
            requests.post(netbox_endpoint_url, json={
                'id': pk,
                'name': netbox_service_obj.name,
                'ip_address': netbox_ip,
                'port': netbox_service_obj.port,
                'token': netbox_service_obj.token
            })
            
    response = get_request(url)
    if response:
        status = 'success'
    else:
        status = 'error'
    
    return render(
        request,
        template_name,
        {
            'status': status
        }
    )
 