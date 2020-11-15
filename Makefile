SHELL := /bin/bash

# Makefile to structure work on the AI-DO baselines.

# ==================== FOR DATA EXTRACTION ====================

# This runs in a docker container. Dependencies are taken care of.
# ---------------- DOCKER -----------------------------------
docker_extract_data:
				docker build -t extract_container -f Dockerfile_extract_data .; \

# Extract data from docker container and copies it to the learning repository
docker_copy_for_learning:
				mkdir -p data; \
				docker create -it --name dummy_for_copying extract_container:latest bash; \
				docker cp dummy_for_copying:/workspace/data/duckietown data/duckietown; \
				docker rm -fv dummy_for_copying;

# ==================== FOR MODEL LEARNING ====================

VIRTUALENV = LF_IL_virtualenv_learning

# ---------- REGULAR --------------
# This assumes that you have GPU drivers installed already.

# If only CPU is available for computation on your machine,
# change the line "pip install tensorflow-gpu" to "tensorflow" (without the GPU option)
install-dependencies:
				virtualenv $(VIRTUALENV) --python=python3.7; \
				. $(VIRTUALENV)/bin/activate; \
				pip install --no-cache-dir -r requirements_learning.txt; \
				pip install --upgrade tensorflow-gpu==1.13.1;

learn-regular:
				. $(VIRTUALENV)/bin/activate; \
				python src/cnn_training_tensorflow.py; \
				python src/freeze_graph.py;

# ==================== FOR SUBMISSION ====================



build:
	dts build_utils aido-container-build --use-branch daffy --ignore-untagged


push: build
	dts build_utils aido-container-push --use-branch daffy


submit:
	dts challenges submit

submit-bea:
	dts challenges submit --impersonate 1639 --challenge all --retire-same-label
