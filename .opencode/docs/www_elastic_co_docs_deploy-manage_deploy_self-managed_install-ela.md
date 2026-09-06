# Start a single-node cluster in Docker | Elastic Docs

> Source: https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-basic
> Cached: 2026-09-06T08:01:05.731Z

---

# Start a single-node cluster in Docker

			
			
	

			
	Use Docker commands to start a single-node Elasticsearch cluster for development or testing. You can then run additional Docker commands to add nodes to the test cluster or run Kibana.

	
		Tip
	
	

- If you just want to test Elasticsearch in local development, refer to [Run Elasticsearch locally](/docs/deploy-manage/deploy/self-managed/local-development-installation-quickstart). Note that this setup is not suitable for production environments.

- This setup doesn’t run multiple Elasticsearch nodes or Kibana by default. To create a multi-node cluster with Kibana, use Docker Compose instead. See [Start a multi-node cluster with Docker Compose](/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-compose).

## [Hardened Docker images](#docker-wolfi-hardened-image)

You can also use the hardened [Wolfi](https://wolfi.dev/) image for additional security. Using Wolfi images requires Docker version 20.10.10 or higher.

To use the Wolfi image, append `-wolfi` to the image tag in the Docker command.

For example:

	
Latest

	
	
		
docker pull docker.elastic.co/elasticsearch/elasticsearch-wolfi:9.5.3
		
	

Specific version

	
	
		
docker pull docker.elastic.co/elasticsearch/elasticsearch-wolfi:<SPECIFIC.VERSION.NUMBER>
		
	

You can download and install a specific version of the Elastic Stack by replacing `<SPECIFIC.VERSION.NUMBER>` with the version number you want. For example, you can replace `<SPECIFIC.VERSION.NUMBER>` with 9.0.0.

## [Start a single-node cluster](#_start_a_single_node_cluster)

Install Docker. Visit [Get Docker](https://docs.docker.com/get-docker/) to install Docker for your environment.

If using Docker Desktop, make sure to allocate at least 4GB of memory. You can adjust memory usage in Docker Desktop by going to **Settings > Resources**.

Create a new docker network.

	
		
docker network create elastic
		
	

Pull the Elasticsearch Docker image.

	
Latest

	
	
		
docker pull docker.elastic.co/elasticsearch/elasticsearch:9.5.3
		
	

Specific version

	Replace `<SPECIFIC.VERSION.NUMBER>` with the Elastic Stack version number you want. For example, you can replace `<SPECIFIC.VERSION.NUMBER>` with 9.0.0. You'll use this same version number throughout this tutorial.

	
		
docker pull docker.elastic.co/elasticsearch/elasticsearch:<SPECIFIC.VERSION.NUMBER>
		
	

Optional: Install [Cosign](https://docs.sigstore.dev/cosign/system_config/installation/) for your environment. Then use Cosign to verify the Elasticsearch image’s signature.

	
Latest

	

	
		
wget https://artifacts.elastic.co/cosign.pub
cosign verify --key cosign.pub docker.elastic.co/elasticsearch/elasticsearch:9.5.3
		
	

The `cosign` command prints the check results and the signature payload in JSON format:

	
		
Verification for docker.elastic.co/elasticsearch/elasticsearch:9.5.3 --
The following checks were performed on each of these signatures:
  - The cosign claims were validated
  - Existence of the claims in the transparency log was verified offline
  - The signatures were verified against the specified public key
		
	

Specific version

	Replace `<SPECIFIC.VERSION.NUMBER>` with the version of the Docker image you downloaded.

	
		
wget https://artifacts.elastic.co/cosign.pub
cosign verify --key cosign.pub docker.elastic.co/elasticsearch/elasticsearch:<SPECIFIC.VERSION.NUMBER>
		
	

The `cosign` command prints the check results and the signature payload in JSON format:

	
		
Verification for docker.elastic.co/elasticsearch/elasticsearch:<SPECIFIC.VERSION.NUMBER> --
The following checks were performed on each of these signatures:
  - The cosign claims were validated
  - Existence of the claims in the transparency log was verified offline
  - The signatures were verified against the specified public key
		
	

Start an Elasticsearch container.

	
Latest

	
	
		
docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:9.5.3
		
	

	
		Tip
	
	Use the `-m` flag to set a memory limit for the container. This removes the need to [manually set the JVM size](/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-prod#docker-set-heap-size).

Machine learning features such as [semantic search with ELSER](/docs/solutions/search/semantic-search/semantic-search-elser-ingest-pipelines) require a larger container with more than 1GB of memory. If you intend to use the machine learning capabilities, then start the container with this command:

	
		
docker run --name es01 --net elastic -p 9200:9200 -it -m 6GB -e "xpack.ml.use_auto_machine_memory_percent=true" docker.elastic.co/elasticsearch/elasticsearch:9.5.3
		
	

The command prints the `elastic` user password and an enrollment token for Kibana.

Specific version

	Use the same Elastic Stack version number as the Docker image you pulled earlier and replace `<SPECIFIC.VERSION.NUMBER>` with it.

	
		
docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:<SPECIFIC.VERSION.NUMBER>
		
	

	
		Tip
	
	Use the `-m` flag to set a memory limit for the container. This removes the need to [manually set the JVM size](/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-prod#docker-set-heap-size).

Machine learning features such as [semantic search with ELSER](/docs/solutions/search/semantic-search/semantic-search-elser-ingest-pipelines) require a larger container with more than 1GB of memory. If you intend to use the machine learning capabilities, then start the container with this command:

	
		
docker run --name es01 --net elastic -p 9200:9200 -it -m 6GB -e "xpack.ml.use_auto_machine_memory_percent=true" docker.elastic.co/elasticsearch/elasticsearch:<SPECIFIC.VERSION.NUMBER>
		
	

The command prints the `elastic` user password and an enrollment token for Kibana.

Copy the generated `elastic` password and enrollment token. These credentials are only shown when you start Elasticsearch for the first time. You can regenerate the credentials using the following commands.

	
		
docker exec -it es01 /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
docker exec -it es01 /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana
		
	

We recommend storing the `elastic` password as an environment variable in your shell. Example:

	
		
export ELASTIC_PASSWORD="your_password"
		
	

Copy the `http_ca.crt` SSL certificate from the container to your local machine.

	
		
docker cp es01:/usr/share/elasticsearch/config/certs/http_ca.crt .
		
	

Make a REST API call to Elasticsearch to ensure the Elasticsearch container is running.

	
		
curl --cacert http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200
		
	

## [Add more nodes](#_add_more_nodes)

Use an existing node to generate a enrollment token for the new node.

	
		
docker exec -it es01 /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s node
		
	

The enrollment token is valid for 30 minutes.

Start a new Elasticsearch container. Include the enrollment token as an environment variable.

	
Latest

	
	
		
docker run -e ENROLLMENT_TOKEN="<token>" --name es02 --net elastic -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:9.5.3
		
	

Specific version

	Use the same Elastic Stack version number as the Docker image you pulled earlier and replace `<SPECIFIC.VERSION.NUMBER>` with it.

	
		
docker run -e ENROLLMENT_TOKEN="<token>" --name es02 --net elastic -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:<SPECIFIC.VERSION.NUMBER>
		
	

Call the [cat nodes API](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-cat-nodes) to verify the node was added to the cluster.

	
		
curl --cacert http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200/_cat/nodes
		
	

## [Run Kibana](#run-kibana-docker)

Pull the Kibana Docker image.

	
Latest

	
	
		
docker pull docker.elastic.co/kibana/kibana:9.5.3
		
	

Specific version

	Use the same Elastic Stack version number as the Docker image you pulled earlier and replace `<SPECIFIC.VERSION.NUMBER>` with it.

	
		
docker pull docker.elastic.co/kibana/kibana:<SPECIFIC.VERSION.NUMBER>
		
	

Optional: Verify the Kibana image’s signature.

	
Latest

	
	
		
wget https://artifacts.elastic.co/cosign.pub
cosign verify --key cosign.pub docker.elastic.co/kibana/kibana:9.5.3
		
	

Specific version

	Use the same Elastic Stack version number as the Docker image you pulled earlier and replace `<SPECIFIC.VERSION.NUMBER>` with it.

	
		
wget https://artifacts.elastic.co/cosign.pub
cosign verify --key cosign.pub docker.elastic.co/kibana/kibana:<SPECIFIC.VERSION.NUMBER>
		
	

Start a Kibana container.

	
Latest

	
	
		
docker run --name kib01 --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:9.5.3
		
	

Specific version

	Use the same Elastic Stack version number as the Docker image you pulled earlier and replace `<SPECIFIC.VERSION.NUMBER>` with it.

	
		
docker run --name kib01 --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:<SPECIFIC.VERSION.NUMBER>
		
	

When Kibana starts, it outputs a unique generated link to the terminal. To access Kibana, open this link in a web browser.

In your browser, enter the enrollment token that was generated when you started Elasticsearch.

To regenerate the token, run:

	
		
docker exec -it es01 /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana
		
	

Log in to Kibana as the `elastic` user with the password that was generated when you started Elasticsearch.

To regenerate the password, run:

	
		
docker exec -it es01 /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
		
	

## [Remove containers](#remove-containers-docker)

To remove the containers and their network, run:

	
		
# Remove the Elastic network
docker network rm elastic

# Remove Elasticsearch containers
docker rm es01
docker rm es02

# Remove the Kibana container
docker rm kib01
		
	
## [Next steps](#_next_steps_5)

You now have a test Elasticsearch environment set up. Before you start serious development or go into production with Elasticsearch, review the [requirements and recommendations](/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-prod) to apply when running Elasticsearch in Docker in production.