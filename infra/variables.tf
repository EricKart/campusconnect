variable "location" {
  description = "Azure region -- centralindia. eastus (this subscription's usual region for Days 10/13/14) turned out to be LocationIsOfferRestricted for Postgres Flexible Server on this specific subscription; centralindia and southeastasia were confirmed available via `az postgres flexible-server list-skus`, and centralindia matches where this subscription already runs other resources."
  type        = string
  default     = "centralindia"
}

variable "project" {
  description = "Short name used as a prefix/suffix for every resource this project creates."
  type        = string
  default     = "campusconnect"
}

variable "resource_group_name" {
  type    = string
  default = "rg-campusconnect"
}

variable "aks_node_vm_size" {
  description = "Standard_D2s_v7 (the known-good size in eastus for Days 10/12/13/14) is not available in centralindia at all -- trying Standard_D2s_v5 as a widely-available fallback, per Day 12's 'trust the real error, not assumptions' rule."
  type        = string
  default     = "Standard_D2s_v5"
}
