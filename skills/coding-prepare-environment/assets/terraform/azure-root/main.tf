data "azurerm_subscription" "this" {}
data "azurerm_client_config" "this" {}

locals {
  prefix           = join("-", compact([local.input.stage, local.input.project, local.input.component]))
  prefix_condensed = join("", compact([local.input.stage, local.input.project, local.input.component]))
  prefix_cut       = join("", compact([substr(local.input.stage, 0, 3), substr(local.input.project, 0, 3), substr(local.input.component, 0, 3)]))
  prefix_dns       = local.input.stage == "prod" ? "api" : join(".", [local.input.stage, "api"])
  custom_tags      = local.input
}

locals {
  input = {
    stage     = "REPLACE_STAGE"
    project   = "REPLACE_PROJECT"
    component = "backend"
    service   = ""
    cloud     = "azure"
    location  = "REPLACE_LOCATION"
    managedBy = "terraform"
    owner     = "REPLACE_OWNER"
  }
}
