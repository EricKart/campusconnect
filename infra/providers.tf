terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.116"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "azurerm" {
  features {}
  # Same fix Day 13 needed: this subscription's automatic resource-provider
  # registration hits the same TLS wall as the registry itself. Registration
  # was already done once (Day 13/14 already created AKS clusters here).
  skip_provider_registration = true
}
