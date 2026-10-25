mock_provider "azurerm" {}
mock_provider "external" {
  mock_data "external" {
    defaults = {
      result = {
        mac_public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIB5W3zliMg6KTJYc9jZJeJf/jMeTsYPbIcZ1OmVG6ngw mock-mac"
      }
    }
  }
}

variables {
  subscription_id = "00000000-0000-0000-0000-000000000000"
  owner           = "managed-workspace-proof"
}

run "remote_control_managed_workspace_plan" {
  command = plan

  assert {
    condition     = azurerm_managed_disk.workspace.storage_account_type == "StandardSSD_LRS" && azurerm_managed_disk.workspace.disk_size_gb == 256
    error_message = "The live Git workspace must use the separately managed 256 GiB Standard SSD disk."
  }

  assert {
    condition     = !azurerm_managed_disk.workspace.public_network_access_enabled && azurerm_managed_disk.workspace.network_access_policy == "DenyAll"
    error_message = "The managed disk must deny public network access."
  }

  assert {
    condition     = azurerm_virtual_machine_data_disk_attachment.workspace.lun == 0
    error_message = "The workspace managed disk must be attached to the VM at LUN 0."
  }

  assert {
    condition     = azurerm_management_lock.workspace_disk.lock_level == "CanNotDelete"
    error_message = "The workspace disk must have a CanNotDelete management lock."
  }

  assert {
    condition     = azurerm_managed_disk.workspace.name == "prod-codex-on-vm-workspace-disk"
    error_message = "The persistent disk must use a stable name independent of the VM resource."
  }

  assert {
    condition     = azurerm_backup_protected_vm.workspace.include_disk_luns == toset([0]) && azurerm_backup_policy_vm.workspace.retention_daily[0].count == 30
    error_message = "Daily VM backup must include workspace LUN 0 and retain 30 daily recovery points."
  }

  assert {
    condition     = azurerm_linux_virtual_machine.this.custom_data == null
    error_message = "Terraform must not launch guest preparation through custom data or cloud-init."
  }

  assert {
    condition = (
      output.connection.vm_name == "prod-codex-on-vm-vm" &&
      output.connection.ssh_username == "azureadmin" &&
      output.connection.workspace_mount_path == "/home/azureadmin/projects" &&
      output.connection.workspace_disk_lun == 0 &&
      output.connection.codex_version == "0.144.3" &&
      startswith(output.connection.codex_package_url, "https://") &&
      length(output.connection.codex_package_sha256) == 64
    )
    error_message = "Terraform must expose the non-secret VM, disk, and pinned Codex values consumed by local preparation."
  }

  assert {
    condition = (
      endswith(output.connection.mac_private_key_path, "/.ssh/codex-on-vm-mac") &&
      endswith(output.connection.ssh_host_config_path, "/.ssh/config.d/codex-on-vm.conf") &&
      endswith(output.connection.ssh_known_hosts_path, "/.ssh/codex-on-vm-known_hosts")
    )
    error_message = "Terraform must expose the local SSH paths written only after preparation read-back."
  }

  assert {
    condition     = !can(regex("(?i)cloud-init|on the vm run|ssh-open|scripts/prepare-machine[.]sh|scripts/codex-pair[.]sh|scripts/codex-vm[.]sh (prepare|sync-config|repair)", output.next_steps)) && strcontains(output.next_steps, "interactive workflows ask before running setup") && strcontains(output.next_steps, "non-interactive commands stop") && strcontains(output.next_steps, "scripts/codex-vm.sh setup") && strcontains(output.next_steps, "scripts/codex-vm.sh sign-in") && strcontains(output.next_steps, "scripts/codex-vm.sh pair") && strcontains(output.next_steps, "scripts/codex-vm.sh dot-codex")
    error_message = "Terraform must direct the operator through the local Codex VM console instead of VM-launched or legacy setup instructions."
  }

  assert {
    condition     = endswith(data.external.ssh_keys.program[1], "/scripts/codex-vm.sh") && data.external.ssh_keys.program[2] == "__terraform-ensure-ssh-keys"
    error_message = "Terraform SSH-key preparation must use the private unified-console entrypoint."
  }
}
