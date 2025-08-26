# DevOps Pipeline with Django, Chef Habitat, Ansible Galaxy, and Argo CD

This README provides step-by-step instructions to build, package, and deploy a simple Django app using **Chef Habitat**, **Ansible Galaxy**, and **Argo CD**.

---

## 📌 Prerequisites
- Python 3.x + pip
- Docker installed and running
- Minikube or a Kubernetes cluster
- kubectl configured
- Git + GitHub account
- Argo CD installed on cluster

---

## 🚀 Steps

### 1. Setup Django Project
```bash
mkdir django-devops-demo && cd django-devops-demo
python3 -m venv venv
source venv/bin/activate
pip install django
django-admin startproject demo_project .
pip freeze > requirements.txt
python manage.py runserver 0.0.0.0:8000
```

### 2. Dockerize Django App
Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

Build & push image:
```bash
docker build -t <your-dockerhub-username>/django-demo:latest .
docker push <your-dockerhub-username>/django-demo:latest
```

### 3. Create Kubernetes Manifests
Inside `k8s/` folder:

**deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: django-demo
  template:
    metadata:
      labels:
        app: django-demo
    spec:
      containers:
        - name: django-demo
          image: <your-dockerhub-username>/django-demo:latest
          ports:
            - containerPort: 8000
```

**service.yaml**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: django-demo-service
spec:
  selector:
    app: django-demo
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
  type: NodePort
```

Apply locally (optional test):
```bash
kubectl apply -f k8s/
minikube service django-demo-service
```

### 4. Push to GitHub
```bash
git init
git remote add origin git@github.com:<your-username>/argo_cd.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 5. Install Argo CD
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl port-forward svc/argocd-server -n argocd 9090:443
```

Get password:
```bash
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d
```

Login at: https://localhost:9090

### 6. Create ArgoCD Application
Create `argocd-app.yaml`:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: django-demo
  namespace: argocd
spec:
  project: default
  source:
    repoURL: git@github.com:<your-username>/argo_cd.git
    targetRevision: HEAD
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: django-demo
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Apply:
```bash
kubectl create namespace django-demo
kubectl apply -f argocd-app.yaml -n argocd
```

### 7. Access Django App
```bash
kubectl port-forward svc/django-demo-service -n django-demo 8000:8000
```
Open: http://localhost:8000

Or with Minikube:
```bash
minikube service django-demo-service -n django-demo
```

---

## ✅ Summary
- **Chef Habitat** → Package & lifecycle management (alternative to Docker)
- **Ansible Galaxy** → Automate infra setup (roles for Nginx, Postgres, etc.)
- **Argo CD** → GitOps continuous deployment to Kubernetes
