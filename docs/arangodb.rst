Setting up ArangoDB 
=====================

This section explains how to set up and access **ArangoDB** for our project.

Prerequisites
-------------
- Install `Docker <https://www.docker.com/get-started/>`_
- Access to UMBC Wi-Fi or UMBC GlobalProtect VPN

Local Setup with Docker
-----------------------

We use the official ArangoDB Docker image. You can find it here:
`ArangoDB on Docker Hub <https://hub.docker.com/_/arangodb>`_

Steps:

1. Pull the image:
    
    .. code-block:: bash

        docker pull arangodb

2. Run the container (example):

    .. code-block:: bash

        docker run -d -p 8529:8529 -e ARANGO_RANDOM_ROOT_PASSWORD=1 --name arangodb-instance arangodb

3. Verify that it's running:

    .. code-block:: bash

        docker ps
    
This will list all active containers. Look for ``arangodb-instance``.

4. Find your randomly generated password (run locally):

    .. code-block:: bash

        docker logs arangodb-instance

5. Access and sign in:

    - Navigate to http://localhost:8529
    - **Username**: ``root``
    - **Password**: as shown in the logs above

Accessing the Real Knowledge Graph (KG)
---------------------------------------

If you would like to view our deployed Knowledge Graph instance:

- You **must** be connected to the UMBC Wi-Fi or connect with the `UMBC GlobalProtect VPN <https://umbc.atlassian.net/wiki/spaces/faq/pages/30754220/Getting+Connected+with+the+UMBC+GlobalProtect+VPN>`_

- Navigate to::

    http://visionpc01.cs.umbc.edu:8529

- Sign in with:

  - **Username**: ``root``
  - **Password**: Run the following command in the DAMS server to retrieve it from the container logs:

    .. code-block:: bash

      docker logs arangodb-instance

Notes
-----

- The local Docker setup is ideal for **testing** and **development**.
- The deployed instance (``visionpc01``) is the **source of truth** for the project.
- Make sure to use VPN access if you're working remotely.