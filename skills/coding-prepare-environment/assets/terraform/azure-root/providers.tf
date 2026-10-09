terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      # Add the target project's supported version constraint before initialization.
    }
  }
}

provider "azurerm" {
  features {}
  # Supply the selected subscription and credentials through the operator environment.
}
