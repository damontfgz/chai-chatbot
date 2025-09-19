data "google_project" "project" {
}

resource "google_service_account" "cluster" {
  create_ignore_already_exists = true
  account_id                   = "gke-cluster"
}

resource "google_project_iam_member" "artifactry_reader" {
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.cluster.email}"
  project = data.google_project.project.project_id
}

resource "google_container_cluster" "main" {
  name                      = "demo-gke-cluster"
  location                  = var.region
  network                   = google_compute_network.region.self_link
  subnetwork                = google_compute_subnetwork.main.self_link
  datapath_provider         = "ADVANCED_DATAPATH"
  deletion_protection = false
  remove_default_node_pool = true

  initial_node_count       = 1


  workload_identity_config {
    workload_pool = "${data.google_project.project.project_id}.svc.id.goog"
  }

  # SBC-GCP-3011
  enable_intranode_visibility = true

  release_channel {
    channel = "STABLE"
  }

  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }

    # SBC-GCP-3013
  master_authorized_networks_config {
  }

  control_plane_endpoints_config {
    dns_endpoint_config {
      allow_external_traffic = true
    }
  }

  private_cluster_config {
    enable_private_endpoint = true
    enable_private_nodes = true

    private_endpoint_subnetwork = google_compute_subnetwork.main.self_link
  }

  node_config {
    service_account = google_service_account.cluster.email
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    shielded_instance_config {
      enable_secure_boot = true
      enable_integrity_monitoring = true
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  addons_config {
    ray_operator_config {
      enabled = true
      ray_cluster_logging_config {
        enabled = true
      }
      ray_cluster_monitoring_config {
        enabled = true
      }
    }
    
  }

}

resource "google_container_node_pool" "main" {
  name_prefix       = "api-knp-"
  location          = var.region
  cluster           = google_container_cluster.main.name
  autoscaling {
    min_node_count = 1
    max_node_count = 1
  }

  node_config {
    # preemptible  = true
    # machine_type = "e2-highcpu-8"
    machine_type = "e2-standard-2"

    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    service_account = google_service_account.cluster.email
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    shielded_instance_config {
      enable_secure_boot = true
      enable_integrity_monitoring = true
    }

  }
}

# resource "google_container_node_pool" "gpu" {
#   name_prefix       = "gpu-knp-"
#   location          = var.region
#   cluster           = google_container_cluster.main.name
#   node_count = 1
#
#   node_config {
#     image_type   = "cos_containerd"
#     machine_type = "n1-standard-4"
#
#     disk_size_gb = "50"
#     disk_type    = "pd-standard"
#
#     guest_accelerator {
#       type  = "nvidia-tesla-t4"
#       count = 1
#     }
#
#     service_account = google_service_account.cluster.email
#     workload_metadata_config {
#       mode = "GKE_METADATA"
#     }
#     oauth_scopes = [
#       "https://www.googleapis.com/auth/cloud-platform"
#     ]
#
#     shielded_instance_config {
#       enable_secure_boot = true
#       enable_integrity_monitoring = true
#     }
#
#     metadata = {
#       disable-legacy-endpoints = "true"
#     }
#
#   }
# }