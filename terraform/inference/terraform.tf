terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.34.0"
    }

    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.26.0"
    }
  }

  required_version = "~> 1.9.8"
}