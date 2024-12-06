# BlueSky Posting Service

I wanted a simple flow I could put into a Github or Azure DevOps pipeline.  Tho, in truth, this works for anything that one might want to slap a webhook out there for posting a link to BlueSky

## Usage

Just create a payload JSON with your username and password
```json
$ cat payload.json
{ "USERNAME": "myuser.bsky.social", "PASSWORD": "my!password#12354!", "TEXT": "Some Great website to check out. ", "LINK": "https://freshbrewed.science" }
```

Then you can launch a container locally
```
$ docker run -d -p 5550:5000 idjohnson/pybsposter:latest
$ curl -X POST http://localhost:5550/post -H "Content-Type: application/json" -d @payload.json
```

Note: there is a non dockerhub instance you can use at:
```
harbor.freshbrewed.science/library/pybsposter:latest
```

Or you can launch into Kubernetes with the manifest:
```
$ kubectl apply -f ./deploy.yaml
deployment.apps/pybsposter created
service/pybsposter created
```

Then port-forward
```
$ kubectl port-forward svc/pybsposter 5550:80
Forwarding from 127.0.0.1:5550 -> 5000
Forwarding from [::1]:5550 -> 5000
```

Obviously with Kubernetes you can fire up an ingress and serve things up (as I did), but the options are there.

## Future improvements

Right now it does not check if the total length exceeds the BlueSky limit (which I believe at present in 300 characters).

You'll see an error like this if you exceed it
```html
<!doctype html>
<html lang=en>
<title>500 Internal Server Error</title>
<h1>Internal Server Error</h1>
<p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>
```