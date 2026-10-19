# Quote Board on Docker Swarm

A small Python (Flask) web app plus a Redis database, deployed as a Docker Swarm stack.

| Service      | Image                         | Replicas | Port | Role |
|--------------|-------------------------------|----------|------|------|
| `web`        | `quoteboard-web:1.0` (ours)   | 3        | 8000 | Shows quotes and which container answered |
| `redis`      | `redis:7-alpine`              | 1        | –    | Stores the quotes and the view counter |
| `visualizer` | `dockersamples/visualizer`    | 1        | 8080 | Live picture of the swarm (for the demo) |

```
docker-swarm-quoteboard/
├── docker-compose.yml     <- the stack: 3 services, 1 overlay network, 1 volume
├── web/
│   ├── app.py             <- the Flask application
│   ├── requirements.txt   <- Python libraries
│   └── Dockerfile         <- how the web image is built
├── README.md              <- this file (setup + demo script)
└── DEFINITIONS.md         <- the 7 terms explained
```

---

## 1. One-time setup (Windows, PowerShell)

1. Install **Docker Desktop** and start it (Linux containers mode – the default).
2. Open PowerShell in this folder:
   ```powershell
   cd $HOME\Desktop\docker-swarm-quoteboard
   docker version
   ```

## 2. Turn on Swarm mode

```powershell
docker swarm init
docker node ls
```
`docker node ls` should show one node with `MANAGER STATUS = Leader`.
(If it says "already part of a swarm", that's fine.)

## 3. Build the web image

Swarm does not build images, so build it first:
```powershell
docker build -t quoteboard-web:1.0 .\web
docker images quoteboard-web
```

## 4. Deploy the stack

```powershell
docker stack deploy -c docker-compose.yml quotes
```
A warning *"image quoteboard-web:1.0 could not be accessed on a registry"* is normal on a single-node swarm – the local image is used.

Check it:
```powershell
docker stack services quotes        # every service and its REPLICAS (want 3/3, 1/1, 1/1)
docker service ps quotes_web        # the 3 individual web containers (tasks)
```

Open in the browser:
- App: http://localhost:8000 – refresh a few times; **"Served by container"** changes.
- Visualizer: http://localhost:8080

---

## 5. Scaling demo

### Option A – with a command
```powershell
docker service scale quotes_web=6   # scale UP
docker service ls                   # web shows 6/6
docker service ps quotes_web        # 6 tasks Running

docker service scale quotes_web=2   # scale DOWN
docker service ls                   # web shows 2/2
```

### Option B – by changing the Compose file (the "declarative" way)
1. In `docker-compose.yml` change `replicas: 3` to `replicas: 5` under `web`.
2. Re-deploy the same stack:
   ```powershell
   docker stack deploy -c docker-compose.yml quotes
   docker stack services quotes      # web shows 5/5
   ```
3. Set it back to `3` and deploy again.

### Proving the load balancing
Call the app 10 times and print which container answered:
```powershell
1..10 | ForEach-Object { (Invoke-RestMethod http://localhost:8000/whoami).container }
```
You will see several different container IDs – one per replica.

### Bonus: self-healing
```powershell
docker ps --filter name=quotes_web           # pick one container ID
docker rm -f <container-id>                  # kill it
docker service ps quotes_web                 # Swarm already started a replacement
```

---

## 6. Presentation script (≈ 8 minutes)

1. **The cluster** – `docker node ls` → "this is my swarm, this node is the manager."
2. **The Compose file** – open `docker-compose.yml`, walk through `web`, `redis`, `visualizer`, the `quotenet` overlay network, the `redis-data` volume.
3. **The Dockerfile** – open `web/Dockerfile`, explain the 6 steps.
4. **Running app** – `docker stack services quotes`, then the browser on :8000 and :8080.
5. **Scale up** – `docker service scale quotes_web=6` → `docker service ls` + visualizer + refresh browser.
6. **Scale down** – `docker service scale quotes_web=2` → verify again.
7. **(Bonus)** kill a container, show it comes back.
8. **Definitions** – see `DEFINITIONS.md`.

## 7. Clean up / reset before the presentation

```powershell
docker stack rm quotes        # remove the stack (services + network)
docker volume rm quotes_redis-data   # optional: wipe stored quotes
docker swarm leave --force    # optional: turn Swarm mode off
```

---

## Likely questions

**Why does Redis have only 1 replica?** It holds the data. Several independent copies would each have different data. The web service is *stateless* (all state is in Redis), so it can be scaled freely.

**How do the web containers find Redis?** Swarm has built-in DNS. The service name `redis` resolves to the Redis service on the `quotenet` overlay network.

**How is traffic spread across replicas?** Swarm's *routing mesh*: port 8000 is opened on every node, and requests are load-balanced across all healthy `web` tasks.

**What's the difference between `docker compose up` and `docker stack deploy`?** `compose up` runs containers on one machine. `stack deploy` hands the same file to Swarm, which schedules the services across the cluster and uses the `deploy:` section (replicas, restart policy, placement). `build:` is ignored by Swarm.

**What happens if a container crashes?** `restart_policy: on-failure` – Swarm notices the replica count is below the desired number and starts a new task.

**What is `update_config`?** Rolling updates: when the image changes, Swarm replaces replicas one at a time with a 5 s pause, so the app stays online.

**Multi-node?** Run `docker swarm join-token worker` on the manager, then run the printed `docker swarm join ...` command on other machines (or on https://labs.play-with-docker.com). For multi-node, push the web image to Docker Hub so every node can pull it.
