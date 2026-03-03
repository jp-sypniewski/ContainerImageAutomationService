# Container Image Automation Service

## Overview
REST API service written in Python (Flask) that automates container publishing
workflows for applications built within OKD/OpenShift clusters.
Designed to integrate with CI/CD pipelines and reduce manual image promotion
steps.

## Problem
Applications built via OKD BuildConfigs can produce images in internal
ImageStreams. Promoting these images to external registries (Docker Hub)
required manual tagging and inconsistent pipeline logic across environments.

## Solution
This service:
- Accepts image identifiers produced by OKD builds
- Pushes images to Docker Hub
- Can be triggered via Jenkins httpRequest or curl
- Centralizes image promotion logic outside of pipeline scripts

## Tech Stack
- Python
- Flask
- Docker
- OKD (Kubernetes-based platform)
- OpenShift CLI (`oc`) for image operations
- Gunicorn (WSGI server)

## Example Request
```
curl -X POST http://localhost:8080/push-image-to-dockerhub \
  -H "Content-Type: application/json" \
  -d '{"image": "application-name-timestamp"}'
```

## Running Locally

### Build Image
`docker build -t image-automation-service .`

### Run Container
`docker run -p 8080:8080 image-automation-service`

## Future Improvements
- Implement OpenAPI specification for API contract definition
- Add unit and integration tests
- Move image tagging logic fully into service (currently assumed as handled by caller)
- Add authentication and role-based access control