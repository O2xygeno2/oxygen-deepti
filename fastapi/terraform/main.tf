provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# VPC Access Connector
resource "google_vpc_access_connector" "vpc_connector" {
  name          = "${var.project_id}/locations/${var.region}/connectors/${var.vpc_connector_name}"
  region        = var.region
  network       = var.vpc_network_name
  ip_cidr_range = "10.8.0.0/28"
}

# Cloud SQL instance
resource "google_sql_database_instance" "postgres_instance" {
  name             = var.db_instance_name
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = var.db_machine_type

    ip_configuration {
      private_network = "projects/${var.project_id}/global/networks/${var.vpc_network_name}"
      ipv4_enabled    = false
    }

    disk_size = var.db_disk_size
  }
}

# Cloud SQL user
resource "google_sql_user" "db_user" {
  name     = var.db_username
  instance = google_sql_database_instance.postgres_instance.name
  password = var.db_password
}

# Cloud SQL database
resource "google_sql_database" "app_database" {
  name     = var.db_name
  instance = google_sql_database_instance.postgres_instance.name
}

# Service Account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "cloud-run-sa"
  display_name = "Cloud Run Service Account"
}

# Grant Cloud Run SA permission to access Cloud SQL
resource "google_project_iam_member" "cloud_run_cloudsql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Cloud Run service
resource "google_cloud_run_service" "cloud_run_service" {
  name     = var.cloud_run_service_name
  location = var.region

  template {
    spec {
      containers {
        image = var.container_image

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

      vpc_access {
        connector = google_vpc_access_connector.vpc_connector.name
        egress    = "ALL_TRAFFIC"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access to Cloud Run
resource "google_cloud_run_service_iam_member" "invoker" {
  location = google_cloud_run_service.cloud_run_service.location
  project  = var.project_id
  service  = google_cloud_run_service.cloud_run_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
