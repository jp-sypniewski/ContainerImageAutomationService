# Use latest stable Python slim image
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/opt/app

# Install system dependencies required for oc CLI and clean up afterwards
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl tar && \
    curl -L https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/linux/oc.tar.gz \
        -o /tmp/oc.tar.gz && \
    tar -xzf /tmp/oc.tar.gz -C /tmp && \
    mv /tmp/oc /usr/local/bin/oc && \
    chmod +x /usr/local/bin/oc && \
    rm -rf /tmp/oc.tar.gz && \
    apt-get purge -y --auto-remove curl tar && \
    rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR ${APP_HOME}

# Copy dependency file separately for better layer caching
COPY requirements.txt .

# Install Python dependencies without cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Ensure directory permissions are OpenShift compatible
RUN chgrp -R 0 ${APP_HOME} && \
    chmod -R g=u ${APP_HOME}

# Use non-root user (OpenShift compatible)
USER 1001

# Expose application port
EXPOSE 8080

# Start application with gunicorn
CMD ["gunicorn", "app:app", "-w", "4", "--threads", "4", "-b", "0.0.0.0:8080"]