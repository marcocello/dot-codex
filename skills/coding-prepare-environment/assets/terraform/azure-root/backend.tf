terraform {
  backend "azurerm" {
    resource_group_name  = "REPLACE_STATE_RESOURCE_GROUP"
    storage_account_name = "REPLACE_STATE_STORAGE_ACCOUNT"
    container_name       = "REPLACE_STATE_CONTAINER"
    key                  = "REPLACE_STAGE-REPLACE_PROJECT"
  }
}
