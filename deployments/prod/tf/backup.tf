resource "azurerm_recovery_services_vault" "workspace" {
  name                          = lower(join("-", [local.prefix, "recovery-vault"]))
  location                      = azurerm_resource_group.this.location
  resource_group_name           = azurerm_resource_group.this.name
  sku                           = "Standard"
  storage_mode_type             = "LocallyRedundant"
  public_network_access_enabled = true
  tags                          = local.custom_tags
}

resource "azurerm_backup_policy_vm" "workspace" {
  name                           = lower(join("-", [local.prefix, "daily-30d"]))
  resource_group_name            = azurerm_resource_group.this.name
  recovery_vault_name            = azurerm_recovery_services_vault.workspace.name
  policy_type                    = "V2"
  timezone                       = "UTC"
  instant_restore_retention_days = 5

  backup {
    frequency = "Daily"
    time      = "02:00"
  }

  retention_daily {
    count = 30
  }
}

resource "azurerm_backup_protected_vm" "workspace" {
  resource_group_name = azurerm_resource_group.this.name
  recovery_vault_name = azurerm_recovery_services_vault.workspace.name
  source_vm_id        = azurerm_linux_virtual_machine.this.id
  backup_policy_id    = azurerm_backup_policy_vm.workspace.id
  include_disk_luns   = [local.vm.workspace_disk_lun]

  depends_on = [azurerm_virtual_machine_data_disk_attachment.workspace]
}
