output "cloud_run_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_service.cloud_run_service.status[0].url
}

output "cloud_sql_private_ip" {
  description = "Private IP of Cloud SQL instance"
  value       = google_sql_database_instance.postgres_instance.private_ip_address
}
