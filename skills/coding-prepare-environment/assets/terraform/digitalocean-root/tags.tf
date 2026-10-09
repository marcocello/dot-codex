resource "digitalocean_tag" "this" {
  for_each = { for key, value in local.custom_tags : key => value if value != "" }

  name = lower(join(":", [local.prefix, each.key, each.value]))
}
