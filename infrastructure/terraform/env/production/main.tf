terraform {
  required_version = ">= 1.5.0"
  backend "gcs" {
    bucket = "terraform-state-PROJECT_ID"
    prefix = "rebellis/production"
  }
  required_providers { google = { source = "hashicorp/google", version = "~> 5.0" } }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {}
variable "region" { default = "europe-west4" }

module "vpc" {
  source     = "../../modules/vpc"
  project_id = var.project_id
  region     = var.region
}

module "gke" {
  source       = "../../modules/gke"
  project_id   = var.project_id
  region       = var.region
  cluster_name = "rebellis-production"
  network      = module.vpc.network
  subnetwork   = module.vpc.subnet
}

module "cloudsql" {
  source       = "../../modules/cloudsql"
  project_id   = var.project_id
  region       = var.region
  instance_name = "rebellis-production-sql"
}

module "gcs" {
  source      = "../../modules/gcs"
  project_id  = var.project_id
  bucket_name = "rebellis-production-artifacts-PROJECT_ID"
}

output "gke_cluster" { value = module.gke.cluster_name }
output "cloudsql_connection" { value = module.cloudsql.connection_name }
