variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "southasia"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "southasia-1"
}

variable "vpc_connector_name" {
  description = "Name for the VPC Access Connector"
  type        = string
  default     = "oxygen-vpc-connector"
}

variable "db_instance_name" {
  description = "Cloud SQL instance name"
  type        = string
  default     = "oxygen-db-instance"
}

variable "db_machine_type" {
  description = "Cloud SQL machine type"
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

variable "cloud_run_service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "oxygen-cloud-run"
}

variable "container_image" {
  description = "Container image URI"
  type        = string
}
