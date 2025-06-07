job "goalpath-production" {
  datacenters = ["dc1"]
  type        = "service"
  
  group "web" {
    count = 3
    
    network {
      port "http" { to = 8000 }
    }
    
    service {
      name = "goalpath-production"
      port = "http"
      tags = [
        "production", "web", "goalpath",
        "traefik.enable=true",
        "traefik.http.routers.goalpath.rule=Host(`goalpath.com`)",
        "traefik.http.routers.goalpath.tls=true"
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
        mount { type = "volume"; target = "/app/data"; source = "goalpath_production_data" }
      }
      env {
        DATABASE_URL = "${DATABASE_URL}"
        ENVIRONMENT = "production"
        PORT = "8000"
        SECRET_KEY = "${SECRET_KEY}"
      }
      resources { cpu = 512; memory = 1024 }
    }
  }
}