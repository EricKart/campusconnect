# --- Private DNS zone Postgres Flexible Server needs for VNet integration.
# Azure requires the zone name to end in "postgres.database.azure.com" --
# this is the standard, documented pattern (same one used even though this
# is VNet integration, not Private Link/Private Endpoint).
resource "azurerm_private_dns_zone" "postgres" {
  name                = "privatelink.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  name                  = "postgres-dns-link"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.postgres.name
  virtual_network_id    = azurerm_virtual_network.spoke.id
}

# Alphanumeric-only on purpose. A password containing "@" broke the
# connection-string URL parser (it read part of the password as the host);
# percent-encoding it (%40) then broke Alembic's config parser too (it
# treats "%" as interpolation syntax). Rather than patch every downstream
# parser that trips over a URL-reserved character, generate a password with
# none in it -- the actually-robust fix.
resource "random_password" "postgres_admin" {
  length  = 24
  special = false
}

resource "azurerm_postgresql_flexible_server" "main" {
  name                = "psql-${var.project}"
  resource_group_name = azurerm_resource_group.main.name
  location             = azurerm_resource_group.main.location

  version                = "16"
  administrator_login    = "ccadmin"
  administrator_password = random_password.postgres_admin.result

  storage_mb = 32768
  sku_name   = "B_Standard_B1ms"

  delegated_subnet_id           = azurerm_subnet.pe.id
  private_dns_zone_id           = azurerm_private_dns_zone.postgres.id
  public_network_access_enabled = false

  zone = "1"

  depends_on = [azurerm_private_dns_zone_virtual_network_link.postgres]
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "campusconnect"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "UTF8"
}
