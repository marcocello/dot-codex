resource "azurerm_resource_group" "this" {
  name     = lower(join("-", [local.prefix, "rg"]))
  location = local.input.location
  tags     = local.custom_tags
}