# Lab-Kubernetes-Istio

## Kubernetes  
Kubernetes (abbreviation: K8s) is an open-source platform that enables managing containerized workloads and services. The huge advantages of the project are  
its portability, extensibility and flexibiliy. It very important to understand that k8s is not a standalone virtualization platform but rather an extremely  
useful tool to orchestrate microservices virtualized using other solutions (e.g. Docker). Kubernetes perfectly fits the ongoing IT trends aiming to refactor huge monolith  
applications to smaller and easily handled separate functionalities wrapped in microservices. The most important and popular Kubernetes usages include:  
* **Service Discovery and load balancing** -- balance load between multiple containers present in a cluster and expose your application using either DNS or customised IP address,  
* **Storage orchestration** -- make best use of different storage locations including local storages, cloud providers and more,  
* Automated rollouts and rollbacks -- specify a desired version of your application across each container and be able to easily change it anytime you want, on a chosen machine inside a cluster  
* **Automatic bin packing** -- make the best use of your resources and customize the usage per cluster  
* **Self-healing** -- do not worry about containers availability. K8s replaces failed and non-responding continers for you and periodically runs health checks  
* **Secret and configuration management** -- easily manage ssh passwords and certificates without the need to rebuild the container images and exposing sensitive information in your network stack  

In the below picture the typical K8s cluster architecture is presented.  
The most important thing to remember from it is that the cluster consists of worker machines (nodes). Each node is later divided into components of the application  
workload (pods). The control plane usually spans across multiple computers within the cluster. Such infrastructure provides scalable and fault tolerant architcture.   
![k8s architecture](k8s-components.svg)

## Istio

Firstly let's describe what a service mesh is. It is a dedicated infrastructure layer, that can be easily added to the
application and provide functionalities like observability, traffic management and security out of the box. We don't
have to add any additional code by ourselves.

Istio is a service mesh. It also provides more complex capabilities and help with solving problems related to the rate
limiting, encryption, A/B testing etc.

### How does it work?

There are two main components:

#### Data plane

You can consider data plane as a huge number of envoy proxies which run alongside services running in K8s. They
intercept all the network traffic that was designed to reach the specific application.

#### Control plane

Control plane, checks the desired configuration and dynamically updates the proxy servers according to the specified
rules.

## Tutorial
Before continuing with the exercise, let's sum up what we have already learned about Istio and what it actually does under the hood. The concepts of the data and control planes were already introduced above so you should be familiar with them. Together they make a service mesh (introduced above as well). As such, Istio is an open source solution that can be merged with an existing codebase without the need of changing the code itself. The solution acts as a parent component to the whole infrastructure and makes it really easy to enforce security measures, A/B testing, observability, traffic management and so on to your application and everything is working almost out of the box. 

The great advantage is the dynamic configuration handled by the control plane (as _.yaml_ config files) so you'll never have to manually change any of the envoy proxies. The Istio's impact on the application can be visualized as shown in the image below.  
![Istio impact on an app](service-mesh.svg)  

As part of this tutorial you can also slowly go through all of the below described steps in order to quickly set up a custom containerized flask application and Istio routing rules that work right out of the box. This way you can see how easy it is to manage traffic inside k8s container. The provided application answers to GET requests (<url>/hostname path) by returning a hostname of the node handling the particular request. That's an easy and efficient way to visualize traffic management concepts.
1. issue `minikube start` to start a cluster environment
2. cd to tutorial/ directory
3. issue ` eval $(minikube -p minikube docker-env)` to make use of a local k8s and docker registry
4. issue `docker build -f Dockerfile -t tip-app:latest .` to containerize provided flask application
5. let's install Istio mesh inside minikube cluster --- issue `istioctl install --set profile=demo -y` followed by `kubectl label namespace default istio-injection=enabled` to perform the installation and automatically inject Istio traffic envoys to created pods.  
6. issue `kubectl apply -f flask-deploy.yaml` to create pods with just built docker image
7. to verify whether pods are running you can issue `kubectl get pods`. There should be no errors
8. in a new terminal window issue `minikube tunnel` in order to be able to access the flask app outside of the cluster, from your host machine 
9. Let's set up an Istio gateway to redirect each request through the minikube tunnel. Type in your terminal `kubectl apply -f flask-gateway.yaml`
10. verify all the performed steps by typing `istioctl analyze`. There should be no errors 
11. The Flask applicatioon should be reachable now from your host machine. In order to perform a GET request issue below commands. The first one will return an IP address, the second one a port. Using them one can reach the app.  
`export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')`  
`export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].port}')`  
Now you can issue `curl http://INGRESS_HOST:INGRESS_PORT/hostname` to perform a GET request to the Flask application. You can see that each time you perform a request, a different container responds. 
11. Let's try to change that and route all requests only to the containers named flask1.*. Set up decision rules that we will later use for traffic management --- issue `kubectl apply -f dest-rules.yaml`
12.  With the rules all set up let's move all requests to flask1.* containers by typing `kubectl apply -f flask-gateway100.yaml`. Validate your actions with already introduced command `istioctl analyze`. Try to send some requests now. Each response received should come only from 2 out of 4 containers named flask1.*
13. Issuing `kubectl apply -f flask-gateway50.yaml` will change the applicaton behaviour to handle traffic in a 50/50 way. Approximately 50% of requests should be routed to containers named flask1.* and 50% of traffic to containers named flask2.*. 
14. All set up. You can play with the provided files or move right to the next exercises where you will be asked to write some rules yourself. 


The other DIY exercises are as follows:  
1. **Set up your environment** --- you will learn how to install minikube, kiali and Istio tools. Then you will launch an examplary application in order to verify that everything works as expected.

3. **Request Routing** --- you will have a cluster running different versions of your application. Based on various criteria specified later on you are going to implement rules that will change the way traffic is routed within you application. Some of the users will see version 1 of your app whereas the others will see different versions. 

5. **Fault Injection** --- In this part of the exercise you are going to test whether you application is fault tolerant. You will use Istio's fault injection rules to introduce a delay to your application and find possible bugs and problems your customers may encounter. A healthy application means a happy customer!  

7. **Traffic Shifting** --- The last part of this laboratory session will give you tools to seemlessly migrate your application between versions (e.g sequentially deploy a new version of the app). With Istio you can do it without having to manually rebuild and reboot all your containers within the cluster. In order to do so you are going to use envoy sidecar implementation and a feature called weighted roouting. By specyfing an appropriate rule you will have a given percentage of users routed to a different version of your app. If it works, you can deploy it across the whole cluster. Perfect! 
Now that you know everything, ready your command line and get to work!  
---

## Exercise

For the exercise, we will be using the default application and the default tutorial provided by the Istio team.

### Installation

Istio installation can be found on the site: https://istio.io/latest/docs/setup/getting-started/

Minikube installation: https://minikube.sigs.k8s.io/docs/start/

#### Step 1

Run command
``
minikube start
``
to start Your cluster

#### Step 2

Run command
``
istioctl install --set profile=demo -y
``
to set the profile to demo, so that the demo profile is used, and we can use defaults for the application. Also this
profile enables high level of tracing and access logging. As the result, You should something similar to this:

![img.png](exercise/step2.png)

#### Step 3

Run command
``
kubectl label namespace default istio-injection=enabled
``
to set automatic injection of envoy side proxies.

#### Step 4

Run command
``
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml
``
in the istio directory(make sure that You run the correct path).

![img.png](exercise/step4.png)

??? No validation issues found when analyzing namespace: default.

#### Step 5

Create gateway and the destination rules
``
kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml kubectl apply -f samples/bookinfo/networking/destination-rule-all.yaml
``

#### Step 6

Verify that all the services running in the kube
``
kubectl get services
``
![img.png](exercise/step4.png)

#### Step 7

Verify that everything works from the istio side
``
istioctl analyze
``

??? No validation issues found when analyzing namespace: default.

#### Step 8

Verify that You can access productpage: We need the host, and the port for the gateway:

In another terminal, run

````
minikube tunnel
````

And in the current one, run:

````
export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')
export INGRESS_HOST=$(minikube ip)
export GATEWAY_URL=$INGRESS_HOST:$INGRESS_PORT

echo "http://$GATEWAY_URL/productpage"
````

You should see the reviews on the URL.

#### Step 9

We will install kiali - dashboard for istio

```
kubectl apply -f samples/addons/kiali.yaml
kubectl rollout status deployment/kiali -n istio-system
istioctl dashboard kiali
```

### Real task

If You reach this point, You should be able to both reach the kiali dashboard, and see the product page of the system.
Kiali is useful tool to visualize the whole graph of our microservices in the cluster. Architecture of the services
which we will be using.

![img.png](exercise/architecture.png)

As You can see, we have 3 versions of the review app, v1 -> without any stars, v2 -> with black stars and v3 with red
stars.

#### Task 1 Simulate Deployment and weighted rerouting of people

Create Virtual Service which will update the user routing for all the users which login start with Your initials.
Configuration for the user routing:

- around 9 per 10 requests should be routed to the reviews with the version v2
- other requests should be routed to the version with the v1
- other users are unaffected
- specify the timeout that envoy proxy should wait for replies to the 15s
- specify amount of the replies, so that it will try to retry the call 5 times, each with a 5 second timeout

Solution put in the file exercise/user-routing.yaml and apply it to the cluster. Then apply it to the cluster and verify
whether it works.

HINT: header _end-user_ is sent all the time with the login of the user. Add the http match for this header.

#### Task 2 Testing Fault Tolerance

Use the file which You have prepared for the previous task. Extend it by adding the 20s delay for half of the requests
to the ratings for You.

Then verify that sometimes, Your application receives an error fetching product reviews.

#### DIY Task 3 Traffic Mirroring

Using the file that You have already configured testing and fault tolerance for the application, mirror all the logs to
the version v3. Verify logs from the application to check whether they reach the version v3.

Important:

Do not expect that You will see ratings with the red stars. Mirroring of the traffic is done with the fire and forget
method, so all the responses are discarded.

## Solution and Ideas

Solution file are presented in the solution directory.

### Task 1 Simulate Deployment and weighted rerouting of people

In this task, You had learned how easy it is to reroute specific calls to the appropriate services. Imagine situation,
where You are trying to deploy the new version of Your microservice. You can easily specify which users, and how often
are they using new version. What is more, as You see, You can even specify different amount of retries and timeouts for
the new version. Then If You are happy with the testing, You can easily remove the matching and move all the users to
the new microservice.

### Task 2 Testing Fault Tolerance

In this task, You had learned that, we can easily check, what could happen if there would be any timeout in our
application. We could even observe on the frontend, whether the appropriate error message is shown. Also, we can
instantly shift the traffic to other versions of application just as in the task 1.

### DIY Task 3 Traffic Mirroring

In huge, enterprise application, testing Your microservices, just as the user would use them is a huge benefit for the
company. Therefore, preparing out of the box traffic mirroring to the new microservices, it's a huge advantage. By using
that, we can easily make sure that all the requests that are being made to the testing environment with the new version
are tested, and we can generate test suites based on them. What is more, we can easily monitor everything that is
happening in our cluster and make sure that no strange requests occur without affecting production environment.
