## Templates

### Building the model image

Navigate to [container](container) directory and run the following command

```shell
> ./build_and_push.sh <model-name>
```

Here `model-name` is the top-level directory under models. For example:

```shell
> ./build_and_push.sh nlp_spacy
```

### Test the container locally

```shell
> docker run -p 8080:8080 nlp_spacy
```

```shell
> curl -X POST -H "Content-Type: application/json"  -d '{"input": "Amazon Web Service is long for AWS"}' localhost:8080/invocations

{"output": [["Amazon Web Service", "ORG"]]}
```



