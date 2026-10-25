output "connection" {
  description = "Non-sensitive values used by setup, Remote Control, and VPN-only SSH workflows."
  value = {
    subscription_id             = var.subscription_id
    resource_group_name         = azurerm_resource_group.this.name
    network_security_group_name = azurerm_network_security_group.this.name
    ssh_fqdn                    = azurerm_public_ip.this.fqdn
    ssh_username                = local.vm.admin_username
    vm_name                     = azurerm_linux_virtual_machine.this.name
    workspace_disk_name         = azurerm_managed_disk.workspace.name
    workspace_disk_lun          = local.vm.workspace_disk_lun
    workspace_mount_path        = local.vm.workspace_mount_path
    mac_private_key_path        = local.vm.mac_private_key_path
    ssh_host_config_path        = pathexpand(local.vm.local_ssh_host_config_path)
    ssh_known_hosts_path        = local.vm.local_ssh_known_hosts_path
    openvpn_rule_name           = local.openvpn.rule_name
    openvpn_port                = local.openvpn.port
    openvpn_network             = local.openvpn.network
    openvpn_netmask             = local.openvpn.netmask
    openvpn_server_address      = local.openvpn.server_address
    openvpn_ssh_alias           = local.openvpn.connection_alias
    openvpn_local_root_path     = local.openvpn.local_root_path
    openvpn_client_profile_path = local.openvpn.client_profile_path
    codex_version               = local.provisioning.codex_version
    codex_package_url           = local.provisioning.codex_package_url
    codex_package_sha256        = local.provisioning.codex_package_sha256
  }
}

output "next_steps" {
  description = "Brief connection instructions shown after Terraform apply."
  value       = <<-EOT
    1. Set up or repair Codex with: scripts/codex-vm.sh setup
    2. Connect the existing Mac OpenVPN profile: ${local.openvpn.client_profile_path}
    3. Sign in to Codex over the VPN with: scripts/codex-vm.sh sign-in
    4. Start Remote Control and print a pairing code with: scripts/codex-vm.sh pair
    5. Optionally clone or update dot-codex from GitHub with: scripts/codex-vm.sh dot-codex

    Run scripts/codex-vm.sh with no arguments for every interactive operator workflow.
    While connected to OpenVPN, reconcile or intentionally rotate VPN credentials with: scripts/codex-vm.sh vpn-setup [--rotate]
    If preparation is required, interactive workflows ask before running setup; non-interactive commands stop with an explicit setup instruction.
    Terraform creates infrastructure only. Setup and Remote Control recovery use Azure Run Command; interactive VM actions require the connected VPN.
    The NSG has no inbound TCP/22 rule. Its only standing operator ingress is OpenVPN UDP/${local.openvpn.port}; repositories and Codex state persist on the managed disk at ${local.vm.workspace_mount_path}.
    If Codex or Remote Control is unavailable, rerun without SSH from the repository root: scripts/codex-vm.sh setup
  EOT
}
