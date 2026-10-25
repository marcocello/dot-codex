variable "subscription_id" {
  description = "Azure subscription used by the provider. Supply it through ignored terraform.tfvars."
  type        = string

  validation {
    condition     = can(regex("^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$", var.subscription_id))
    error_message = "subscription_id must be an Azure subscription UUID."
  }
}

variable "owner" {
  description = "Operator or team identifier used in Azure resource tags."
  type        = string

  validation {
    condition     = length(trimspace(var.owner)) > 0
    error_message = "owner must not be empty."
  }
}

locals {
  prefix           = join("-", compact([local.input.stage, local.input.project, local.input.component]))
  prefix_condensed = join("", compact([local.input.stage, local.input.project, local.input.component]))
  prefix_cut       = join("", compact([substr(local.input.stage, 0, 3), substr(local.input.project, 0, 3), substr(local.input.component, 0, 3)]))
  prefix_dns       = local.input.stage == "prod" ? join(".", ["api"]) : join(".", [local.input.stage, "api"])
  custom_tags      = local.input
}

locals {
  input = {
    stage     = "prod"
    project   = "codex-on-vm"
    component = ""
    service   = ""
    cloud     = "azure"
    location  = "Austria East"
    managedBy = "terraform"
    owner     = var.owner
  }
}

locals {
  network = {
    address_space = "10.80.0.0/16"
    subnet_prefix = "10.80.1.0/24"
  }
}

locals {
  ssh_key_paths = {
    mac_private = pathexpand("~/.ssh/codex-on-vm-mac")
  }
}

data "external" "ssh_keys" {
  program = [
    "bash",
    abspath("${path.module}/../../../scripts/codex-vm.sh"),
    "__terraform-ensure-ssh-keys",
  ]

  query = {
    mac_private_key_path = local.ssh_key_paths.mac_private
  }
}

locals {
  vm = {
    vm_size                    = "Standard_B2als_v2"
    admin_username             = "azureadmin"
    admin_ssh_public_keys      = toset([data.external.ssh_keys.result.mac_public_key])
    os_disk_size_gb            = 64
    workspace_disk_size_gb     = 256
    workspace_disk_lun         = 0
    workspace_mount_path       = "/home/azureadmin/projects"
    mac_private_key_path       = local.ssh_key_paths.mac_private
    local_ssh_host_config_path = "~/.ssh/config.d/codex-on-vm.conf"
    local_ssh_known_hosts_path = pathexpand("~/.ssh/codex-on-vm-known_hosts")
  }

  openvpn = {
    rule_name           = "AllowOpenVpn"
    port                = 1194
    network             = "10.250.0.0"
    netmask             = "255.255.255.0"
    server_address      = "10.250.0.1"
    connection_alias    = "codex-on-vm-vpn"
    local_root_path     = pathexpand("~/.config/codex-on-vm/openvpn")
    client_profile_path = pathexpand("~/.config/codex-on-vm/openvpn/codex-on-vm.ovpn")
  }

  ubuntu_image = {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "24.04.202606060"
  }

  provisioning = {
    codex_version        = "0.144.3"
    codex_package_url    = "https://github.com/openai/codex/releases/download/rust-v0.144.3/codex-package-x86_64-unknown-linux-musl.tar.gz"
    codex_package_sha256 = "1c3c1f1f636da56a197ce0b5084d44b86f58f0fb32983278fa55c2544d221af4"
  }
}
