resource "google_sql_database_instance" "postgres" {
  name             = var.db_instance_name
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = var.db_tier
    availability_type = "REGIONAL"
    disk_type         = "PD_SSD"
    disk_size         = 100

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc_network.id
      require_ssl     = true
    }
  }

  deletion_protection = true
}

resource "google_sql_database" "database" {
  name     = "rebellis"
  instance = google_sql_database_instance.postgres.name
}
