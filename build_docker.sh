

APPWORKDIR="$(pwd)"
BUILDENV="dev"



DOCKER_BUILDKIT=1 docker build --target=runtime . \
    -t collagerator \
    --build-arg APPWORKDIR=$APPWORKDIR \
    --build-arg BUILDENV=$BUILDENV