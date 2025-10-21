terraform {
  required_providers { google = { source = "hashicorp/google", version = "~> 5.0" } }
}
variable "project_id" {}
variable "bucket_name" { default = "rebellis-artifacts" }
variable "location" { default = "EUROPE-WEST4" }

resource "google_storage_bucket" "artifacts" {
  name          = var.bucket_name
  location      = var.location
  force_destroy = true
  uniform_bucket_level_access = true
  versioning { enabled = true }
  lifecycle_rule {
    condition { num_newer_versions = 5 }
    action    { type = "Delete" }
  }
}

output "bucket_name" { value = google_storage_bucket.artifacts.name }
