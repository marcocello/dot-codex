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
  owner           = "provisioning-proof"
}

run "pinned_root_provisioning_plan" {
  command = plan

  assert {
    condition     = azurerm_linux_virtual_machine.this.source_image_reference[0].offer == "ubuntu-24_04-lts" && azurerm_linux_virtual_machine.this.source_image_reference[0].sku == "server" && azurerm_linux_virtual_machine.this.source_image_reference[0].version == "24.04.202606060"
    error_message = "The VM image must use the reviewed stable Ubuntu 24.04 image available in Austria East instead of latest or a daily-build version."
  }

  assert {
    condition     = output.connection.codex_version == "0.144.3" && output.connection.codex_package_url == "https://github.com/openai/codex/releases/download/rust-v0.144.3/codex-package-x86_64-unknown-linux-musl.tar.gz" && output.connection.codex_package_sha256 == "1c3c1f1f636da56a197ce0b5084d44b86f58f0fb32983278fa55c2544d221af4"
    error_message = "Terraform must expose the exact Codex 0.144.3 package URL and SHA-256 digest to local preparation."
  }

  assert {
    condition     = azurerm_linux_virtual_machine.this.custom_data == null
    error_message = "Terraform must not activate root installation through custom data."
  }

  assert {
    condition     = !strcontains(output.connection.codex_package_url, "install.sh") && !strcontains(output.connection.codex_package_url, "latest")
    error_message = "Terraform must not expose a mutable Codex installer to local preparation."
  }

}
