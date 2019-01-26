# html_converter


Proxy for [Athenapdf](https://github.com/arachnys/athenapdf) based on aiohttp 
that gets an html file and returns it 
as a pdf file (using Athenapdf file converter in a docker container)

Usage:
- Install html_converter (pip install -e .)
- Get Athenapdf (sudo docker pull arachnysdocker/athenapdf)
- Run Athenapdf (sudo docker run --network host --rm 
arachnysdocker/athenapdf-service)
- Run html_converter (python -m html_converter). There you can specify
host and port. More about that: python -m html_converter -h
- Send request to http://localhost:8181/generate with your html file as bytes
- Get the pdf file back as a response

