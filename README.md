# Magisk Modules Repo
- This repository stores modules for [MRepo](https://github.com/ya0211/MRepo)
- This is not an officially supported Magisk-Modules-Repo

## Upload
1. The `id` here is the id of the module `itself`
2. Just edit `modules.json` once
3. `python3 sync.py` to synchronize

### Upload from updateJson
For modules that already have updateJson

```json
{
  "id": "zygisk_shamiko",
  "update": "https://lsposed.github.io/releases/shamiko.json"
}
```

### Upload from url
For modules with a download link

```json
{
  "id": "zygisk_shamiko",
  "update": "https://github.com/LSPosed/LSPosed.github.io/releases/download/shamiko-120/Shamiko-v0.5.2-120-release.zip"
}
```

### Upload from local
For modules without download links or your own

- Create a new folder named `local` in the same directory as `modules`
- Put the `zip` file into the `local` folder
```json
{
  "id": "zygisk_shamiko",
  "update": "Shamiko-v0.5.2-120-release.zip"
}
```