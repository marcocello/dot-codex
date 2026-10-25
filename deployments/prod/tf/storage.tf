resource "azurerm_managed_disk" "workspace" {
  name                          = lower(join("-", [local.prefix, "workspace-disk"]))
  location                      = azurerm_resource_group.this.location
  resource_group_name           = azurerm_resource_group.this.name
  storage_account_type          = "StandardSSD_LRS"
  create_option                 = "Empty"
  disk_size_gb                  = local.vm.workspace_disk_size_gb
  network_access_policy         = "DenyAll"
  public_network_access_enabled = false
  tags                          = local.custom_tags

  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_virtual_machine_data_disk_attachment" "workspace" {
  managed_disk_id    = azurerm_managed_disk.workspace.id
  virtual_machine_id = azurerm_linux_virtual_machine.this.id
  lun                = local.vm.workspace_disk_lun
  caching            = "None"
}

resource "azurerm_management_lock" "workspace_disk" {
  name       = "protect-workspace-disk"
  scope      = azurerm_managed_disk.workspace.id
  lock_level = "CanNotDelete"
  notes      = "Protects the persistent Git workspace disk from accidental deletion."
}
