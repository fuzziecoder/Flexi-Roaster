# Containerization & Orchestration

This repository now includes container and Kubernetes deployment assets that support:

- Docker-based packaging
- Kubernetes orchestration
- Horizontal auto-scaling (HPA)
- Rolling updates
- Self-healing pods (liveness/readiness probes)
- Worker isolation (dedicated worker deployment + node scheduling hints)
- Job-based stage execution
- CronJob-based scheduled pipeline execution

## Docker

### Build images

```bash
docker build -f Dockerfile.backend -t flexiroaster-backend:local .
docker build -f Dockerfile.frontend -t flexiroaster-frontend:local .
```

### Run locally with Docker Compose

```bash
docker compose up --build
```

Services:
- Frontend: `http://localhost:8080`
- Backend: `http://localhost:8000`
- Worker: isolated background worker process

## Kubernetes

Kubernetes manifests are under `deploy/k8s` and can be applied with Kustomize:

```bash
kubectl apply -k deploy/k8s
```

### What is included

- `backend.yaml`: API deployment/service with rolling update strategy and probes.
- `frontend.yaml`: web deployment/service with rolling update strategy and probes.
- `worker.yaml`: isolated worker deployment with node selector/tolerations.
- `autoscaling.yaml`: HPAs for backend and worker.
- `namespace.yaml`: dedicated namespace.
- `stage-execution-job.yaml`: one-off isolated stage execution job template.
- `pipeline-scheduler-cronjob.yaml`: scheduled pipeline launcher using Kubernetes CronJobs.


### Job-based stage execution

Run a one-off stage execution in an isolated container:

```bash
kubectl apply -f deploy/k8s/stage-execution-job.yaml
```

This Job includes:
- `backoffLimit` retries for transient failures
- `activeDeadlineSeconds` for hung-task protection
- `ttlSecondsAfterFinished` for automatic cleanup
- worker `nodeSelector` + tolerations for resource isolation

### Scheduled pipelines with CronJobs

Use Kubernetes CronJobs for recurring pipeline runs:

```bash
kubectl apply -f deploy/k8s/pipeline-scheduler-cronjob.yaml
```

The CronJob is configured for operational safety:
- `concurrencyPolicy: Forbid` to avoid overlapping runs
- execution deadline and retry limits
- retained job history for troubleshooting
- worker node pinning for isolated execution

## Managed Kubernetes options

These manifests are cloud-agnostic and can be deployed to:

- **AWS EKS**
- **Google GKE**
- **Azure AKS**

### Recommended managed-cluster setup

1. Create separate node pools for API/web and workers.
2. Label/taint worker nodes to enforce isolation:
   - Label: `workload=worker`
   - Taint: `dedicated=worker:NoSchedule`
3. Install Metrics Server (or provider equivalent) for HPA.
4. Use a cloud load balancer + Ingress controller for public access.
5. Push images to a cloud registry (ECR/GAR/ACR) and update image references.

## Notes

- Replace placeholder image names (`ghcr.io/your-org/...`) before deployment.
- Consider adding PodDisruptionBudgets, NetworkPolicies, and secrets management for production hardening.
