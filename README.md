# pybsposter - A Webhook-based Social Media Poster for BlueSky and Mastodon

`pybsposter` is a simple, containerized Python service that accepts webhook payloads to post messages and links to [BlueSky](https://bsky.app/) and [Mastodon](https://joinmastodon.org/). It's designed for easy integration with CI/CD pipelines (like GitHub Actions or Azure DevOps) or any other system that can trigger a webhook.

## High-Level Overview

![Component Diagram](docs/diagrams/component.png)

## Quick Start

The fastest way to get started is to run the pre-built container image from Docker Hub.

```bash
# Run the container in the background, mapping port 5550 on your host to port 5000 in the container
docker run -d -p 5550:5000 idjohnson/pybsposter:latest
```

Once running, the service is ready to accept POST requests. See the **API Usage** section below for details on the payloads.

*Note: A non-Docker Hub image is also available at `harbor.freshbrewed.science/library/pybsposter:latest`.*

## API Usage

The service provides separate endpoints for posting to BlueSky and Mastodon.

### BlueSky

To post to BlueSky, send a `POST` request to the `/post` endpoint with a JSON payload.

#### Endpoint

`POST /post`

#### Payload Parameters

*   `USERNAME` (string, required): Your BlueSky username (e.g., `myuser.bsky.social`).
*   `PASSWORD` (string, required): **Use a BlueSky App Password!** Do not use your main account password.
*   `TEXT` (string, required): The text content of your post.
*   `LINK` (string, required): The URL you want to include in the post.

#### :warning: Security Warning (BlueSky)

**DO NOT use your primary BlueSky password.** It is extremely insecure to store your main password in configuration files or send it directly via API calls.

Instead, **create a dedicated App Password** from your BlueSky settings. This is a standard security practice that limits the potential damage if a password is leaked.

1.  Go to **Settings** in your BlueSky client.
2.  Navigate to **App Passwords**.
3.  Generate a new password and give it a descriptive name (e.g., `pybsposter-webhook`).
4.  Use *that* password in your payload.

#### Example `curl` Request (BlueSky)

1.  **Create the payload file (e.g., `bsky-payload.json`):**
    ```json
    {
        "USERNAME": "myuser.bsky.social",
        "PASSWORD": "xxxx-xxxx-xxxx-xxxx",
        "TEXT": "Check out this awesome website I found!",
        "LINK": "https://freshbrewed.science"
    }
    ```

2.  **Send the request:**
    ```bash
    curl -X POST http://localhost:5550/post \
         -H "Content-Type: application/json" \
         -d @bsky-payload.json
    ```

---

### Mastodon

To post to Mastodon, send a `POST` request to the `/post/mastodon` endpoint with a JSON payload.

---

### Threads

To post to Threads, send a `POST` request to the `/post/threads` endpoint with a JSON payload.

#### Endpoint

`POST /post/threads`

#### Payload Parameters

*   `user_id` (string, required): Your Threads user ID.
*   `access_token` (string, required): Your Threads **Access Token**. This is used for authentication with the Threads API.
*   `text` (string, required): The text content of your post.
*   `link` (string, optional): A URL to include in your post.

#### :warning: Security Warning (Threads)

**DO NOT use your primary Threads/Instagram password.** You must use an **Access Token** for authentication.

To obtain a Threads Access Token:

1.  Create a Threads app in the [Meta for Developers](https://developers.facebook.com/) portal.
2.  Configure your app with the necessary permissions for posting (`threads_basic` and `threads_content_publish`).
3.  Complete the OAuth flow to obtain a long-lived access token.
4.  Your **user_id** can be obtained from the Threads API after authentication.
5.  Use the access token as the `access_token` in your payload.

Refer to the [Threads API documentation](https://developers.facebook.com/docs/threads) for detailed setup instructions.

#### Example `curl` Request (Threads)

1.  **Create the payload file (e.g., `threads-payload.json`):**
    ```json
    {
        "user_id": "123456789",
        "access_token": "YOUR_THREADS_ACCESS_TOKEN",
        "text": "Hello from pybsposter!",
        "link": "https://freshbrewed.science"
    }
    ```

2.  **Send the request:**
    ```bash
    curl -X POST http://localhost:5550/post/threads \
         -H "Content-Type: application/json" \
         -d @threads-payload.json
    ```

---

#### Endpoint

`POST /post/mastodon`

#### Payload Parameters

*   `baseURL` (string, required): The base URL of your Mastodon instance (e.g., `https://mastodon.social`).
*   `PASSWORD` (string, required): Your Mastodon **Access Token**. This is used for authentication.
*   `TEXT` (string, required): The text content of your toot.
*   `LINK` (string, optional): A URL to include in your toot.
*   `USERNAME` (string, required): This field is currently required by the API but is **not used** for Mastodon posting. You can provide any non-empty string.

#### :warning: Security Warning (Mastodon)

**DO NOT use your primary Mastodon password.** You must use an **Access Token** for authentication.

1.  In your Mastodon instance, go to **Preferences** -> **Development**.
2.  Click **New Application**.
3.  Give your application a name (e.g., `pybsposter-webhook`).
4.  Ensure the `write:statuses` scope is checked.
5.  Save the application.
6.  Your **Access Token** will be displayed on the next page. Use this token as the `PASSWORD` in your payload.

#### Example `curl` Request (Mastodon)

1.  **Create the payload file (e.g., `mastodon-payload.json`):
    ```json
    {
        "baseURL": "https://mastodon.social",
        "PASSWORD": "YOUR_MASTODON_ACCESS_TOKEN",
        "TEXT": "This is a test post to Mastodon from my awesome service!",
        "LINK": "https://freshbrewed.science",
        "USERNAME": "unused"
    }
    ```

2.  **Send the request:**
    ```bash
    curl -X POST http://localhost:5550/post/mastodon \
         -H "Content-Type: application/json" \
         -d @mastodon-payload.json
    ```

## Deployment

The service is designed to be deployed easily in containerized environments like Kubernetes.

### Kubernetes

YouYou can deploy the service using the provided `deploy.yaml` manifest. This will create a `Deployment` and a `Service`.

```bash
# Apply the manifest to your cluster
kubectl apply -f ./deploy.yaml
```

To access the service from your local machine, you can use `port-forward`:

```bash
# Forward local port 5550 to the service's port 80
kubectl port-forward svc/pybsposter 5550:80
```

For production use, you should configure an Ingress controller to expose the service publicly and handle TLS termination.

### Helm

A Helm chart is available in the `charts/pybsposter` directory for more configurable deployments.

```bash
# Install the chart
helm install pybsposter ./charts/pybsposter

NAME: pybsposter
LAST DEPLOYED: Fri Dec  6 07:37:34 2024
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

You can customize the deployment by modifying the `values.yaml` file within the chart.

### Docker Compose

For those who prefer `docker-compose`, a `docker-compose.yaml` file is provided in the root of the repository.

```bash
# Start the service in detached mode
docker-compose up -d
```

This will start the service and expose it on port 8000.

## Local Development

If you need to build the image locally for testing or development.

1.  **Build the Docker image:**
    ```bash
    # Tag the image as 'mytest:01'
    docker build -t mytest:01 .
    ```

2.  **Run the Docker container:**
    You can set the `VERSION` environment variable to display a version (e.g., the current Git SHA) at startup. The service runs on port 8000 inside the container.

    ```bash
    # Run the container, mapping host port 8000 to container port 8000
    docker run -p 8000:8000 -e VERSION=$(git rev-parse --short HEAD) mytest:01
    ```

## Limitations and Error Handling

*   **Post Length:**
    *   **BlueSky:** The service does not currently validate the total post length. BlueSky has a limit of 300 characters. If your combined `TEXT` and `LINK` exceed this, the post will be trimmed automatically.
    *   **Mastodon:** The default character limit is 500 characters. The service will trim posts that exceed this limit.
*   **Error Responses:** Invalid credentials or other API issues will also likely result in a `500` error. Future versions should provide more specific error feedback.
