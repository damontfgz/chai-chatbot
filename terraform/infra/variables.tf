variable "athenz" {
    type = object({
        domain = string,
    })
}

variable "region" {
    type = string
    default = "us-central1"
}

variable "bastion" {
    type = object({
        athenz_name = string,
        image_project = string,
        image = string,
        
    })
}