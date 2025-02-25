variable "DOCKERHUB_USERNAME" {
  default = "voicevox"
}

variable "TAG_BASE" {
  default = "${DOCKERHUB_USERNAME}/voicevox_engine"
}

variable "VOICEVOX_ENGINE_VERSION" {
  default = "latest"
}

variable "ENABLE_CACHE_TO" {
  default = false
}

function "make_cache_from" {
  params = [image_name]
  result = [
    {
      type = "registry"
      ref = "${TAG_BASE}:${image_name}-latest-buildcache"
    }
  ]
}

function "make_cache_to" {
  params = [image_name]
  result = ENABLE_CACHE_TO ? [
    {
      type = "registry"
      ref = "${TAG_BASE}:${image_name}-latest-buildcache",
      mode = "max"
    }
  ] : []
}

target "_common" {
  dockerfile = "Dockerfile"
  args = {
    PYTHON_VERSION = "3.11.9"
    VOICEVOX_ENGINE_VERSION = VOICEVOX_ENGINE_VERSION
    VOICEVOX_CORE_VERSION = "0.15.7"
    VOICEVOX_RESOURCE_VERSION = "0.22.2"
    ONNXRUNTIME_VERSION = "1.13.1"
  }
}

target "_cpu" {
  inherits = ["_common"]
  target = "runtime-env"
  platforms = ["linux/amd64", "linux/arm64/v8"]
}

target "_nvidia" {
  inherits = ["_common"]
  args = {
    USE_GPU = true
  }
  target = "runtime-nvidia-env"
  platforms = ["linux/amd64"]
}

target "_ubuntu20" {
  args = {
    BASE_IMAGE = "ubuntu:20.04"
  }
}

target "_ubuntu22" {
  args = {
    BASE_IMAGE = "ubuntu:22.04"
  }
}

target "cpu-ubuntu20" {
  inherits = ["_cpu", "_ubuntu20"]
  tags = ["${TAG_BASE}:cpu-ubuntu20.04-${VOICEVOX_ENGINE_VERSION}"]
  cache-from = make_cache_from("cpu-ubuntu20.04")
  cache-to = make_cache_to("cpu-ubuntu20.04")
}

target "nvidia-ubuntu20" {
  inherits = ["_nvidia", "_ubuntu20"]
  args = {
    BASE_RUNTIME_IMAGE = "nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04"
  }
  tags = ["${TAG_BASE}:nvidia-ubuntu20.04-${VOICEVOX_ENGINE_VERSION}"]
  cache-from = make_cache_from("nvidia-ubuntu20.04")
  cache-to = make_cache_to("nvidia-ubuntu20.04")
}

target "cpu-ubuntu22" {
  inherits = ["_cpu", "_ubuntu22"]
  tags = [
    "${TAG_BASE}:cpu-ubuntu22.04-${VOICEVOX_ENGINE_VERSION}",
    "${TAG_BASE}:cpu-${VOICEVOX_ENGINE_VERSION}"
  ]
  cache-from = make_cache_from("cpu-ubuntu22.04")
  cache-to = make_cache_to("cpu-ubuntu22.04")
}

target "nvidia-ubuntu22" {
  inherits = ["_nvidia", "_ubuntu22"]
  args = {
    BASE_RUNTIME_IMAGE = "nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04"
  }
  tags = [
    "${TAG_BASE}:nvidia-ubuntu22.04-${VOICEVOX_ENGINE_VERSION}",
    "${TAG_BASE}:nvidia-${VOICEVOX_ENGINE_VERSION}"
  ]
  cache-from = make_cache_from("nvidia-ubuntu22.04")
  cache-to = make_cache_to("nvidia-ubuntu22.04")
}

group "default" {
  targets = ["cpu-ubuntu20", "nvidia-ubuntu20", "cpu-ubuntu22", "nvidia-ubuntu22"]
}
