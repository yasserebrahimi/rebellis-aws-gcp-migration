terraform {
  required_providers { google = { source = "hashicorp/google", version = "~> 5.0" } }
}
variable "project_id" {}
variable "vpc_name" { default = "rebellis-vpc" }
variable "region" { default = "europe-west4" }

resource "google_compute_network" "vpc" {
  name = var.vpc_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "primary" {
  name          = "${var.vpc_name}-subnet"
  ip_cidr_range = "10.10.0.0/16"
  region        = var.region
  network       = google_compute_network.vpc.id
}

output "network"   { value = google_compute_network.vpc.self_link }
output "subnet"    { value = google_compute_subnetwork.primary.self_link }
