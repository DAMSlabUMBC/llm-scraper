UMBC DAMS Server
================

The **DAMS server** hosts our deployed instance of the Knowledge Graph (KG).

- Web access: http://visionpc01.cs.umbc.edu:8529
- Hostname: ``visionpc01.cs.umbc.edu``

Getting Access
--------------

To get an account on the DAMS server, please contact the project leads.

SSH Access
----------

You can log into the server via SSH:

.. code-block:: bash

   ssh <username>@visionpc01.cs.umbc.edu

ArangoDB Instance
-----------------

Currently, if the ArangoDB instance shuts down, all data is lost except for what is stored on disk. To re-run the ArangoDB instance, use the following commands.

1. Run the container:

   .. code-block:: bash

      docker run -d -p 8529:8529 -e ARANGO_RANDOM_ROOT_PASSWORD=1 --name arangodb-instance arangodb

2. Verify that it's running:

   .. code-block:: bash

      docker ps

   Look for ``arangodb-instance`` in the process list.

3. Find the randomly generated password:

   .. code-block:: bash

      docker logs arangodb-instance

4. Access and sign in:

    - Navigate to http://visionpc01.cs.umbc.edu:8529
    - **Username**: ``root``
    - **Password**: as shown in the logs above