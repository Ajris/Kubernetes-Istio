docker build -f Dockerfile -t tip-app:latest .
minikube start
kubectl apply -f flask-deploy.yaml

echo "Issue 'kubectl get pods' to see the status of the pods.\nNow the service should be accsessible at http://localhost:6000"
