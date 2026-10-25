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
  owner           = "openvpn-proof"
}

run "self_hosted_openvpn_plan" {
  command = plan

  assert {
    condition = (
      azurerm_network_security_rule.openvpn.name == "AllowOpenVpn" &&
      azurerm_network_security_rule.openvpn.direction == "Inbound" &&
      azurerm_network_security_rule.openvpn.access == "Allow" &&
      azurerm_network_security_rule.openvpn.protocol == "Udp" &&
      azurerm_network_security_rule.openvpn.destination_port_range == "1194" &&
      azurerm_network_security_rule.openvpn.source_address_prefix == "*" &&
      azurerm_network_security_rule.openvpn.network_security_group_name == azurerm_network_security_group.this.name
    )
    error_message = "The standing OpenVPN ingress must allow only UDP/1194 on the existing VM NSG."
  }

  assert {
    condition = (
      output.connection.openvpn_rule_name == "AllowOpenVpn" &&
      output.connection.openvpn_port == 1194 &&
      output.connection.openvpn_network == "10.250.0.0" &&
      output.connection.openvpn_netmask == "255.255.255.0" &&
      output.connection.openvpn_server_address == "10.250.0.1" &&
      output.connection.openvpn_ssh_alias == "codex-on-vm-vpn" &&
      endswith(output.connection.openvpn_local_root_path, "/.config/codex-on-vm/openvpn") &&
      endswith(output.connection.openvpn_client_profile_path, "/.config/codex-on-vm/openvpn/codex-on-vm.ovpn") &&
      !contains(keys(output.connection), "ssh_alias") &&
      !contains(keys(output.connection), "temporary_ssh_rule_name") &&
      !contains(keys(output.connection), "local_mount_path")
    )
    error_message = "Terraform must expose only the VPN-only, non-secret values consumed by the Mac workflow."
  }

  assert {
    condition     = strcontains(output.next_steps, "scripts/codex-vm.sh vpn-setup") && !strcontains(output.next_steps, "Azure VPN Gateway")
    error_message = "Terraform must direct the operator to the self-hosted VPN workflow without a paid gateway."
  }
}
