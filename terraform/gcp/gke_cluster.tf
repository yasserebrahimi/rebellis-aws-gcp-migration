resource "google_container_cluster" "primary" {
  name     = var.gke_cluster_name
  location = var.region

  enable_autopilot = true

  network    = google_compute_network.vpc_network.id
  subnetwork = google_compute_subnetwork.gke_subnet.id

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  release_channel {
    channel = "REGULAR"
  }
}
