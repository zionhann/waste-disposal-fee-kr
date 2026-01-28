FROM public.ecr.aws/lambda/python:3.11

# Set environment variables
# We store models in the task root so they are part of the image and don't need downloading at runtime
ENV HF_HOME=${LAMBDA_TASK_ROOT}/.cache/huggingface \
    TORCH_HOME=${LAMBDA_TASK_ROOT}/.cache/torch \
    PYTHONPATH=${LAMBDA_TASK_ROOT}

WORKDIR ${LAMBDA_TASK_ROOT}

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and data
COPY app/ app/
COPY scripts/ scripts/
COPY waste_disposal_fee.csv .

# Create data directory
RUN mkdir -p data

# Download model and generate embeddings during build
RUN python scripts/download_model.py
RUN python scripts/generate_embeddings.py

# Set the CMD to the handler
CMD ["app.main.handler"]