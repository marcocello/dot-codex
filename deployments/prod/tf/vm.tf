resource "azurerm_linux_virtual_machine" "this" {
  name                            = lower(join("-", [local.prefix, "vm"]))
  resource_group_name             = azurerm_resource_group.this.name
  location                        = azurerm_resource_group.this.location
  size                            = local.vm.vm_size
  admin_username                  = local.vm.admin_username
  disable_password_authentication = true
  network_interface_ids           = [azurerm_network_interface.this.id]
  tags                            = local.custom_tags

  dynamic "admin_ssh_key" {
    for_each = local.vm.admin_ssh_public_keys

    content {
      username   = local.vm.admin_username
      public_key = admin_ssh_key.value
    }
  }

  os_disk {
    caching              = "ReadWrite"
    disk_size_gb         = local.vm.os_disk_size_gb
    storage_account_type = "StandardSSD_LRS"
  }

  source_image_reference {
    publisher = local.ubuntu_image.publisher
    offer     = local.ubuntu_image.offer
    sku       = local.ubuntu_image.sku
    version   = local.ubuntu_image.version
  }

}
