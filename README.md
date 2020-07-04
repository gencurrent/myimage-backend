# MyImage.io
# A project for image editing


# Build and push to the registry
`docker-compose -f docker-compose.prod.yml build`

`docker-compose -f docker-compose.prod.yml push`

Or use it in one line:

`docker-compose -f docker-compose.prod.yml build && docker-compose -f docker-compose.prod.yml push`