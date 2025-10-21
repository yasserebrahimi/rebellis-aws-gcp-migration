variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "rebellis-production"
}

variable "region" {
  description = "Primary GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Primary GCP zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "gke_cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "rebellis-prod-cluster"
}

variable "db_instance_name" {
  description = "Cloud SQL instance name"
  type        = string
  default     = "rebellis-postgres-15"
}

variable "db_tier" {
  description = "Cloud SQL tier"
  type        = string
  default     = "db-custom-4-16384"
}
