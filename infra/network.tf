resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

# --- Hub ---------------------------------------------------------------
resource "azurerm_virtual_network" "hub" {
  name                = "${var.project}-hub-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

# --- Spoke ---------------------------------------------------------------
resource "azurerm_virtual_network" "spoke" {
  name                = "${var.project}-spoke-vnet"
  address_space       = ["10.1.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "aks" {
  name                 = "snet-aks"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.spoke.name
  address_prefixes     = ["10.1.1.0/24"]
}

resource "azurerm_subnet" "pe" {
  name                 = "snet-pe"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.spoke.name
  address_prefixes     = ["10.1.2.0/24"]

  # Postgres Flexible Server uses VNet integration (a subnet delegated
  # directly to it), NOT the Private Endpoint mechanism Day 12 taught for
  # Storage -- same private-only OUTCOME, different underlying Azure
  # mechanism. This delegation hands the subnet over exclusively to
  # Postgres Flexible Server.
  delegation {
    name = "postgres-delegation"
    service_delegation {
      name    = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

# --- Peering, both directions (Day 12's exact pattern) --------------------
resource "azurerm_virtual_network_peering" "hub_to_spoke" {
  name                      = "hub-to-spoke"
  resource_group_name       = azurerm_resource_group.main.name
  virtual_network_name      = azurerm_virtual_network.hub.name
  remote_virtual_network_id = azurerm_virtual_network.spoke.id
}

resource "azurerm_virtual_network_peering" "spoke_to_hub" {
  name                      = "spoke-to-hub"
  resource_group_name       = azurerm_resource_group.main.name
  virtual_network_name      = azurerm_virtual_network.spoke.name
  remote_virtual_network_id = azurerm_virtual_network.hub.id
}

# --- NSGs -------------------------------------------------------------
resource "azurerm_network_security_group" "aks" {
  name                = "nsg-snet-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowVnetInBound"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "VirtualNetwork"
  }

  # The Standard-tier Azure Load Balancer behind the Ingress controller's
  # LoadBalancer Service lives OUTSIDE this subnet and forwards traffic to
  # the AKS nodes on their NodePorts. AKS only auto-manages inbound rules
  # on an NSG it creates itself -- ours is a hand-authored one attached to
  # a hub-spoke subnet, so those rules never get injected. Real symptom
  # hit without this: the LB got a public IP, but curl to it timed out
  # (exit 28) with no response at all. Two rules are needed: the LB's own
  # health probes (source tag AzureLoadBalancer) and the actual forwarded
  # client traffic (source tag Internet), both against AKS's default
  # NodePort range.
  security_rule {
    name                       = "AllowLoadBalancerProbeInBound"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "30000-32767"
    source_address_prefix      = "AzureLoadBalancer"
    destination_address_prefix = "VirtualNetwork"
  }

  security_rule {
    name                       = "AllowInternetToNodePortInBound"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "30000-32767"
    source_address_prefix      = "Internet"
    destination_address_prefix = "VirtualNetwork"
  }
}

resource "azurerm_subnet_network_security_group_association" "aks" {
  subnet_id                 = azurerm_subnet.aks.id
  network_security_group_id = azurerm_network_security_group.aks.id
}

resource "azurerm_network_security_group" "pe" {
  name                = "nsg-snet-pe"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowVnetInBound"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "VirtualNetwork"
  }
}

resource "azurerm_subnet_network_security_group_association" "pe" {
  subnet_id                 = azurerm_subnet.pe.id
  network_security_group_id = azurerm_network_security_group.pe.id
}
