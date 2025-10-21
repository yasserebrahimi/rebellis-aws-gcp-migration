terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" {}
variable "region" { default = "europe-west4" }
variable "cluster_name" { default = "rebellis" }
variable "enable_autopilot" { default = true }
variable "network" { default = "default" }
variable "subnetwork" { default = null }
variable "labels" { default = {} }
variable "release_channel" { default = "RAPID" }

resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.region
  enable_autopilot = var.enable_autopilot

  release_channel { channel = var.release_channel }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  network    = var.network
  subnetwork = var.subnetwork

  deletion_protection = false
}

output "cluster_name"     { value = google_container_cluster.primary.name }
output "cluster_location" { value = google_container_cluster.primary.location }
