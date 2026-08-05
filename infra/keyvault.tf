data "azurerm_client_config" "current" {}

resource "random_id" "kv_suffix" {
  byte_length = 3
}

resource "azurerm_key_vault" "main" {
  name                = "kv-${var.project}-${random_id.kv_suffix.hex}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = ["Get", "List", "Set", "Delete", "Purge"]
  }
}

resource "azurerm_key_vault_secret" "database_url" {
  name = "database-url"
  # urlencode() is required here -- a connection-string URL uses "@" to
  # separate credentials from host, so any "@" (or other URL-reserved
  # character) actually IN the password must be percent-encoded first, or
  # the parser misreads part of the password as the hostname. Hit this for
  # real: an unescaped "@" in the password corrupted the host into
  # "ss7734@psql-campusconnect...", a real "could not translate host name"
  # error from the running api pod.
  value        = "postgresql+psycopg2://ccadmin:${urlencode(random_password.postgres_admin.result)}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/campusconnect"
  key_vault_id = azurerm_key_vault.main.id
}

resource "random_id" "jwt_secret" {
  byte_length = 32
}

resource "azurerm_key_vault_secret" "jwt_secret" {
  name         = "jwt-secret"
  value        = random_id.jwt_secret.hex
  key_vault_id = azurerm_key_vault.main.id
}
