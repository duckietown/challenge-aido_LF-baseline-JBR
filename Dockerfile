ARG AIDO_REGISTRY
FROM ${AIDO_REGISTRY}/duckietown/challenge-aido_lf-template-tensorflow:daffy-amd64

# let's create our workspace, we don't want to clutter the container
RUN rm -r /workspace; mkdir /workspace

WORKDIR /workspace

# let's copy all our solution files to our workspace
# if you have more file use the COPY command to move them to the workspace
# IMPORTANT: This should fail if "frozen_graph.pb" does not exist.
# This file will contain a learned model which the agent should execute.
COPY learned_models/frozen_graph.pb .
COPY requirements.txt .
COPY src/ src/

# here, we install the requirements, some requirements come by default
# you can add more if you need to in requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# necessary to get opencv to work properly
RUN apt update && apt install -y libsm6 libxext6

# CMD python solution.py
ENTRYPOINT ["python", "-m", "src.imitation.imitation_agent"]
