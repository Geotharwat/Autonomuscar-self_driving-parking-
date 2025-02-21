when you build docker images on RPi you may face 
```
failed to solve: node:alpine: failed to do request: Head "https://registry-1.docker.io/v2/library/node/manifests/alpine": dial tcp: lookup registry-1.docker.io on 192.168.1.1:53: no such host
```

then you add `nameserver 8.8.8.8` to `/etc/resolv.conf` file
by running
```sudo nano /etc/resolv.conf```