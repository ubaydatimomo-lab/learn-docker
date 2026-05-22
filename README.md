# Multi-Container Scaled Architecture with Nginx Load Balancing

A personalized, highly available multi-container microservice application. The infrastructure decouples application logic, caching, and routing into separate containerized layers, utilizing Nginx to dynamically load-balance traffic across a scaled backend array.

---

## What I Built

I developed a full-stack, containerized system that serves interactive web pages while safely persisting dynamic state. 

### Core Components
* **Application Layer:** A Python Flask web server hosting dynamic user routes, including a personalized portfolio profile (`/about`) and a traffic monitor (`/count`).
* **State & Caching Layer:** A distributed Redis key-value store acting as a centralized state engine to keep data unified across independent workers.
* **Routing & Load Balancing Layer:** An Nginx reverse proxy serving as the public-facing entry point, configured to distribute client traffic efficiently.

                   +---------------+
                   |  Web Browser  |
                   +-------+-------+
                           | (Port 5002)
                           v
                   +---------------+
                   |     Nginx     |
                   +-------+-------+
                           |
     +---------------------+---------------------+
     | (Round-Robin)       | (Round-Robin)       | (Round-Robin)
     v                     v                     v
+------------+        +------------+        +------------+
|  Web App 1 |        |  Web App 2 |        |  Web App 3 |
+----+-------+        +----+-------+        +----+-------+
|                     |                     |
+---------------------+---------------------+
|
v
+--------------+
|    Redis     |
+--------------+


---

## Your Approach

To mimic a real-world production deployment, I followed a modular, container-first approach rather than launching a standard monolithic local server.

1.  **Deconstruction:** I separated the code logic from data storage, ensuring that the Flask application containers remain entirely stateless. 
2.  **Containerization:** Built custom Docker configurations utilizing lightweight base images (`python:3.11-slim`) to minimize image footprints and ensure environment reproducibility.
3.  **Horizontal Scaling:** Orchestrated the services via Docker Compose, eliminating hardcoded host ports on the web layer so the backend could scale fluidly (`--scale web=3`) without resource conflicts.
4.  **Reverse Proxying:** Mounted custom local configurations (`nginx.conf`) directly into the official upstream Nginx container to gracefully bind public queries on a custom port and handle internal service name resolution.

---

## Challenges and How I Solved Them

### 1. The Indentation Trap (YAML Syntax)
* **Challenge:** Early orchestration attempts failed on container startup due to formatting alignment errors (`did not find expected '-' indicator`).
* **Solution:** Learned that YAML relies strictly on strict column alignment rather than bracket styling. Cleaned up the nested service declarations, aligning block elements, list items, and volume mounts down to identical space intervals.

### 2. Upstream Port Mismatches (502 Bad Gateway)
* **Challenge:** After scaling the containers, the browser repeatedly returned a `502 Bad Gateway` error while terminal logs revealed constant `Connection refused` errors between Nginx and the web containers.
* **Solution:** Discovered Nginx was routing internal cluster queries to port `5000` while the scaled Flask applications were listening on port `5002`. Standardized the internal application layout to listen strictly on `0.0.0.0:5000` inside the isolated network, allowing Nginx's `upstream` server configuration block to establish clean handshakes.

### 3. Local Host OS Resource Conflicts (Access Denied)
* **Challenge:** Encountered system permission blocks (`Access Denied`) when trying to expose the internal application port directly to the local host machine.
* **Solution:** Identified that macOS claims port `5000` by default for the AirPlay Receiver service. Resolved this by swapping out the web container's `ports` mapping for `expose`, isolating port `5000` inside the Docker network structure where it is invisible to the host OS. The public port mapping was moved entirely to Nginx on port `5002`.

---

## What I Learnt

* **Microservice Interconnectivity:** Gained a practical understanding of how containers communicate using internal DNS and service abstractions within a shared bridge network.
* **Stateless Scaling:** Learned how stateless backends interact with centralized data layers (Redis), ensuring that data remains consistent regardless of which container handles an individual HTTP request.
* **Production Load Balancing:** Understood how reverse proxies route ingress traffic via Round-Robin, mitigating single points of failure and laying the groundwork for high-availability systems.
* **Debugging Container Networks:** Developed strong troubleshooting workflows by isolating container logs directly (`docker compose logs web`) to dissect runtime traceroute faults.

---

## 🛠️ Project Structure

```text
FirstProject/
├── app/
│   ├── templates/
│   │   ├── about.html      # Portfolio UI
│   │   └── count.html      # Analytics Dashboard UI
│   ├── app.py              # Flask backend application logic
│   ├── requirements.txt    # Application dependencies
│   └── Dockerfile          # Python build script
├── nginx.conf              # Load balancer proxy configuration
└── docker-compose.yml      # Service orchestration engine