# Run in Container
## Installing nvidia-container-toolkit
In order for containers to be able to use your Nvidia GPU, the `nvidia-container-toolkit` package must be installed on the host machine. To install it, you need to import one of two repositories. If you have a deb-based distro, use this repo: `https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list`. If you have an rpm based distro, use this repo: `https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo`.

More info on installing this package: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

### Install examples
#### Ubuntu
```
# Import repo
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
# Install package
sudo apt update && sudo apt install -y nvidia-container-toolkit
```

#### SUSE
```
# Import repo
sudo zypper ar https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo
# Install package
sudo zypper ref && sudo zypper install -y nvidia-container-toolkit
```

## Generate CDI specification
After the `nvidia-container-toolkit` package has been installed, you need to create a CDI specification for the container to get all the info about your GPU.
```
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
```

## Create necessary files
Create the db file and download the env_example file

```
mkdir lemmy-safety
cd lemmy-safety
touch lemmy_safety.db
wget https://raw.githubusercontent.com/db0/lemmy-safety/main/env_example
```

Edit the env_example file that was downloaded and enter the details for your setup. Note that the ssh key path in the env file must match the right side of the volume mount. The left side must match where it is on the host.

## Run the container
Specify which script you want to run and all of the arguments you want to pass it at the end of the line

### All mode, local storage example
Local storage mode requires you to enter the passphrase of your ssh key, which means you must pass the `-it` options and must not pass the `-d` option. After entering your passphrase, you can detach your shell from the container with `Ctrl-P, Ctrl-Q`
```
docker run -it --rm --device nvidia.com/gpu=all --name lemmy-safety -v ./env_example:/app/.env -v ./lemmy_safety.db:/app/lemmy_safety.db -v /path/to/ssh/key/on/host.key:/app/private_key lemmy-safety:latest lemmy_safety_local_storage.py --all
```

### Daemon mode, object storage example:
Object storage mode does not require you to interact with the container, so you can pass the `-d` option.
```
docker run -d --rm --device nvidia.com/gpu=all --name lemmy-safety -v ./env_example:/app/.env -v ./lemmy_safety.db:/app/lemmy_safety.db lemmy-safety:latest lemmy_safety_object_storage.py
```
