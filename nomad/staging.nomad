job "goalpath-staging" {
  datacenters = ["dc1"]
  type        = "service"
  
  group "web" {
    count = 2
    
    network {
      port "http" { to = 8000 }
    }
    
    service {
      name = "goalpath-staging"
      port = "http"
      tags = [
        "staging", "web", "goalpath",
        "traefik.enable=true",
        "traefik.http.routers.goalpath-staging.rule=Host(`staging.goalpath.local`)"
      ]
      check {
        type = "http"; path = "/health"; interval = "10s"; timeout = "5s"
      }
    }
    
    task "goalpath" {
      driver = "docker"
      config {
        image = "${IMAGE_TAG}"
        ports = ["http"]
        mount { type = "volume"; target = "/app/data"; source = "goalpath_staging_data" }
      }
      env {
        DATABASE_URL = "sqlite:////app/data/goalpath_staging.db"
        ENVIRONMENT = "staging"; PORT = "8000"
      }
      resources { cpu = 256; memory = 512 }
    }
  }
}