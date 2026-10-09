terraform {
  backend "s3" {
    bucket = "REPLACE_STATE_BUCKET"
    key    = "REPLACE_STAGE-REPLACE_PROJECT-backend/terraform.tfstate"
    region = "us-east-1"

    endpoints = {
      s3 = "https://REPLACE_SPACES_REGION.digitaloceanspaces.com"
    }

    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true

    # Verify conditional lock creation on the selected Spaces bucket before shared use.
    use_lockfile = true
  }
}
