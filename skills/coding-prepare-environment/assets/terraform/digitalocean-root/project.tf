resource "digitalocean_project" "this" {
  name        = lower(local.prefix)
  description = "Infrastructure for ${local.prefix}, managed by Terraform."
  purpose     = "Web Application"
  environment = local.project_environment
}
