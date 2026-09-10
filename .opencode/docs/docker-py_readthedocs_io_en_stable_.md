# Docker SDK for Python &#8212; Docker SDK for Python 7.2.0 documentation

> Source: https://docker-py.readthedocs.io/en/stable/
> Cached: 2026-09-10T08:45:51.139Z

---

# [Docker SDK for Python](#)

A Python library for the Docker Engine API

### Navigation

- [Client](client.html)

- [Configs](configs.html)

- [Containers](containers.html)

- [Images](images.html)

- [Networks](networks.html)

- [Nodes](nodes.html)

- [Plugins](plugins.html)

- [Secrets](secrets.html)

- [Services](services.html)

- [Swarm](swarm.html)

- [Volumes](volumes.html)

- [Low-level API](api.html)

- [Using TLS](tls.html)

- [User guides and tutorials](user_guides/index.html)

- [Changelog](change-log.html)

  ### Quick search

    
    
      
      
    
    

        
      
      
        
          

          
            
  
# Docker SDK for Python[¶](#docker-sdk-for-python)

A Python library for the Docker Engine API. It lets you do anything the `docker` command does, but from within Python apps – run containers, manage containers, manage Swarms, etc.

For more information about the Engine API, [see its documentation](https://docs.docker.com/engine/reference/api/docker_remote_api/).

## Installation[¶](#installation)

The latest stable version [is available on PyPI](https://pypi.python.org/pypi/docker/). Either add `docker` to your `requirements.txt` file or install with pip:

pip install docker

## Getting started[¶](#getting-started)

To talk to a Docker daemon, you first need to instantiate a client. You can use [`from_env()`](client.html#docker.client.from_env) to connect using the default socket or the configuration in your environment:

import docker
client = docker.from_env()

You can now run containers:

>>> client.containers.run("ubuntu", "echo hello world")
'hello world\n'

You can run containers in the background:

>>> client.containers.run("bfirsh/reticulate-splines", detach=True)
<Container '45e6d2de7c54'>

You can manage containers:

>>> client.containers.list()
[<Container '45e6d2de7c54'>, <Container 'db18e4f20eaa'>, ...]

>>> container = client.containers.get('45e6d2de7c54')

>>> container.attrs['Config']['Image']
"bfirsh/reticulate-splines"

>>> container.logs()
"Reticulating spline 1...\n"

>>> container.stop()

You can stream logs:

>>> for line in container.logs(stream=True):
...   print(line.strip())
Reticulating spline 2...
Reticulating spline 3...
...

You can manage images:

>>> client.images.pull('nginx')
<Image 'nginx'>

>>> client.images.list()
[<Image 'ubuntu'>, <Image 'nginx'>, ...]

That’s just a taste of what you can do with the Docker SDK for Python. For more, [take a look at the reference](client.html).

          
          
        
      
    
  
    
      &#169;2026 Docker Inc.
      
      |
      Powered by [Sphinx 5.1.1](https://www.sphinx-doc.org/)
      & [Alabaster 0.7.16](https://alabaster.readthedocs.io)
      
      |
      [Page source](_sources/index.rst.txt)