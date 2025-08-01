terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
  required_version = ">= 1.1.0"
}

provider "google" {
  project = "oxygen-deepti"
  region  = "southasia1"
  zone    = "southasia1-a"
}

# Enable necessary APIs
resource "google_project_service" "cloud_run" {
  service = "run.googleapis.com"
}

resource "google_project_service" "cloud_sql" {
  service = "sqladmin.googleapis.com"
}

resource "google_project_service" "vpc_access" {
  service = "vpcaccess.googleapis.com"
}

resource "google_project_service" "artifact_registry" {
  service = "artifactregistry.googleapis.com"
}

# VPC network (default network could be used, but explicit is cleaner)
resource "google_compute_network" "vpc_network" {
  name                    = "oxygen-vpc-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "vpc_subnet" {
  name          = "oxygen-subnet"
  ip_cidr_range = "10.10.0.0/16"
  region        = "southasia1"
  network       = google_compute_network.vpc_network.id
}

# Serverless VPC Access Connector for Cloud Run to connect to VPC (and thus Cloud SQL privately)
resource "google_vpc_access_connector" "vpc_connector" {
  name   = "oxygen-vpc-connector"
  region = "southasia1"
  network = google_compute_network.vpc_network.name

  ip_cidr_range = "10.8.0.0/28"
}

# Cloud SQL PostgreSQL instance
resource "google_sql_database_instance" "postgres_instance" {
  name             = "oxygen-db-instance"
  database_version = "POSTGRES_14"
  region           = "southasia1"

  settings {
    tier = "db-f1-micro"  # minimum machine type for dev
    ip_configuration {
      # Disable public IP to enforce private connection
      ipv4_enabled    = false
      private_network = google_compute_network.vpc_network.id
    }
    backup_configuration {
      enabled = false
    }
  }

  deletion_protection = false
}

# PostgreSQL user
resource "google_sql_user" "db_user" {
  name     = "deepti-db"
  instance = google_sql_database_instance.postgres_instance.name
  password = "DeeptiGarg@0111"
}

# Create a database in the instance (optional)
resource "google_sql_database" "app_database" {
  name     = "appdb"
  instance = google_sql_database_instance.postgres_instance.name
}

# Cloud Run service
resource "google_cloud_run_service" "fastapi_service" {
  name     = "oxygen-cloud-run"
  location = "southasia1"

  template {
    spec {
      containers {
        image = "southasia-docker.pkg.dev/oxygen-deepti/fastapi-backend-repo/fastapi-backend:latest"
  
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
          value = google_sql_user.db_user.name
        }
        env {
          name  = "DATABASE_PASSWORD"
          value = google_sql_user.db_user.password
        }
        env {
          name  = "DATABASE_NAME"
          value = google_sql_database.app_database.name
        }
      }
      container_concurrency = 80
      service_account_name  = google_service_account.cloud_run_sa.email
      vpc_access {
        connector = google_vpc_access_connector.vpc_connector.name
        egress    = "ALL_TRAFFIC"
      }
    }
  }

  traffics {
    percent         = 100
    latest_revision = true
  }
}

# Create a service account for Cloud Run with Cloud SQL Client role
resource "google_service_account" "cloud_run_sa" {
  account_id   = "cloud-run-sa"
  display_name = "Cloud Run service account"
}

resource "google_project_iam_member" "cloud_run_cloudsql" {
  project = "oxygen-deepti"
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Allow Cloud Run to be invoked publicly (optional, can be restricted later)
resource "google_cloud_run_service_iam_member" "invoker" {
  location    = google_cloud_run_service.fastapi_service.location
  project     = "oxygen-deepti"
  service     = google_cloud_run_service.fastapi_service.name
  role        = "roles/run.invoker"
  member      = "allUsers"
}
