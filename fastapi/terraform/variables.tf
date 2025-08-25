variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "Primary GCP region for resources"
  type        = string
  default     = "asia-south1" # Mumbai
}

variable "zone" {
  description = "Primary GCP zone for resources"
  type        = string
  default     = "asia-south1-a" # Mumbai zone
}

# Networking
variable "vpc_network_name" {
  description = "The name of the existing VPC network"
  type        = string
  default     = "oxygen-vpc"
}

variable "vpc_connector_name" {
  description = "Name for the Serverless VPC Access Connector"
  type        = string
  default     = "oxygen-vpc-connector"
}

# Cloud SQL
variable "db_instance_name" {
  description = "Cloud SQL instance name"
  type        = string
  default     = "oxygen-db-instance"
}

variable "db_machine_type" {
  description = "Cloud SQL machine type (db-f1-micro, db-g1-small, db-custom-2-3840, etc.)"
  type        = string
  default     = "db-f1-micro"
}

variable "db_disk_size" {
  description = "Cloud SQL disk size in GB"
  type        = number
  default     = 10
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "deepti-db"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "appdb"
}

# Cloud Run
variable "cloud_run_service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "oxygen-cloud-run"
}

variable "container_image" {
  description = "Container image URI in Artifact Registry or GCR"
  type        = string
}

# Optional: Pre-created Service Account (if no IAM permission to create one via Terraform)
variable "cloud_run_sa_email" {
  description = "Email of an existing service account for Cloud Run (if created manually)"
  type        = string
  default     = "" # leave empty if Terraform should create it
}
