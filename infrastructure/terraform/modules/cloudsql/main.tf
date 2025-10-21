terraform {
  required_providers {
    google = { source = "hashicorp/google", version = "~> 5.0" }
  }
}

variable "project_id" {}
variable "region" { default = "europe-west4" }
variable "instance_name" { default = "rebellis-sql" }
variable "tier" { default = "db-custom-2-4096" }
variable "database_version" { default = "POSTGRES_15" }
variable "authorized_networks" { default = [] }

resource "google_sql_database_instance" "this" {
  name             = var.instance_name
  database_version = var.database_version
  region           = var.region

  settings {
    tier = var.tier
    ip_configuration {
      ipv4_enabled = false
      private_network = null
      authorized_networks = [
        for cidr in var.authorized_networks : {
          name  = "auth"
          value = cidr
        }
      ]
    }
    backup_configuration {
      enabled = true
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
    }
    maintenance_window {
      day  = 7
      hour = 3
    }
    insights_config {
      query_insights_enabled = true
    }
  }
  deletion_protection = false
}

resource "google_sql_database" "app" {
  name     = "rebellis"
  instance = google_sql_database_instance.this.name
}

output "connection_name" { value = google_sql_database_instance.this.connection_name }
