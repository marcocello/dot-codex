terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      # Add the target project's supported version constraint before initialization.
    }
  }
}

provider "digitalocean" {
  # Supply DIGITALOCEAN_TOKEN through the operator environment.
}
