# Key terms – in plain words

These are drafts. Read them, then say them in your own way.

**Docker image**
A read-only package that contains everything an app needs to run: the code, the runtime (Python), the libraries and the settings. It is like a recipe or a template. In my project, `quoteboard-web:1.0` is the image for the web app and `redis:7-alpine` is the image for the database.

**Dockerfile**
A text file with step-by-step instructions for building a Docker image. Each line is a step: start from a base image, copy files, install libraries, say which command starts the app. My `web/Dockerfile` starts from `python:3.12-slim`, installs Flask and Redis, copies `app.py`, and starts it with gunicorn.

**Docker Compose**
A tool, and a YAML file (`docker-compose.yml`), for describing an application made of several containers in one place: which services exist, which image each uses, ports, networks, volumes and environment variables. Instead of typing many `docker run` commands, I write it once in the file. Docker Swarm can read the same file with `docker stack deploy`.

**Docker node**
One machine (physical computer, virtual machine or cloud server) that runs Docker and is a member of a swarm. A *manager* node controls the swarm and decides where containers run. A *worker* node only runs the containers it is given. My laptop is a single manager node.

**Cluster**
A group of machines (nodes) that work together and look like one big system. If one machine fails, the others continue. In Docker, a cluster of nodes is called a swarm.

**Docker Swarm**
Docker's built-in tool for running containers on a cluster. I tell it the *desired state* ("I want 3 copies of the web app"), and Swarm makes it happen and keeps it that way. It spreads containers across nodes, load-balances traffic between them, restarts failed containers and lets me scale with one command.

**Replica**
One running copy of a service. If the `web` service has `replicas: 3`, there are three identical containers running the same image, and Swarm shares the traffic between them. More replicas means more capacity and no single point of failure. Scaling means changing the number of replicas.

---

### Bonus terms (good for questions)

- **Container**: a running instance of an image (the image is the recipe, the container is the cooked meal).
- **Service**: in Swarm, the definition of "run this image, with N replicas, with these settings".
- **Task**: Swarm's name for one replica's container slot. `docker service ps` lists tasks.
- **Stack**: a group of services deployed together from one Compose file (my stack is called `quotes`).
- **Overlay network**: a virtual network that connects containers across all nodes of the swarm.
- **Routing mesh**: Swarm opens the published port on every node and forwards each request to a healthy replica.
