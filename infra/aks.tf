resource "random_id" "acr_suffix" {
  byte_length = 3
}

resource "azurerm_container_registry" "main" {
  name                = "acr${var.project}${random_id.acr_suffix.hex}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
}

resource "azurerm_kubernetes_cluster" "main" {
  name                = "aks-${var.project}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "aks-${var.project}"

  default_node_pool {
    name           = "default"
    node_count     = 1
    vm_size        = var.aks_node_vm_size
    vnet_subnet_id = azurerm_subnet.aks.id
  }

  identity {
    type = "SystemAssigned"
  }

  # Azure enables this by default on new clusters and it cannot be turned
  # back off once on -- declared explicitly so Terraform stops trying to
  # "correct" a setting that was never actually wrong.
  oidc_issuer_enabled = true
}

# Lets AKS pull images from this ACR without a separate registry secret --
# the same effect as `az aks update --attach-acr` from Day 10, as code.
resource "azurerm_role_assignment" "aks_acr_pull" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}
