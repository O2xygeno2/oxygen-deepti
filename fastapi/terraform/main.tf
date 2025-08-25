provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_project_service" "vpcaccess" {
  project = var.project_id
  service = "vpcaccess.googleapis.com"
}

resource "google_project_service" "servicenetworking" {
  project = var.project_id
  service = "servicenetworking.googleapis.com"
}

# Create custom VPC
resource "google_compute_network" "vpc_network" {
  name                    = var.vpc_network_name
  auto_create_subnetworks = false
}

# Create subnet in your region
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.vpc_network_name}-subnet"
  ip_cidr_range = "10.10.0.0/16"
  region        = var.region
  network       = google_compute_network.vpc_network.id
}

# Reserve IP range for private services
resource "google_compute_global_address" "private_ip_alloc" {
  name          = "private-ip-range"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc_network.id
}

# VPC peering for Service Networking (needed for Cloud SQL private IP)
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
}

# VPC Access Connector (for Cloud Run -> SQL)
resource "google_vpc_access_connector" "vpc_connector" {
  name    = var.vpc_connector_name
  region  = var.region
  network = google_compute_network.vpc_network.name

  ip_cidr_range  = "10.8.0.0/28"
  min_throughput = 200
  max_throughput = 300
}

# --------------------------
# Cloud SQL
# --------------------------
resource "google_sql_database_instance" "postgres_instance" {
  name             = var.db_instance_name
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = var.db_machine_type

    ip_configuration {
      private_network = google_compute_network.vpc_network.id
      ipv4_enabled    = false
    }

    disk_size = var.db_disk_size
  }

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

# DB User
resource "google_sql_user" "db_user" {
  name     = var.db_username
  instance = google_sql_database_instance.postgres_instance.name
  password = var.db_password
}

# DB Schema
resource "google_sql_database" "app_database" {
  name     = var.db_name
  instance = google_sql_database_instance.postgres_instance.name
}

# --------------------------
# Service Account for Cloud Run
# --------------------------
resource "google_service_account" "cloud_run_sa" {
  account_id   = "cloud-run-sa"
  display_name = "Cloud Run Service Account"
}

# Grant Cloud Run SA access to Cloud SQL
resource "google_project_iam_member" "cloud_run_cloudsql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Artifact Registry repository
resource "google_artifact_registry_repository" "fastapi_repo" {
  project  = var.project_id
  location = var.region
  repository_id = "fastapi-backend-repo"
  format   = "DOCKER"
}


locals {
  container_image = "asia-south1-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.fastapi_repo.repository_id}/fastapi-backend:latest"
}


# --------------------------
# Cloud Run
# --------------------------
resource "google_cloud_run_service" "cloud_run_service" {
  name     = var.cloud_run_service_name
  location = var.region

  template {
    metadata {
      annotations = {
        "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.vpc_connector.id
        "run.googleapis.com/vpc-access-egress"    = "all-traffic"
      }
    }

    spec {
      containers {
        image = local.container_image

        env {
          name  = "DATABASE_HOST"
          value = google_sql_database_instance.postgres_instance.private_ip_address
        }
        env {
          name  = "DATABASE_PORT"
          value = "5432"
        }
        env {
          name  = "DATABASE_USER"
          value = var.db_username
        }
        env {
          name  = "DATABASE_PASSWORD"
          value = var.db_password
        }
        env {
          name  = "DATABASE_NAME"
          value = var.db_name
        }
      }
      service_account_name  = google_service_account.cloud_run_sa.email
      container_concurrency = 80
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "invoker" {
  location = google_cloud_run_service.cloud_run_service.location
  project  = var.project_id
  service  = google_cloud_run_service.cloud_run_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
