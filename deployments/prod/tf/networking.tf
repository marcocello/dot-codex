resource "azurerm_virtual_network" "this" {
  name                = lower(join("-", [local.prefix, "vnet"]))
  address_space       = [local.network.address_space]
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = local.custom_tags
}

resource "azurerm_subnet" "this" {
  name                 = lower(join("-", [local.prefix, "subnet"]))
  resource_group_name  = azurerm_resource_group.this.name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = [local.network.subnet_prefix]
}

resource "azurerm_network_security_group" "this" {
  name                = lower(join("-", [local.prefix, "nsg"]))
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = local.custom_tags
}

resource "azurerm_network_security_rule" "openvpn" {
  name                        = local.openvpn.rule_name
  priority                    = 110
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Udp"
  source_port_range           = "*"
  destination_port_range      = tostring(local.openvpn.port)
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.this.name
  network_security_group_name = azurerm_network_security_group.this.name
}

resource "azurerm_public_ip" "this" {
  name                = lower(join("-", [local.prefix, "pip"]))
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  allocation_method   = "Static"
  sku                 = "Standard"
  domain_name_label   = local.input.project
  tags                = local.custom_tags
}

resource "azurerm_network_interface" "this" {
  name                = lower(join("-", [local.prefix, "nic"]))
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = local.custom_tags

  ip_configuration {
    name                          = "primary"
    subnet_id                     = azurerm_subnet.this.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.this.id
  }
}

resource "azurerm_network_interface_security_group_association" "this" {
  network_interface_id      = azurerm_network_interface.this.id
  network_security_group_id = azurerm_network_security_group.this.id
}
