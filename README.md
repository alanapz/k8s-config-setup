# K8S-CONFIG-SETUP

Utility image to unpack Helm config maps, preserving ownership as well as optional base64 decoding.

Ideal for preserving folder structure (as config maps do not support subkeys).

## To Configure

Create in your config-map an entry called `__CONFIG.yaml`, with a list of `rules`.

For example:

```
__CONFIG.yaml: |-
  rules:
    # As we are stateful set, should overwrite existing file if necessary
    - overwrite: true
    - path: /etc/passwd
      uid: 0
    - pattern: "/etc/nginx.conf/.*"
      mode: 0664
```

Valid parameters are:

| Name    | Type        | Description                                                   |
|---------|-------------|---------------------------------------------------------------|
| path    | String      | If specified, rule applies only to this path (exact match)    |
| pattern | String      | If specified, rule applies only to paths matchis this pattern |
| type    | 'file' or 'dir' | If specified, rule applies only to objects of this type |    
| uid     | Number | chown owner UID to this value                                 |
| gid     | Number | chown owner GID to this value                                 |
| mode | Octal Number | chmod file to this mode |
| overwrite | Boolean | If specified, allow overwriting of existing files |

Default values are:

- UID: 0
- GID: 0
- Mode for new files: 0664
- Mode for new directories: 0775
- Overwrite: False

## To Rebuild

```
./build.sh
```
