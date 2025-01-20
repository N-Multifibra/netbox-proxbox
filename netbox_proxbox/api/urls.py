from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'proxbox'

router = NetBoxRouter()
router.register('endpoints/proxmox', views.ProxmoxEndpointViewSet)
router.register('endpoints/netbox', views.NetBoxEndpointViewSet)

urlpatterns = router.urls